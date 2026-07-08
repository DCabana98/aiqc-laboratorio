# ==============================================================
# AIQC – Asistente IA (Google Gemini)
#   · inyecta datos reales de QC, Bio-Rad KB, cobas 8000 y R-4s
#   · responde de forma natural a saludos / preguntas generales
# ==============================================================
import os

import pandas as pd
import streamlit as st
import google.generativeai as genai

from .config import get_section, get_value
from .knowledge_base import NIVELES, COBAS_8000_KB, TEA_CLIA, TEA_DEFAULT, buscar_kb
from .qc_rules import REGLAS_DESC, evaluar_westgard, evaluar_r4s, calcular_sigma


GEMINI_MODELS = [
    "models/gemini-2.5-flash",
    "models/gemini-2.0-flash",
    "models/gemini-2.0-flash-lite",
]

GEMINI_SYSTEM = (
    "Eres AIQC, asistente de Control de Calidad de un laboratorio clínico. "
    "Usas controles Bio-Rad (Liquichek/Lyphochek) y el analizador cobas® 8000 (Roche). "
    "Datos de QC vienen de OpenLab (Agilent) sincronizados automáticamente vía GitHub. "
    "Para preguntas técnicas de QC: usa SOLO los datos del bloque === DATOS REALES ===, NUNCA inventes. "
    "Para alarmas: menciona causas y acciones según Bio-Rad Y manual cobas 8000 si aplica. "
    "R-4s = ERROR ALEATORIO entre niveles — NO recalibrar como primer paso. "
    "Para preguntas no técnicas: responde brevemente y de forma natural, SIN mencionar datos del lab. "
    "Idioma: español. Técnico: Markdown conciso. General: tono cercano. Z-Score: Z=(x-media)/SD."
)

GEMINI_CFG = {"temperature": 0.2, "max_output_tokens": 2048, "top_p": 0.85}


def get_api_key():
    return (
        get_section("gemini").get("api_key")
        or get_value("GEMINI_API_KEY", "")
        or os.environ.get("GEMINI_API_KEY", "")
    )


# ==============================================================
# DETECCIÓN DE CONTEXTO (saludo vs QC)
# ==============================================================
SALUDOS = {
    "hola",
    "buenas",
    "buenos días",
    "buenos dias",
    "buenas tardes",
    "buenas noches",
    "hey",
    "hi",
    "hello",
    "ey",
    "gracias",
    "muchas gracias",
    "de nada",
    "ok",
    "vale",
    "perfecto",
    "genial",
    "entendido",
    "de acuerdo",
    "claro",
    "bien",
    "muy bien",
    "adiós",
    "adios",
    "hasta luego",
    "bye",
    "chao",
    "¿cómo estás?",
    "como estas",
    "¿qué tal?",
    "que tal",
    "¿quién eres?",
    "quien eres",
    "¿qué eres?",
    "que eres",
    "¿qué puedes hacer?",
    "que puedes hacer",
    "ayuda",
    "help",
}

PALABRAS_QC = {
    "analito",
    "control",
    "qc",
    "westgard",
    "alarma",
    "alerta",
    "zscore",
    "z-score",
    "levey",
    "jennings",
    "ewma",
    "cusum",
    "sigma",
    "cv",
    "sd",
    "media",
    "valor",
    "resultado",
    "regla",
    "deriva",
    "tendencia",
    "calibr",
    "reactivo",
    "potasio",
    "sodio",
    "glucosa",
    "alt",
    "ast",
    "creatinina",
    "colesterol",
    "hemoglobina",
    "amilasa",
    "r-4s",
    "r4s",
    "1_3s",
    "2_2s",
    "4_1s",
    "10_x",
    "bio-rad",
    "biorad",
    "lote",
    "nivel",
    "normal",
    "patológico",
    "patologico",
    "informe",
    "pdf",
    "csv",
    "exportar",
    "incidencia",
    "laboratorio",
    "analisis",
    "análisis",
    "muestra",
    "paciente",
    "clinico",
    "clínico",
    "cobas",
    "openlab",
    "ise",
    "fotométrico",
    "fotometrico",
    "pipeta",
    "bandeja",
    "verde",
    "calibracion",
    "calibración",
    "mantenimiento",
    "interlock",
    "electrodo",
    "absorbancia",
    "enzima",
}


def necesita_datos_qc(pregunta):
    texto = pregunta.strip().lower().rstrip(".,!?¿¡ ")
    if texto in SALUDOS:
        return False
    palabras = texto.split()
    if len(palabras) <= 3 and not any(t in texto for t in PALABRAS_QC):
        return False
    if not any(t in texto for t in PALABRAS_QC):
        return False
    return True


MAX_TURNS = 10


# ==============================================================
# RESPUESTA GEMINI
# ==============================================================
def ia_responde_gemini(pregunta, historial, df_all, analitos_ls, f_min, f_max):
    api_key = get_api_key()
    if not api_key:
        return "❌ **API Key de Gemini no configurada.**"
    genai.configure(api_key=api_key)
    niveles_disponibles = sorted(df_all["Nivel"].unique()) if "Nivel" in df_all.columns else ["N"]

    if necesita_datos_qc(pregunta):
        resumen = []
        for an in analitos_ls:
            for niv in niveles_disponibles:
                sub = evaluar_westgard(
                    df_all[
                        (df_all["Analito"] == an)
                        & (df_all["Nivel"] == niv)
                        & (df_all["Fecha"] >= pd.Timestamp(f_min))
                        & (df_all["Fecha"] <= pd.Timestamp(f_max))
                    ].copy()
                )
                if sub.empty:
                    continue
                u = sub.iloc[-1]
                z_calc = (u["Valor"] - u["Media_Objetivo"]) / u["SD_Objetivo"]
                tea = TEA_CLIA.get(an, (TEA_DEFAULT, "", ""))[0]
                sig = calcular_sigma(sub, tea)
                niv_label = NIVELES.get(niv, NIVELES["N"])["label"]
                kb = buscar_kb(an, u["Estado"])
                kb_txt = ""
                if kb and u["Estado"] != "Verde":
                    kb_txt = (
                        f"\n  - Bio-Rad causas: {'; '.join(kb['causas_comunes'][:2])}"
                        f"\n  - Bio-Rad acciones: "
                        f"{'; '.join((kb['acciones_1_3s'] if u['Estado'] == 'Rojo' else kb['acciones_warn'])[:2])}"
                    )
                resumen.append(
                    f"• {an} | Nivel: {niv_label}\n"
                    f"  - Valor:{u['Valor']} Media:{u['Media_Objetivo']} SD:{u['SD_Objetivo']}\n"
                    f"  - Z={z_calc:+.3f} Estado:{u['Estado']} Regla:{u['Regla_Violada']} "
                    f"Score:{int(u['Score_Riesgo'])}/100\n"
                    f"  - Sigma:{sig.get('sigma', 'N/A')}sigma CV:{sig.get('cv_pct', 'N/A')}%{kb_txt}"
                )
        r4s_lines = []
        for an in analitos_ls:
            r4s = evaluar_r4s(df_all, an, f_min, f_max)
            if r4s:
                r4s_lines.append(
                    f"  [R-4s] {an}: {r4s['label_a']} Z={r4s['z_a']:+.2f} vs "
                    f"{r4s['label_b']} Z={r4s['z_b']:+.2f}"
                )
        r4s_sec = ("=== ALARMAS R-4s ===\n" + "\n".join(r4s_lines) + "\n\n") if r4s_lines else ""
        contexto = (
            f"=== DATOS REALES ({f_min} - {f_max}) ===\n{chr(10).join(resumen)}\n\n"
            f"{r4s_sec}=== COBAS 8000 MANUAL ===\n{COBAS_8000_KB}\n\n"
            f"=== REGLAS WESTGARD ===\n{REGLAS_DESC}\n\n=== PREGUNTA ===\n{pregunta}"
        )
    else:
        contexto = f"=== PREGUNTA ===\n{pregunta}"

    recent = historial[1:][-MAX_TURNS * 2 :]
    gemini_hist = [
        {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
        for m in recent
    ]
    last_error = ""
    for model_name in GEMINI_MODELS:
        try:
            m = genai.GenerativeModel(
                model_name=model_name,
                generation_config=GEMINI_CFG,
                system_instruction=GEMINI_SYSTEM,
            )
            chat = m.start_chat(history=gemini_hist)
            resp = chat.send_message(contexto)
            st.session_state["gemini_model_active"] = model_name
            return resp.text
        except Exception as e:
            last_error = str(e)
            if "api_key" in last_error.lower() or "403" in last_error:
                return "❌ API Key inválida."
            continue
    return f"⚠ Modelos no disponibles.\n\n_Error: {last_error}_"
