# ==============================================================
#  AIQC – Artificial Intelligence for Quality Control
#  Versión: 4.8 – Base de conocimiento Bio-Rad (Liquichek + Lyphochek)
#  Deploy:  streamlit run app.py
#  Deps:    pip install streamlit plotly pandas numpy fpdf2 openpyxl google-generativeai kaleido
# ==============================================================

import os, sqlite3
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from fpdf import FPDF
import google.generativeai as genai

st.set_page_config(
    page_title="AIQC – Quality Control",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================
#  ESTILOS GLOBALES
# ==============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"] {
    background-color: #FFFFFF !important; color: #212529;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }
[data-testid="stSidebar"] { background-color: #F8F9FA !important; border-right: 1px solid #DEE2E6; }
[data-testid="stSidebar"] * { color: #212529 !important; }
[data-baseweb="select"] > div, [data-testid="stTextInput"] input, [data-testid="stDateInput"] input {
    background-color: #FFFFFF !important; border: 1px solid #CED4DA !important;
    border-radius: 8px !important; color: #212529 !important;
}
.stButton > button[kind="primary"] {
    background-color: #0066CC !important; border: none !important;
    color: #FFFFFF !important; border-radius: 8px !important; font-weight: 600 !important;
}
.stButton > button[kind="primary"]:hover { background-color: #0052A3 !important; }
.stButton > button[kind="secondary"] {
    background-color: #FFFFFF !important; border: 1.5px solid #0066CC !important;
    color: #0066CC !important; border-radius: 8px !important; font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-list"] { gap: 4px; background: transparent; border-bottom: 2px solid #DEE2E6; }
.stTabs [data-baseweb="tab"] {
    background: transparent !important; border: none !important;
    border-bottom: 3px solid transparent !important; border-radius: 0 !important;
    color: #6C757D !important; font-weight: 500; padding: 10px 20px !important; margin-bottom: -2px;
}
.stTabs [data-baseweb="tab"]:hover { color: #0066CC !important; }
.stTabs [aria-selected="true"] { color: #0066CC !important; border-bottom-color: #0066CC !important; font-weight: 700 !important; background: transparent !important; }
.kpi-card { background: #FFFFFF; border: 1px solid #E9ECEF; border-radius: 12px; padding: 20px 18px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,.06); transition: box-shadow .2s, transform .2s; }
.kpi-card:hover { box-shadow: 0 6px 20px rgba(0,0,0,.10); transform: translateY(-2px); }
.kpi-val { font-size: 1.9rem; font-weight: 700; letter-spacing: -.5px; line-height: 1.15; }
.kpi-lbl { font-size: .73rem; font-weight: 600; color: #6C757D; text-transform: uppercase; letter-spacing: .08em; margin-top: 6px; }
.kpi-sub { font-size: .78rem; color: #ADB5BD; margin-top: 3px; }
.badge { display: inline-flex; align-items: center; gap: 5px; padding: 4px 12px; border-radius: 20px; font-size: .78rem; font-weight: 600; }
.badge-green { background: #D1F7E7; color: #0A6640; border: 1px solid #A3EFD0; }
.badge-amber { background: #FFF3CD; color: #856404; border: 1px solid #FFE082; }
.badge-red   { background: #FCE8E8; color: #9B1C1C; border: 1px solid #F5C6C6; }
.nivel-pill  { display:inline-block; padding:3px 12px; border-radius:20px; font-size:.78rem; font-weight:700; }
.nivel-N  { background:#E8F4FD; color:#0066CC; border:1px solid #B3D1F5; }
.nivel-PB { background:#FFF3CD; color:#856404; border:1px solid #FFE082; }
.nivel-PA { background:#FCE8E8; color:#9B1C1C; border:1px solid #F5C6C6; }
.login-card { background: #FFFFFF; border: 1px solid #DEE2E6; border-radius: 16px; padding: 48px 44px; max-width: 420px; margin: 60px auto 0 auto; box-shadow: 0 8px 32px rgba(0,0,0,.10); }
.sec-head { font-size: 1rem; font-weight: 700; color: #0066CC; border-left: 3px solid #0066CC; padding-left: 10px; margin: 24px 0 14px 0; }
.sb-logo  { text-align:center; font-size:2.6rem; margin-bottom:2px; }
.sb-title { text-align:center; font-size:1.1rem; font-weight:800; color:#0066CC; margin-bottom:4px; }
.sb-sub   { text-align:center; font-size:.78rem; color:#6C757D; margin-bottom:16px; }
.data-pill { background:#EBF3FF; border:1px solid #B3D1F5; border-radius:8px; padding:10px 14px; font-size:.82rem; color:#004A99; margin-top:6px; }
.gemini-banner { background: #EBF3FF; border: 1px solid #B3D1F5; border-radius: 10px; padding: 10px 16px; font-size: 12.5px; color: #004A99; margin-bottom: 14px; }
.biorad-card { background: #F8F9FA; border: 1px solid #DEE2E6; border-radius: 10px; padding: 14px 16px; margin-bottom: 10px; }
.biorad-card-red { background: #FFF5F5; border: 1.5px solid #F5C6C6; border-radius: 10px; padding: 14px 16px; margin-bottom: 10px; }
.biorad-card-amber { background: #FFFBF0; border: 1.5px solid #FFE082; border-radius: 10px; padding: 14px 16px; margin-bottom: 10px; }
table { width:100%; border-collapse:collapse; font-size:.87rem; }
thead tr { background:#F8F9FA; }
th { padding:10px 12px; text-align:left; font-weight:600; color:#495057; border-bottom:2px solid #DEE2E6; }
td { padding:9px 12px; border-bottom:1px solid #F1F3F5; color:#212529; }
tr:hover td { background:#F8F9FA; }
[data-testid="stChatMessage"] { background:#F8F9FA !important; border:1px solid #E9ECEF !important; border-radius:12px !important; }
[data-testid="stMetric"] { background:#FFFFFF; border:1px solid #E9ECEF; border-radius:12px; padding:16px 14px; box-shadow:0 2px 8px rgba(0,0,0,.05); }
</style>
""", unsafe_allow_html=True)


# ==============================================================
#  BASE DE CONOCIMIENTO BIO-RAD
#  Fuentes: Inserts Liquichek / Lyphochek (Bio-Rad), CLSI EP15,
#           guías técnicas QCNet y literatura Westgard Associates.
# ==============================================================
BIORAD_KB = {
    # ── BIOQUÍMICA BÁSICA ─────────────────────────────────────
    "Glucosa": {
        "producto":   "Liquichek Chemistry Control / Lyphochek Chemistry",
        "grupo":      "Bioquímica básica",
        "causas_comunes": [
            "Evaporación del vial de control (apertura prolongada o temperatura elevada)",
            "Degradación glucolítica in vitro si el control no se procesa en ≤2 h tras reconstitución",
            "Interferencia por hemólisis severa (libera glucosa eritrocitaria)",
            "Calibración desactualizada o curva de calibración no lineal en el rango del control",
            "Contaminación cruzada con reactivos de otros analitos en analizadores multicanal",
        ],
        "acciones_1_3s": [
            "🔴 No liberar resultados de pacientes hasta resolver la alarma",
            "Repetir el control con un NUEVO vial del mismo lote",
            "Si persiste: repetir con vial de LOTE DIFERENTE para descartar lote defectuoso",
            "Verificar temperatura de almacenamiento del control (2–8 °C según insert Bio-Rad)",
            "Comprobar fecha de caducidad y tiempo desde reconstitución (máx. 5 días refrigerado)",
            "Recalibrar con estándar trazable IDMS y repetir control",
            "Revisar estado del reactivo (fecha caducidad, turbidez, conservación)",
            "Documentar acción y responsable en el registro de trazabilidad",
        ],
        "acciones_warn": [
            "🟡 Monitoreo estrecho — no bloquear resultados pero aumentar vigilancia",
            "Revisar si hay tendencia en el gráfico Levey-Jennings (¿deriva progresiva?)",
            "Verificar temperatura del baño termostatizado del analizador",
            "Comprobar que el vial se ha mezclado correctamente antes de pipetear",
            "Registrar observación en el libro de incidencias",
        ],
        "causas_deriva": [
            "Deterioro progresivo del reactivo (degradación enzimática de glucosa oxidasa/hexoquinasa)",
            "Deriva del calibrador (recalibrar según protocolo del fabricante del analizador)",
            "Fluctuación de temperatura ambiente del laboratorio",
        ],
        "estabilidad_biorad": "Reconstituido: 5 días a 2-8 °C / 30 días a -20 °C (sin descongelar repetidamente)",
        "interferencias": "Hemólisis (↑), lipemia severa (↓ método GOD-PAP), ácido ascórbico >30 mg/dL (↓)",
        "referencia": "Liquichek Chemistry Control Insert · Bio-Rad cat. 66796 / CLSI EP7-A2",
    },

    "Potasio (K+)": {
        "producto":   "Liquichek Chemistry Control / Liquichek Electrolyte Plus",
        "grupo":      "Bioquímica básica",
        "causas_comunes": [
            "Evaporación del vial (concentra el analito → resultado falsamente elevado)",
            "Contaminación por EDTA (anticoagulante de tubos — eleva K⁺ falsamente)",
            "Hemólisis in vitro del control (libera K⁺ intracelular)",
            "Interferencia del sodio en electrodos ISE por ruptura de membrana selectiva",
            "Temperatura incorrecta del módulo de electrodos ISE",
        ],
        "acciones_1_3s": [
            "🔴 Verificar que el vial de control no lleva abierto más de 8 horas",
            "Repetir con vial nuevo — si el resultado corrige, el problema era el vial",
            "Revisar el electrodo ISE de potasio (limpieza, membrana, solución de referencia)",
            "Comprobar la solución de referencia interna y el buffer de calibración ISE",
            "Recalibrar el módulo ISE con soluciones estándar trazables",
            "Verificar que no hay hemólisis visible en el control reconstituido",
            "Si persiste: contactar soporte técnico del analizador",
        ],
        "acciones_warn": [
            "Verificar tiempo de apertura del vial de control",
            "Comprobar limpieza del electrodo ISE (ciclo de lavado automático)",
            "Revisar temperatura de la celda de medida (37 °C ± 0,5 °C)",
        ],
        "causas_deriva": [
            "Desgaste progresivo de la membrana del electrodo ISE (vida útil: 3-6 meses)",
            "Acumulación de proteínas en el electrodo (limpiar con solución de proteasa)",
            "Deriva del calibrador de 2 puntos ISE",
        ],
        "estabilidad_biorad": "Reconstituido: 8 h a temperatura ambiente / 5 días a 2-8 °C",
        "interferencias": "Hemólisis (↑↑ efecto mayor), EDTA (↑), heparina litio (efecto mínimo)",
        "referencia": "Liquichek Electrolyte Plus Insert · Bio-Rad · CLSI EP9-A3",
    },

    "Sodio": {
        "producto":   "Liquichek Chemistry Control / Liquichek Electrolyte Plus",
        "grupo":      "Bioquímica básica",
        "causas_comunes": [
            "Pseudohiponatremia por lipemia severa en métodos de llama (no afecta ISE indirecto)",
            "Dilución incorrecta del control durante la reconstitución",
            "Electrodo ISE de sodio con membrana deteriorada o contaminada",
            "Contaminación por agua destilada con sodio residual",
        ],
        "acciones_1_3s": [
            "🔴 Repetir control con vial nuevo del mismo lote",
            "Verificar el volumen de reconstitución (agua ultrapura, volumen exacto del insert)",
            "Revisar y limpiar el electrodo ISE de sodio",
            "Recalibrar con solución estándar de NaCl trazable NIST",
            "Comprobar el estado del agua destilada/purificada utilizada",
        ],
        "acciones_warn": [
            "Revisar que el control se ha mezclado por inversión suave (no agitar vigorosamente)",
            "Verificar temperatura de la celda ISE",
            "Comprobar la solución de referencia del electrodo",
        ],
        "causas_deriva": [
            "Envejecimiento de la membrana del electrodo ISE de sodio",
            "Cambio de lote de reactivo sin recalibración",
        ],
        "estabilidad_biorad": "Reconstituido: 8 h a temperatura ambiente / 5 días a 2-8 °C",
        "interferencias": "Lipemia (↓ en métodos fotométricos de llama), hemólisis (efecto mínimo en ISE)",
        "referencia": "Liquichek Electrolyte Plus Insert · Bio-Rad · CLSI EP7-A2",
    },

    "Creatinina": {
        "producto":   "Liquichek Chemistry Control",
        "grupo":      "Bioquímica básica",
        "causas_comunes": [
            "Interferencia por cromógenos de Jaffé (cefalosporinas, acetona, bilirrubina)",
            "Diferencia de método: Jaffé cinético vs enzimático (los valores del insert son por método)",
            "Ictericia severa puede causar falsa elevación en método Jaffé",
            "Calibración trazable a IDMS requerida — calibradores no trazables generan sesgo",
        ],
        "acciones_1_3s": [
            "🔴 Confirmar que el insert Bio-Rad tiene valores asignados para TU método/instrumento",
            "Cambiar a método enzimático si hay interferencia por bilirrubina o fármacos",
            "Recalibrar con calibrador trazable a IDMS (NIST SRM 967)",
            "Repetir control con vial nuevo",
            "Verificar si el paciente (o el control) tiene niveles de cefalosporinas que interfieran",
        ],
        "acciones_warn": [
            "Verificar el método utilizado (Jaffé vs enzimático) y usar valores correctos del insert",
            "Revisar fecha de caducidad del reactivo Jaffé (ácido pícrico se degrada)",
        ],
        "causas_deriva": [
            "Degradación del ácido pícrico en método Jaffé (reactivo muy sensible a luz y calor)",
            "Deriva del calibrador entre lotes",
        ],
        "estabilidad_biorad": "Reconstituido: 5 días a 2-8 °C",
        "interferencias": "Bilirrubina >10 mg/dL (↑ Jaffé), cefalosporinas (↑ Jaffé), acetona (↑ Jaffé), hemólisis (↑ leve)",
        "referencia": "Liquichek Chemistry Control Insert · Bio-Rad · CLSI EP6-A",
    },

    # ── ENZIMAS ───────────────────────────────────────────────
    "ALT (Transaminasa)": {
        "producto":   "Liquichek Chemistry Control / Lyphochek Chemistry",
        "grupo":      "Enzimas hepáticas",
        "causas_comunes": [
            "Temperatura de incubación incorrecta (las enzimas son muy sensibles a T°)",
            "Degradación enzimática del control por exceso de ciclos de congelación/descongelación",
            "Longitud de onda del fotómetro fuera de tolerancia (340 nm para métodos NADH)",
            "Interferencia por hemólisis (ALT eritrocitaria libera actividad)",
            "Reactivo de piridoxal fosfato (P-5-P) faltante o degradado",
        ],
        "acciones_1_3s": [
            "🔴 Verificar temperatura del baño termostatizado (37,0 °C ± 0,1 °C)",
            "Repetir con vial nuevo — la actividad enzimática es sensible al manejo",
            "Comprobar que el reactivo contiene piridoxal fosfato (P-5-P) activado",
            "Verificar longitud de onda del espectrofotómetro con filtro de referencia",
            "Revisar el tiempo de lag phase (preincubación) configurado en el analizador",
            "Si el control de ALT falla junto con AST: sospechar problema de temperatura o reactivo",
            "Recalibrar si no se ha realizado en las últimas 24 h",
        ],
        "acciones_warn": [
            "Comprobar temperatura del módulo fotométrico",
            "Verificar mezcla correcta del vial de control antes de pipetear",
            "Revisar si hay burbujas en la cubeta de reacción",
            "Controlar la absorbancia del blanco de reactivo (no debe superar 1.5 AU)",
        ],
        "causas_deriva": [
            "Deterioro progresivo del coenzima NADH en el reactivo (sensible a luz UV)",
            "Fluctuación de temperatura del laboratorio que afecta al módulo termostatizado",
            "Cambio de lote de reactivo sin ajuste de valores objetivo",
        ],
        "estabilidad_biorad": "Reconstituido: 5 días a 2-8 °C (la actividad enzimática decrece con el tiempo)",
        "interferencias": "Hemólisis severa (↑), lipemia >500 mg/dL (↑ o ↓ según método), bilirrubina >20 mg/dL (↑ leve)",
        "referencia": "Liquichek Chemistry Control Insert · Bio-Rad · IFCC EP9 / CLSI EP15-A3",
    },

    "AST": {
        "producto":   "Liquichek Chemistry Control / Lyphochek Chemistry",
        "grupo":      "Enzimas hepáticas",
        "causas_comunes": [
            "Hemólisis in vitro del control (AST eritrocitaria es 15× mayor que en plasma)",
            "Temperatura incorrecta (37 °C es crítica — cada grado cambia la actividad ~7%)",
            "Piridoxal fosfato ausente o degradado en el reactivo",
            "Interferencia con el malato deshidrogenasa (MDH) por oxalacetato espontáneo",
        ],
        "acciones_1_3s": [
            "🔴 Inspeccionar visualmente el vial de control — ¿hay hemólisis visible (color rosado)?",
            "Repetir con vial nuevo sin hemólisis",
            "Verificar temperatura del baño (37,0 °C ± 0,1 °C)",
            "Comprobar activación con P-5-P del reactivo",
            "Recalibrar si ALT también falla simultáneamente",
        ],
        "acciones_warn": [
            "Revisar manejo del vial (no agitar — mezclar por inversión suave)",
            "Verificar la absorbancia inicial del blanco de reactivo",
            "Comprobar fecha de caducidad del reactivo R2 (con MDH)",
        ],
        "causas_deriva": [
            "Degradación del NADH del reactivo por exposición a luz",
            "Acumulación de oxalacetato espontáneo en el reactivo R2 abierto",
        ],
        "estabilidad_biorad": "Reconstituido: 5 días a 2-8 °C",
        "interferencias": "Hemólisis (↑↑↑ efecto más marcado que en ALT), lipemia moderada (↑ leve)",
        "referencia": "Liquichek Chemistry Control Insert · Bio-Rad · IFCC / CLSI EP7-A2",
    },

    "GGT": {
        "producto":   "Liquichek Chemistry Control",
        "grupo":      "Enzimas hepáticas",
        "causas_comunes": [
            "Temperatura de reacción incorrecta (sensible a variaciones de ±0,5 °C)",
            "pH del reactivo fuera de rango (óptimo 7,9–8,2 para GGT)",
            "Evaporación del substrato (L-gamma-glutamil-p-nitroanilida) por mal sellado",
        ],
        "acciones_1_3s": [
            "🔴 Verificar temperatura del módulo fotométrico",
            "Comprobar pH del tampón del reactivo si es posible",
            "Repetir con vial nuevo y reactivo recién preparado",
            "Recalibrar con calibrador trazable",
        ],
        "acciones_warn": [
            "Revisar fecha de preparación del reactivo (vida en uso según fabricante del analizador)",
            "Verificar ausencia de precipitados en el reactivo",
        ],
        "causas_deriva": [
            "Hidrólisis espontánea del substrato en el reactivo abierto",
            "Fluctuación de pH por exposición al CO₂ ambiental",
        ],
        "estabilidad_biorad": "Reconstituido: 5 días a 2-8 °C",
        "interferencias": "Hemólisis leve (efecto mínimo), lipemia >1000 mg/dL (↑)",
        "referencia": "Liquichek Chemistry Control Insert · Bio-Rad · ECCLS / DGKC",
    },

    "LDH": {
        "producto":   "Liquichek Chemistry Control / Lyphochek Chemistry",
        "grupo":      "Enzimas hepáticas",
        "causas_comunes": [
            "Hemólisis (la LDH eritrocitaria es 160× mayor que en plasma — efecto enorme)",
            "Isoenzimas de LDH: el control tiene perfil de isoenzimas fijo (LDH1-5 definido en insert)",
            "Temperatura crítica: cada °C modifica la actividad ~8–10%",
            "Inhibición por exceso de piruvato (en método inverso piruvato→lactato)",
        ],
        "acciones_1_3s": [
            "🔴 Inspeccionar el vial — la hemólisis es la causa más frecuente de falsa elevación",
            "Repetir con vial nuevo sin hemólisis (aspecto transparente/ligeramente amarillo)",
            "Verificar temperatura del módulo (37,0 °C)",
            "Comprobar dirección de la reacción configurada (L→P o P→L) coincide con el reactivo",
        ],
        "acciones_warn": [
            "Verificar que el reactivo no tiene precipitados (NADH precipita en frío)",
            "Atemperar el reactivo a temperatura ambiente antes de su uso",
        ],
        "causas_deriva": [
            "Degradación del NADH por congelación repetida del reactivo",
            "Cambio de isoenzimas en el control por lote diferente",
        ],
        "estabilidad_biorad": "Reconstituido: 24 h a 2-8 °C (muy lábil — usar el mismo día)",
        "interferencias": "Hemólisis (↑↑↑ crítico), oxalato (↓), urea elevada (↓ leve)",
        "referencia": "Liquichek Chemistry Control Insert · Bio-Rad · IFCC/DGKC",
    },

    # ── LÍPIDOS ───────────────────────────────────────────────
    "Colesterol": {
        "producto":   "Liquichek Lipid Control / Lyphochek Lipid",
        "grupo":      "Lípidos",
        "causas_comunes": [
            "Diferencia de método: método enzimático CHOD-PAP vs método de Abell-Kendall (referencia)",
            "Interferencia por bilirrubina >5 mg/dL (inhibe la peroxidasa en CHOD-PAP)",
            "Efecto matriz del control (suero humano vs suero animal con lipoproteinasen distintas)",
            "Calibrador no trazable a NIST SRM 1951c (material de referencia para colesterol)",
        ],
        "acciones_1_3s": [
            "🔴 Verificar que los valores objetivo del insert corresponden a TU método/instrumento",
            "Repetir con vial nuevo del mismo lote",
            "Recalibrar con calibrador trazable a NIST SRM 1951c",
            "Revisar el reactivo de colesterol (CHOD-PAP) — verificar absorbancias del blanco",
            "Comprobar la temperatura de incubación (37 °C, 5–10 min según fabricante)",
        ],
        "acciones_warn": [
            "Verificar la mezcla del vial (colesterol puede precipitar — mezclar por inversión suave)",
            "Revisar si hay interferencia por bilirrubina en muestras de ese día",
            "Confirmar que el blanco de reactivo está dentro del rango de linealidad del fotómetro",
        ],
        "causas_deriva": [
            "Degradación de la colesterol oxidasa (CHOD) en el reactivo por temperatura o luz",
            "Cambio de lote de reactivo con diferente lote de enzima",
        ],
        "estabilidad_biorad": "Reconstituido: 7 días a 2-8 °C / estable a -20 °C hasta caducidad",
        "interferencias": "Bilirrubina >5 mg/dL (↓ CHOD-PAP), hemólisis severa (↑ leve), ácido ascórbico (↓)",
        "referencia": "Liquichek Lipid Control Insert · Bio-Rad · CDC/NHLBI Lipid Standardization Program",
    },

    "Triglicéridos": {
        "producto":   "Liquichek Lipid Control / Lyphochek Lipid",
        "grupo":      "Lípidos",
        "causas_comunes": [
            "Glicerol endógeno libre en el control (algunos inserts incluyen corrección por glicerol)",
            "Interferencia por hemólisis (la hemoglobina inhibe la peroxidasa)",
            "Falta de ayuno simulado en el control (el control es postprandial por diseño)",
        ],
        "acciones_1_3s": [
            "🔴 Verificar si el insert Bio-Rad especifica valores con o sin corrección por glicerol libre",
            "Repetir control con vial nuevo",
            "Recalibrar con calibrador trazable a NIST SRM 1951c",
            "Comprobar el estado del reactivo GPO-PAP (lipasa, glicerol quinasa, GPO, peroxidasa)",
        ],
        "acciones_warn": [
            "Verificar que el control se ha atemperado correctamente (no pipetear en frío)",
            "Revisar el tiempo de incubación del reactivo",
        ],
        "causas_deriva": [
            "Degradación de la lipasa pancreática en el reactivo",
            "Acumulación de glicerol libre en el vial de control abierto",
        ],
        "estabilidad_biorad": "Reconstituido: 7 días a 2-8 °C",
        "interferencias": "Hemólisis (↓ peroxidasa), glicerol libre endógeno (↑), bilirrubina >5 mg/dL (↓)",
        "referencia": "Liquichek Lipid Control Insert · Bio-Rad",
    },

    "HDL-Colesterol": {
        "producto":   "Liquichek Lipid Control",
        "grupo":      "Lípidos",
        "causas_comunes": [
            "Efecto matriz del control en métodos de precipitación directa (distintas lipoproteínas)",
            "Interferencia de VLDL elevadas con los métodos de HDL directo homogéneo",
            "Calibración incorrecta del método homogéneo directo (muy sensible a calibrador)",
        ],
        "acciones_1_3s": [
            "🔴 Verificar los valores del insert Bio-Rad para TU método específico de HDL (directo/precipitación)",
            "Repetir con vial nuevo",
            "Recalibrar — los métodos de HDL directo requieren calibración frecuente",
            "Revisar si hay hipertrigliceridemia en muestras del día (interfiere en HDL directo)",
        ],
        "acciones_warn": [
            "Confirmar que el tipo de método en el analizador coincide con los valores del insert",
            "Verificar la integridad del blanco de HDL",
        ],
        "causas_deriva": [
            "Cambio de lote de reactivo sin recalibración (los reactivos de HDL directo son sensibles)",
        ],
        "estabilidad_biorad": "Reconstituido: 7 días a 2-8 °C",
        "interferencias": "Triglicéridos >400 mg/dL (↑ falso en directo), bilirrubina >10 mg/dL (↑)",
        "referencia": "Liquichek Lipid Control Insert · Bio-Rad · CDC Lipid Standardization",
    },

    # ── INMUNOENSAYO / HORMONAL ───────────────────────────────
    "TSH": {
        "producto":   "Lyphochek Immunoassay Plus Control",
        "grupo":      "Inmunoensayo hormonal",
        "causas_comunes": [
            "Anticuerpos heterófilos en el control (HAMA — anti-ratón) que interfieren en ensayos sandwich",
            "Efecto gancho (hook effect) en niveles muy elevados de TSH (raro en controles normales)",
            "Degradación de la hormona por ciclos de congelación/descongelación inadecuados",
            "Variabilidad inter-ensayo elevada en plataformas de inmunoensayo (CV% típico 5-8%)",
            "Reactividad cruzada con anticuerpos contra otras glicoproteínas (LH, FSH)",
        ],
        "acciones_1_3s": [
            "🔴 Verificar que el control Lyphochek está específicamente asignado a TU plataforma de inmunoensayo",
            "Repetir con vial nuevo — los controles de inmunoensayo son más variables que los de bioquímica",
            "Revisar el número de ciclos de congelación/descongelación del vial (máx. 3 según insert)",
            "Comprobar la fecha de caducidad y condiciones de almacenamiento (-20 °C sin defrostar)",
            "Verificar calibración del inmunoensayo (los kits se calibran en lote)",
            "Si persiste: ejecutar control de calidad interno del analizador (IQC procedural check)",
        ],
        "acciones_warn": [
            "Revisar el número de lote del reactivo vs la calibración activa",
            "Verificar que el cartucho/reactivo de TSH no está próximo a caducidad",
            "Comprobar los volúmenes de muestra (pipeteo automático — verificar con agua destilada)",
        ],
        "causas_deriva": [
            "Cambio de lote de reactivo con diferente calibración (recalibrar obligatoriamente)",
            "Degradación gradual del conjugado enzimático del inmunoensayo",
            "Fluctuación de temperatura del módulo de incubación del analizador",
        ],
        "estabilidad_biorad": "Liofilizado: según caducidad etiqueta / Reconstituido: 30 días a 2-8 °C (Lyphochek)",
        "interferencias": "HAMA (↑↑), biotina >20 ng/mL en paciente (↓ ensayos tipo streptavidina), hemólisis severa (variable)",
        "referencia": "Lyphochek Immunoassay Plus Control Insert · Bio-Rad · CLSI EP15-A3",
    },

    "T4 Libre (FT4)": {
        "producto":   "Lyphochek Immunoassay Plus Control",
        "grupo":      "Inmunoensayo hormonal",
        "causas_comunes": [
            "Interferencia por proteínas de unión (TBG, albúmina) que varían entre el control y pacientes",
            "Dilución incorrecta del control liofilizado (agua ultrapura, volumen exacto)",
            "Variabilidad entre plataformas de FT4 (los valores son método-dependientes)",
            "Efecto de biotina en ensayos que usan estreptavidina",
        ],
        "acciones_1_3s": [
            "🔴 Confirmar que los valores objetivo del insert son específicos para TU analizador",
            "Repetir con vial nuevo reconstituido correctamente (agua ultrapura, temperatura ambiente)",
            "Recalibrar el inmunoensayo de FT4",
            "Verificar integridad del reactivo (aspecto, color, precipitados)",
        ],
        "acciones_warn": [
            "Comprobar el volumen de reconstitución exacto según el insert Lyphochek",
            "Verificar que el control se ha mezclado por inversión suave (no vortex)",
        ],
        "causas_deriva": [
            "Cambio de lote de reactivo (FT4 es muy sensible a variaciones de calibración entre lotes)",
            "Degradación de la hormona por temperatura de almacenamiento inadecuada",
        ],
        "estabilidad_biorad": "Reconstituido: 30 días a 2-8 °C (Lyphochek)",
        "interferencias": "Biotina >20 ng/mL (↓), HAMA (variable), heparina IV (↑ artefactual in vitro)",
        "referencia": "Lyphochek Immunoassay Plus Control Insert · Bio-Rad",
    },

    "Hemoglobina": {
        "producto":   "Lyphochek Hematology / Liquichek Hematology",
        "grupo":      "Hematología",
        "causas_comunes": [
            "Envejecimiento del control de hematología (los eritrocitos se fragmentan con el tiempo)",
            "Temperatura de almacenamiento incorrecta (los controles de hematología son muy sensibles a T°)",
            "Variabilidad entre analizadores de hematología (parámetros no armonizados globalmente)",
            "Calibración del analizador desactualizada (recalibrar según protocolo del fabricante)",
        ],
        "acciones_1_3s": [
            "🔴 Verificar la fecha de caducidad DEL VIAL ABIERTO (típicamente 5-7 días según insert Bio-Rad)",
            "Repetir con vial nuevo dentro de fecha",
            "Ejecutar el ciclo de QC interno del analizador (autoverificación del hardware)",
            "Recalibrar con material de referencia del fabricante del analizador (no con Lyphochek)",
            "Si el fallo afecta a múltiples parámetros: sospechar problema del analizador (óptica, hidráulica)",
        ],
        "acciones_warn": [
            "Verificar temperatura de almacenamiento del control (2-8 °C, NO congelar)",
            "Comprobar que el control se ha invertido suavemente 8-10 veces antes de analizar",
            "Revisar el tiempo de estabilización del control tras sacar de nevera (15 min a T° ambiente)",
        ],
        "causas_deriva": [
            "Fragmentación progresiva de eritrocitos en el control envejecido",
            "Variación de la calibración del canal de hemoglobina (HGB) por suciedad en la cubeta",
        ],
        "estabilidad_biorad": "Abierto: 5-7 días a 2-8 °C / No congelar / Descartar si hay hemólisis visible",
        "interferencias": "Lipemia severa (↑ HGB fotométrico), crioglobulinas (↑ leucocitos falso), ictericia severa (↑ HGB)",
        "referencia": "Lyphochek Hematology Control Insert · Bio-Rad · CLSI H26-A2",
    },

    "Calcio": {
        "producto":   "Liquichek Chemistry Control",
        "grupo":      "Bioquímica básica",
        "causas_comunes": [
            "Interferencia por EDTA (quelante del calcio — tubos morados son incompatibles)",
            "pH del control fuera de rango (el calcio iónico varía con el pH)",
            "Interferencia por magnesio elevado en método de o-cresolftaleína",
            "Evaporación del vial (concentra el calcio)",
        ],
        "acciones_1_3s": [
            "🔴 Descartar contaminación con EDTA (tubos morados o capilares EDTA)",
            "Repetir con vial nuevo",
            "Verificar el pH del reactivo de o-cresolftaleína (sensible al pH)",
            "Recalibrar con calibrador trazable a SRM NIST 956c",
            "Comprobar el blanco de reactivo (la o-cresolftaleína cambia de color con el pH ambiental)",
        ],
        "acciones_warn": [
            "Verificar tiempo de apertura del vial de control",
            "Comprobar temperatura de incubación (37 °C)",
        ],
        "causas_deriva": [
            "Degradación del indicador o-cresolftaleína por pH o temperatura",
            "Cambio de lote de reactivo con diferente concentración de indicador",
        ],
        "estabilidad_biorad": "Reconstituido: 5 días a 2-8 °C",
        "interferencias": "EDTA (↓↓↓ crítico), magnesio elevado (↑ leve en o-cresolftaleína), hemólisis (↑ leve)",
        "referencia": "Liquichek Chemistry Control Insert · Bio-Rad · CLSI EP7-A2",
    },
}

# Grupos de analitos para búsqueda por similitud
GRUPOS_ANALITICOS = {
    "Bioquímica básica": ["Glucosa", "Potasio (K+)", "Sodio", "Creatinina", "Calcio"],
    "Enzimas hepáticas": ["ALT (Transaminasa)", "AST", "GGT", "LDH"],
    "Lípidos":           ["Colesterol", "Triglicéridos", "HDL-Colesterol"],
    "Inmunoensayo hormonal": ["TSH", "T4 Libre (FT4)"],
    "Hematología":       ["Hemoglobina"],
}

def buscar_kb(analito: str, estado: str) -> dict | None:
    """Busca en la KB por nombre exacto o por similitud parcial."""
    if analito in BIORAD_KB:
        return BIORAD_KB[analito]
    # Búsqueda parcial (ej: "ALT" → "ALT (Transaminasa)")
    an_norm = analito.lower()
    for key in BIORAD_KB:
        if an_norm in key.lower() or key.lower() in an_norm:
            return BIORAD_KB[key]
    return None

def render_kb_panel(analito: str, estado: str, regla: str, nivel: str):
    """Renderiza el panel de conocimiento Bio-Rad para un analito con alarma."""
    kb = buscar_kb(analito, estado)
    nivel_label = NIVELES.get(nivel, NIVELES["N"])["label"]
    card_class  = "biorad-card-red" if estado == "Rojo" else "biorad-card-amber" if estado == "Ámbar" else "biorad-card"

    if kb is None:
        st.markdown(
            f'<div class="{card_class}">'
            f'<b>📋 Bio-Rad KB:</b> No hay ficha específica para <b>{analito}</b> en la base de conocimiento. '
            f'Consulta el insert de tu lote en <a href="https://myeinserts-app.qcnet.com/home" target="_blank">myeInserts QCNet</a>.'
            f'</div>', unsafe_allow_html=True)
        return

    ico = "🔴" if estado == "Rojo" else "🟡"
    st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
    st.markdown(
        f"#### {ico} Guía Bio-Rad — **{analito}** · {nivel_label} · Regla `{regla}`\n"
        f"*Producto: {kb['producto']} · Grupo: {kb['grupo']}*")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🔍 Causas más probables:**")
        for c in kb["causas_comunes"]:
            st.markdown(f"- {c}")

        if estado == "Ámbar" and ("10_x" in regla or "4_1s" in regla or "2_2s" in regla):
            st.markdown("**📉 Causas de deriva/tendencia:**")
            for c in kb.get("causas_deriva", []):
                st.markdown(f"- {c}")

    with col2:
        acciones = kb["acciones_1_3s"] if estado == "Rojo" else kb["acciones_warn"]
        st.markdown("**✅ Acciones correctivas:**")
        for a in acciones:
            st.markdown(f"- {a}")

    st.markdown(
        f"**⚠️ Interferencias conocidas:** {kb['interferencias']}\n\n"
        f"**🧪 Estabilidad Bio-Rad:** {kb['estabilidad_biorad']}\n\n"
        f"**📖 Referencia:** {kb['referencia']}"
    )
    st.markdown(
        f'<small>🔗 Consulta el insert de tu lote específico: '
        f'<a href="https://myeinserts-app.qcnet.com/home" target="_blank">myeInserts QCNet Bio-Rad</a></small>',
        unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================
#  CONSTANTES DE NIVELES
# ==============================================================
NIVELES = {
    "N":  {"label": "Normal",          "pill": "nivel-N",  "icon": "🔵"},
    "PB": {"label": "Patológico Bajo",  "pill": "nivel-PB", "icon": "🟡"},
    "PA": {"label": "Patológico Alto",  "pill": "nivel-PA", "icon": "🔴"},
}

def nivel_badge(codigo: str) -> str:
    cfg = NIVELES.get(codigo, NIVELES["N"])
    return f'<span class="nivel-pill {cfg["pill"]}">{cfg["icon"]} {cfg["label"]}</span>'


# ==============================================================
#  1. GOOGLE GEMINI
# ==============================================================
GEMINI_MODELS = ["models/gemini-2.5-flash","models/gemini-2.0-flash","models/gemini-2.0-flash-lite"]
GEMINI_SYSTEM = (
    "Eres AIQC, el sistema automatizado de Control de Calidad de un laboratorio clínico. "
    "Usas controles Bio-Rad (Liquichek y Lyphochek). "
    "REGLA ABSOLUTA: Cada respuesta DEBE incluir los valores numéricos reales del laboratorio "
    "(valor medido, media, SD, Z-Score, estado, regla violada, nivel de control). "
    "Cuando hay una alarma, menciona las causas probables según el insert Bio-Rad y las acciones correctivas. "
    "NUNCA respondas de forma genérica. Respondes en español, de forma concisa y técnica. "
    "Usas Markdown para mayor claridad. Fórmula Z-Score: Z = (x − μ) / σ."
)
GEMINI_CFG = {"temperature": 0.2, "max_output_tokens": 2048, "top_p": 0.85}

def get_api_key() -> str:
    return (
        st.secrets.get("gemini", {}).get("api_key") or
        st.secrets.get("GEMINI_API_KEY", "") or
        os.environ.get("GEMINI_API_KEY", "")
    )


# ==============================================================
#  2. AUTENTICACIÓN
# ==============================================================
def get_credentials() -> tuple[str, str]:
    try:
        return st.secrets["auth"]["user"], st.secrets["auth"]["password"]
    except KeyError:
        st.error("⚠️ Crea `.streamlit/secrets.toml` con [auth] user y password."); st.stop()

VALID_USER, VALID_PASS = get_credentials()

def render_login():
    st.markdown("""<div class="login-card">
        <div style="font-size:3rem;text-align:center">🔬</div>
        <div style="text-align:center;font-size:1.8rem;font-weight:800;color:#0066CC">AIQC</div>
        <div style="text-align:center;font-size:.86rem;color:#6C757D;margin-bottom:28px">
            Artificial Intelligence for Quality Control · v4.8
        </div></div>""", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.8, 1])
    with mid:
        st.markdown("<br>", unsafe_allow_html=True)
        user = st.text_input("Usuario", placeholder="admin", key="_u")
        pwd  = st.text_input("Contraseña", type="password", placeholder="••••••", key="_p")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Acceder al sistema →", use_container_width=True, type="primary"):
            if user == VALID_USER and pwd == VALID_PASS:
                st.session_state["auth"] = True; st.rerun()
            else:
                st.error("Credenciales incorrectas.")

if not st.session_state.get("auth"):
    render_login(); st.stop()


# ==============================================================
#  3. SQLITE
# ==============================================================
DB_PATH = "aiqc_acciones.db"

def init_db():
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.execute("CREATE TABLE IF NOT EXISTS acciones (clave TEXT PRIMARY KEY, hecha INTEGER DEFAULT 0, ts TEXT)")
    con.commit(); return con

def load_acciones(con): return {r[0]: bool(r[1]) for r in con.execute("SELECT clave,hecha FROM acciones").fetchall()}
def save_accion(con, clave, hecha):
    con.execute("INSERT OR REPLACE INTO acciones VALUES (?,?,datetime('now'))", (clave, int(hecha))); con.commit()

if "db_con" not in st.session_state:
    st.session_state["db_con"] = init_db()
db_con = st.session_state["db_con"]


# ==============================================================
#  4. DATOS DEMO
# ==============================================================
NIVELES_DEMO = {
    "Potasio (K+)":       {"N":(4.5,0.15),"PB":(2.8,0.12),"PA":(6.2,0.18)},
    "ALT (Transaminasa)": {"N":(35.0,2.5),"PB":(12.0,1.5),"PA":(120.0,8.0)},
}

@st.cache_data(show_spinner=False)
def build_demo(ref_date: str = "") -> pd.DataFrame:
    np.random.seed(2026)
    today = pd.Timestamp(ref_date).replace(hour=0, minute=0, second=0, microsecond=0)
    dates = [today - timedelta(days=29-i) for i in range(30)]
    rows  = []
    for analito, niveles in NIVELES_DEMO.items():
        for nivel_cod, (media, sd) in niveles.items():
            for i, d in enumerate(dates):
                drift = 2.5*(i-24)*0.65 if analito=="ALT (Transaminasa)" and nivel_cod=="PA" and i>=25 else 0.0
                rows.append({"Fecha":d,"Analito":analito,"Nivel":nivel_cod,
                              "Valor":round(np.random.normal(media+drift,sd*0.85),3),
                              "Media_Objetivo":media,"SD_Objetivo":sd,"Lote":f"LOT-{2026+i//10}"})
    return pd.DataFrame(rows)


# ==============================================================
#  5. CARGA CSV/XLSX
# ==============================================================
COL_SYNONYMS = {
    "Fecha":["fecha","date","dia","timestamp","time","datetime"],
    "Analito":["analito","analyte","test","prueba","parametro","magnitud"],
    "Nivel":["nivel","level","control_level","qc_level","tipo_control"],
    "Valor":["valor","value","resultado","result","medicion","concentracion"],
    "Media_Objetivo":["media_objetivo","media","mean","target","objetivo","xbar"],
    "SD_Objetivo":["sd_objetivo","sd","desviacion","std","sigma","desvest"],
    "Lote":["lote","lot","batch","lote_reactivo","reactivo"],
}

def _norm(s):
    return s.lower().strip().translate(str.maketrans("áéíóúàèìòùäëïöüÁÉÍÓÚ","aeiouaeiouaeiouAEIOU"))

def normalizar_df(df):
    df_n = {_norm(c): c for c in df.columns}
    rename = {}
    for interno, sins in COL_SYNONYMS.items():
        for s in sins:
            if s in df_n: rename[df_n[s]] = interno; break
        if interno not in rename.values():
            for cn, co in df_n.items():
                if any(s in cn or cn in s for s in sins): rename[co] = interno; break
    df2 = df.rename(columns=rename)
    obligatorias = ["Fecha","Analito","Valor","Media_Objetivo","SD_Objetivo"]
    faltan = [c for c in obligatorias if c not in df2.columns]
    if faltan: return None, f"Columnas no encontradas: {', '.join(faltan)}."
    if "Nivel" not in df2.columns: df2["Nivel"] = "N"
    if "Lote"  not in df2.columns: df2["Lote"]  = "N/A"
    df2["Fecha"]          = pd.to_datetime(df2["Fecha"], dayfirst=True, errors="coerce")
    df2["Valor"]          = pd.to_numeric(df2["Valor"],         errors="coerce")
    df2["Media_Objetivo"] = pd.to_numeric(df2["Media_Objetivo"], errors="coerce")
    df2["SD_Objetivo"]    = pd.to_numeric(df2["SD_Objetivo"],    errors="coerce")
    nivel_map = {
        "n":"N","normal":"N","nivel 1":"N","nivel1":"N","n1":"N","1":"N",
        "pb":"PB","patologico bajo":"PB","bajo":"PB","nivel 2":"PB","n2":"PB","2":"PB",
        "pa":"PA","patologico alto":"PA","alto":"PA","nivel 3":"PA","n3":"PA","3":"PA",
    }
    df2["Nivel"] = df2["Nivel"].astype(str).str.lower().str.strip().map(lambda x: nivel_map.get(x,"N"))
    df2 = df2.dropna(subset=obligatorias)
    if df2.empty: return None, "Sin filas válidas."
    return df2[obligatorias+["Nivel","Lote"]].reset_index(drop=True), ""

def leer_archivo(uploaded):
    name = uploaded.name.lower()
    try:
        raw = pd.read_csv(uploaded, sep=None, engine="python") if name.endswith(".csv") else pd.read_excel(uploaded)
        return normalizar_df(raw)
    except Exception as e:
        return None, f"Error: {e}"


# ==============================================================
#  6. WESTGARD
# ==============================================================
REGLAS_DESC = "1_3s: ±3SD → Rojo | 2_2s: 2 consec ±2SD → Rojo | 4_1s: 4 consec ±1SD → Ámbar | 10_x: 10 consec mismo lado → Ámbar"

def evaluar_westgard(serie):
    df = serie.copy().sort_values("Fecha").reset_index(drop=True)
    df["Z_Score"] = (df["Valor"]-df["Media_Objetivo"])/df["SD_Objetivo"]
    df["Regla_Violada"]="—"; df["Score_Riesgo"]=0; df["Estado"]="Verde"
    for i in range(len(df)):
        z = df.at[i,"Z_Score"]
        if abs(z)>=3.0: df.at[i,"Regla_Violada"]="1_3s"; df.at[i,"Score_Riesgo"]=90; df.at[i,"Estado"]="Rojo"; continue
        if i>=1:
            zp=df.at[i-1,"Z_Score"]
            if abs(z)>=2.0 and abs(zp)>=2.0 and np.sign(z)==np.sign(zp):
                df.at[i,"Regla_Violada"]="2_2s"; df.at[i,"Score_Riesgo"]=75; df.at[i,"Estado"]="Rojo"; continue
        if i>=3:
            w4=df.loc[i-3:i,"Z_Score"].values
            if all(abs(x)>=1.0 for x in w4) and len(set(np.sign(w4)))==1:
                df.at[i,"Regla_Violada"]="4_1s"; df.at[i,"Score_Riesgo"]=60; df.at[i,"Estado"]="Ámbar"; continue
        if i>=9:
            w10=df.loc[i-9:i,"Z_Score"].values; signos=set(np.sign(w10))
            if len(signos)==1 and 0.0 not in signos:
                df.at[i,"Regla_Violada"]="10_x"; df.at[i,"Score_Riesgo"]=55; df.at[i,"Estado"]="Ámbar"; continue
        if abs(z)>=2.0: df.at[i,"Regla_Violada"]="1_2s (warn)"; df.at[i,"Score_Riesgo"]=45; df.at[i,"Estado"]="Ámbar"; continue
        df.at[i,"Score_Riesgo"]=max(0,int(abs(z)*18))
    return df

def estado_badge(e):
    cfg={"Verde":("badge-green","●"),"Ámbar":("badge-amber","▲"),"Rojo":("badge-red","■")}
    cls,ico=cfg.get(e,("badge-green","●"))
    return f'<span class="badge {cls}">{ico} {e}</span>'


# ==============================================================
#  7. SIGMA METRICS
# ==============================================================
TEA_CLIA = {
    "Potasio (K+)":(8.0,"mmol/L","CLIA"),"ALT (Transaminasa)":(20.0,"U/L","CLIA"),
    "Glucosa":(10.0,"mg/dL","CLIA"),"Sodio":(4.0,"mmol/L","CLIA"),
    "Creatinina":(15.0,"mg/dL","CLIA"),"Colesterol":(10.0,"mg/dL","CLIA"),
    "Hemoglobina":(7.0,"g/dL","CLIA"),"Calcio":(8.0,"mg/dL","CLIA"),
    "Triglicéridos":(25.0,"mg/dL","CLIA"),"HDL-Colesterol":(30.0,"mg/dL","CLIA"),
    "TSH":(25.0,"mIU/L","CLIA"),"T4 Libre (FT4)":(20.0,"ng/dL","CLIA"),
    "AST":(20.0,"U/L","CLIA"),"GGT":(20.0,"U/L","CLIA"),"LDH":(20.0,"U/L","CLIA"),
}
TEA_DEFAULT = 15.0

def calcular_sigma(df_analito, tea_pct):
    if df_analito.empty: return {}
    media=df_analito["Media_Objetivo"].iloc[0]; sd=df_analito["SD_Objetivo"].iloc[0]; vals=df_analito["Valor"]
    cv_pct=(sd/media)*100 if media!=0 else 0
    sesgo_pct=abs((vals.mean()-media)/media)*100 if media!=0 else 0
    sigma=(tea_pct-sesgo_pct)/cv_pct if cv_pct>0 else 0
    if sigma>=6:   cat="🏆 Clase Mundial"; color="#198754"
    elif sigma>=4: cat="✅ Buena calidad"; color="#0066CC"
    elif sigma>=3: cat="⚠️ Aceptable";    color="#FD7E14"
    else:          cat="🔴 Revisar método";color="#DC3545"
    return {"sigma":round(sigma,2),"cv_pct":round(cv_pct,2),"sesgo_pct":round(sesgo_pct,2),
            "tea_pct":tea_pct,"categoria":cat,"color":color,"media":round(media,3),"sd":round(sd,4),"n":len(vals)}


# ==============================================================
#  8. LEVEY-JENNINGS
# ==============================================================
def build_lj_figure(df_series, analito, nivel):
    u=df_series.iloc[-1]; m=u["Media_Objetivo"]; sd=u["SD_Objetivo"]
    nivel_label=NIVELES.get(nivel,NIVELES["N"])["label"]
    fig=go.Figure()
    for y0,y1,col in [(m+2*sd,m+3*sd,"rgba(220,53,69,.10)"),(m-3*sd,m-2*sd,"rgba(220,53,69,.10)"),
                       (m+sd,m+2*sd,"rgba(255,193,7,.08)"),(m-2*sd,m-sd,"rgba(255,193,7,.08)"),
                       (m-sd,m+sd,"rgba(25,135,84,.06)")]:
        fig.add_hrect(y0=y0,y1=y1,fillcolor=col,line_width=0)
    for y_v,color,width,dash,name in [
        (m,"#198754",2.0,"solid","Media"),(m+sd,"#ADB5BD",1.0,"dash","+1 SD"),(m-sd,"#ADB5BD",1.0,"dash","−1 SD"),
        (m+2*sd,"#FD7E14",1.4,"dash","+2 SD"),(m-2*sd,"#FD7E14",1.4,"dash","−2 SD"),
        (m+3*sd,"#DC3545",1.8,"dot","+3 SD"),(m-3*sd,"#DC3545",1.8,"dot","−3 SD"),
    ]:
        fig.add_hline(y=y_v,line_color=color,line_width=width,line_dash=dash,
                      annotation_text=name,annotation_position="right",
                      annotation_font=dict(color=color,size=10,family="Arial"))
    fig.add_trace(go.Scatter(x=df_series["Fecha"],y=df_series["Valor"],
                             mode="lines",line=dict(color="#CED4DA",width=1.5),showlegend=False,hoverinfo="skip"))
    for estado,color in [("Verde","#198754"),("Ámbar","#FD7E14"),("Rojo","#DC3545")]:
        sub=df_series[df_series["Estado"]==estado]
        if sub.empty: continue
        fig.add_trace(go.Scatter(x=sub["Fecha"],y=sub["Valor"],mode="markers",name=estado,
                                 marker=dict(size=9,color=color,line=dict(color="#FFFFFF",width=1.5))))
    fig.update_layout(
        template="plotly_white",
        title=dict(text=f"Levey-Jennings — {analito} · Nivel: {nivel_label}",
                   font=dict(size=13,color="#212529",family="Arial")),
        paper_bgcolor="#FFFFFF",plot_bgcolor="#FFFFFF",font=dict(color="#495057",family="Arial"),
        legend=dict(orientation="h",y=1.08,x=1,xanchor="right"),
        xaxis=dict(gridcolor="#F1F3F5",linecolor="#DEE2E6",tickformat="%d %b",title="Fecha"),
        yaxis=dict(gridcolor="#F1F3F5",linecolor="#DEE2E6",title="Valor"),
        height=380,width=760,margin=dict(l=10,r=110,t=55,b=40))
    return fig

def fig_to_png_bytes(fig):
    try: return fig.to_image(format="png",scale=2)
    except: return None


# ==============================================================
#  9. PDF
# ==============================================================
def generar_pdf(df_all, analitos, fuente):
    pdf=FPDF(); pdf.set_auto_page_break(auto=True,margin=15); pdf.add_page()
    pdf.set_fill_color(0,102,204); pdf.rect(0,0,210,36,"F")
    pdf.set_font("Helvetica","B",18); pdf.set_text_color(255,255,255); pdf.ln(8)
    pdf.cell(0,10,"AIQC – Informe de Incidencias de Calidad",ln=True,align="C")
    pdf.set_font("Helvetica","",9); pdf.set_text_color(220,235,255)
    pdf.cell(0,6,f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}  |  Fuente: {fuente}  |  Analitos: {', '.join(analitos)}",ln=True,align="C")
    pdf.ln(10)
    niveles_disponibles=sorted(df_all["Nivel"].unique()) if "Nivel" in df_all.columns else ["N"]

    def sec(txt):
        pdf.set_font("Helvetica","B",12); pdf.set_text_color(0,102,204)
        pdf.cell(0,8,txt,ln=True)
        pdf.set_draw_color(0,102,204); pdf.line(10,pdf.get_y(),200,pdf.get_y()); pdf.ln(3)

    sec("1. Resumen Ejecutivo por Nivel de Control")
    for niv in niveles_disponibles:
        frames=[evaluar_westgard(df_all[(df_all["Analito"]==an)&(df_all["Nivel"]==niv)].copy()) for an in analitos]
        df_ev=pd.concat([f for f in frames if not f.empty])
        if df_ev.empty: continue
        total=len(df_ev); rojos=int((df_ev["Estado"]=="Rojo").sum())
        ambar=int((df_ev["Estado"]=="Ámbar").sum()); ok=int((df_ev["Estado"]=="Verde").sum())
        pdf.set_font("Helvetica","B",10); pdf.set_text_color(33,37,41)
        pdf.cell(0,7,f"Nivel: {NIVELES.get(niv,NIVELES['N'])['label']}",ln=True)
        pdf.set_font("Helvetica","",9)
        pdf.cell(0,6,f"  Total: {total}  |  Verde: {ok} ({100*ok//total if total else 0}%)  |  Ámbar: {ambar}  |  Rojo: {rojos}",ln=True)
        pdf.ln(2)

    sec("2. Estado por Analito y Nivel  [Z = (x - media) / SD]")
    pdf.set_font("Helvetica","",8); pdf.set_text_color(80,80,80)
    pdf.cell(0,5,REGLAS_DESC,ln=True); pdf.ln(2)
    col_w=[40,26,20,22,22,26,22,20]; hdrs=["Analito","Nivel","Valor","Z-Score","Score","Regla","Estado","N pts"]
    pdf.set_fill_color(240,242,245); pdf.set_text_color(73,80,87); pdf.set_font("Helvetica","B",8)
    for w,h in zip(col_w,hdrs): pdf.cell(w,8,h,border=1,fill=True)
    pdf.ln()
    for an in analitos:
        for niv in niveles_disponibles:
            sub=evaluar_westgard(df_all[(df_all["Analito"]==an)&(df_all["Nivel"]==niv)].copy())
            if sub.empty: continue
            u=sub.iloc[-1]; niv_label=NIVELES.get(niv,NIVELES["N"])["label"]
            if u["Estado"]=="Rojo":    pdf.set_fill_color(252,232,232); pdf.set_text_color(155,28,28)
            elif u["Estado"]=="Ámbar": pdf.set_fill_color(255,243,205); pdf.set_text_color(133,100,4)
            else:                       pdf.set_fill_color(209,247,231); pdf.set_text_color(10,102,64)
            pdf.set_font("Helvetica","",8)
            for w,v in zip(col_w,[an[:22],niv_label[:14],str(u["Valor"]),f"{u['Z_Score']:+.2f}",
                                   f"{int(u['Score_Riesgo'])}/100",u["Regla_Violada"],u["Estado"],str(len(sub))]):
                pdf.cell(w,7,str(v),border=1,fill=True)
            pdf.ln()
    pdf.ln(5)

    sec("3. Gráficos Levey-Jennings por Analito y Nivel")
    for an in analitos:
        for niv in niveles_disponibles:
            sub_ev=evaluar_westgard(df_all[(df_all["Analito"]==an)&(df_all["Nivel"]==niv)].copy())
            if sub_ev.empty: continue
            fig=build_lj_figure(sub_ev,an,niv); png=fig_to_png_bytes(fig)
            niv_label=NIVELES.get(niv,NIVELES["N"])["label"]
            if png:
                tmp=f"/tmp/lj_{an.replace(' ','_').replace('(','').replace(')','_')}_{niv}.png"
                open(tmp,"wb").write(png)
                pdf.set_font("Helvetica","B",10); pdf.set_text_color(33,37,41)
                pdf.cell(0,7,f"{an} — Nivel: {niv_label}",ln=True)
                pdf.image(tmp,x=10,w=190); pdf.ln(4)
    pdf.ln(3)

    sec("4. Guía Bio-Rad de Acciones Correctivas")
    pdf.set_font("Helvetica","",9); pdf.set_text_color(33,37,41)
    alarmas_generadas = set()
    for an in analitos:
        for niv in niveles_disponibles:
            sub=evaluar_westgard(df_all[(df_all["Analito"]==an)&(df_all["Nivel"]==niv)].copy())
            if sub.empty: continue
            u=sub.iloc[-1]
            if u["Estado"]!="Verde" and an not in alarmas_generadas:
                alarmas_generadas.add(an)
                kb=buscar_kb(an, u["Estado"])
                if not kb: continue
                niv_label=NIVELES.get(niv,NIVELES["N"])["label"]
                pdf.set_font("Helvetica","B",10)
                if u["Estado"]=="Rojo": pdf.set_text_color(155,28,28)
                else: pdf.set_text_color(133,100,4)
                pdf.cell(0,7,f"{'🔴' if u['Estado']=='Rojo' else '🟡'} {an} [{niv_label}] — Regla {u['Regla_Violada']}",ln=True)
                pdf.set_font("Helvetica","",8); pdf.set_text_color(33,37,41)
                pdf.cell(0,5,f"Producto: {kb['producto']}",ln=True)
                pdf.set_font("Helvetica","B",8); pdf.cell(0,5,"Causas probables:",ln=True)
                pdf.set_font("Helvetica","",8)
                for c in kb["causas_comunes"][:3]: pdf.multi_cell(0,5,f"  • {c}"); 
                pdf.set_font("Helvetica","B",8); pdf.cell(0,5,"Acciones correctivas:",ln=True)
                pdf.set_font("Helvetica","",8)
                acciones=kb["acciones_1_3s"] if u["Estado"]=="Rojo" else kb["acciones_warn"]
                for a in acciones[:4]: pdf.multi_cell(0,5,f"  • {a.replace('🔴','').replace('🟡','').strip()}")
                pdf.cell(0,5,f"Interferencias: {kb['interferencias'][:80]}...",ln=True)
                pdf.cell(0,5,f"Referencia: {kb['referencia']}",ln=True); pdf.ln(3)

    if not alarmas_generadas:
        pdf.set_font("Helvetica","I",9); pdf.set_text_color(10,102,64)
        pdf.cell(0,7,"Sin alarmas activas — no se requieren acciones correctivas.",ln=True)
    pdf.ln(4)
    pdf.set_draw_color(222,226,230); pdf.line(10,pdf.get_y(),200,pdf.get_y()); pdf.ln(2)
    pdf.set_font("Helvetica","I",8); pdf.set_text_color(108,117,125)
    pdf.cell(0,5,"AIQC v4.8 · Powered by Bio-Rad KB · Uso interno del laboratorio",ln=True,align="C")
    return bytes(pdf.output())


# ==============================================================
#  10. ASISTENTE IA GEMINI
# ==============================================================
MAX_TURNS = 10

def ia_responde_gemini(pregunta, historial, df_all, analitos_ls, f_min, f_max):
    api_key=get_api_key()
    if not api_key: return "❌ **API Key de Gemini no configurada.**"
    genai.configure(api_key=api_key)
    niveles_disponibles=sorted(df_all["Nivel"].unique()) if "Nivel" in df_all.columns else ["N"]
    resumen=[]
    for an in analitos_ls:
        for niv in niveles_disponibles:
            sub=evaluar_westgard(df_all[(df_all["Analito"]==an)&(df_all["Nivel"]==niv)&
                                        (df_all["Fecha"]>=pd.Timestamp(f_min))&
                                        (df_all["Fecha"]<=pd.Timestamp(f_max))].copy())
            if sub.empty: continue
            u=sub.iloc[-1]; z_calc=(u['Valor']-u['Media_Objetivo'])/u['SD_Objetivo']
            tea=TEA_CLIA.get(an,(TEA_DEFAULT,"",""))[0]; sig=calcular_sigma(sub,tea)
            niv_label=NIVELES.get(niv,NIVELES["N"])["label"]
            kb=buscar_kb(an,u["Estado"])
            kb_txt=""
            if kb and u["Estado"]!="Verde":
                causas="; ".join(kb["causas_comunes"][:2])
                acciones="; ".join((kb["acciones_1_3s"] if u["Estado"]=="Rojo" else kb["acciones_warn"])[:2])
                kb_txt=f"\n  - Bio-Rad causas: {causas}\n  - Bio-Rad acciones: {acciones}"
            resumen.append(
                f"• {an} | Nivel: {niv_label}\n"
                f"  - Valor: {u['Valor']} | Media: {u['Media_Objetivo']} | SD: {u['SD_Objetivo']}\n"
                f"  - Z = {z_calc:+.3f} | Estado: {u['Estado']} | Regla: {u['Regla_Violada']} | Score: {int(u['Score_Riesgo'])}/100\n"
                f"  - Sigma: {sig.get('sigma','N/A')}σ | CV: {sig.get('cv_pct','N/A')}% | Sesgo: {sig.get('sesgo_pct','N/A')}%{kb_txt}")
    contexto=(
        f"=== DATOS REALES ({f_min} → {f_max}) ===\n{chr(10).join(resumen)}\n\n"
        f"=== REGLAS WESTGARD ===\n{REGLAS_DESC}\n\n"
        f"=== SIGMA METRICS ===\n≥6σ: Clase Mundial | ≥4σ: Buena | ≥3σ: Aceptable | <3σ: Revisar\n\n"
        f"=== CONTROLES BIO-RAD ===\nLiquichek (bioquímica) + Lyphochek (inmunoensayo/hormonal)\n\n"
        f"=== PREGUNTA ===\n{pregunta}"
    )
    recent=historial[1:][-MAX_TURNS*2:]
    gemini_hist=[{"role":"user" if m["role"]=="user" else "model","parts":[m["content"]]} for m in recent]
    last_error=""
    for model_name in GEMINI_MODELS:
        try:
            m=genai.GenerativeModel(model_name=model_name,generation_config=GEMINI_CFG,system_instruction=GEMINI_SYSTEM)
            chat=m.start_chat(history=gemini_hist); resp=chat.send_message(contexto)
            st.session_state["gemini_model_active"]=model_name; return resp.text
        except Exception as e:
            last_error=str(e)
            if "api_key" in last_error.lower() or "403" in last_error: return "❌ API Key inválida."
            continue
    return f"⚠️ Modelos no disponibles.\n\n_Error: {last_error}_"


# ==============================================================
#  11. SIDEBAR
# ==============================================================
with st.sidebar:
    st.markdown('<div class="sb-logo">🔬</div>',unsafe_allow_html=True)
    st.markdown('<div class="sb-title">AIQC</div>',unsafe_allow_html=True)
    st.markdown('<div class="sb-sub">Quality Control · v4.8 · Bio-Rad KB</div>',unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**📂 Fuente de datos**")
    uploaded=st.file_uploader("CSV o Excel",type=["csv","xlsx","xls"],
        help="Columnas: Fecha, Analito, Nivel (N/PB/PA), Valor, Media_Objetivo, SD_Objetivo, Lote.")
    if uploaded:
        df_cargado,err=leer_archivo(uploaded)
        if df_cargado is not None:
            df_all=df_cargado; data_src=f"📄 {uploaded.name}"
            st.markdown(f'<div class="data-pill">✅ <b>{uploaded.name}</b><br>{len(df_all)} filas · {df_all["Analito"].nunique()} analito(s)</div>',unsafe_allow_html=True)
        else:
            st.error(err); df_all=build_demo(datetime.today().strftime("%Y-%m-%d")); data_src="Demo (error)"
    else:
        df_all=build_demo(datetime.today().strftime("%Y-%m-%d")); data_src="🔬 Modo Demo"
        st.caption("Datos simulados con 3 niveles de control.")

    st.markdown("---")
    analito=st.selectbox("Analito activo",options=sorted(df_all["Analito"].unique()),key="sel_analito")
    niveles_analito=sorted(df_all[df_all["Analito"]==analito]["Nivel"].unique())
    nivel_options={NIVELES.get(n,NIVELES["N"])["label"]:n for n in niveles_analito}
    nivel_sel_label=st.selectbox("Nivel de control",options=list(nivel_options.keys()),key="sel_nivel")
    nivel_activo=nivel_options[nivel_sel_label]

    fechas_d=sorted(df_all["Fecha"].dropna().unique())
    if len(fechas_d)>=2:
        f_min=st.date_input("Desde",value=pd.Timestamp(fechas_d[0]).date(),
                            min_value=pd.Timestamp(fechas_d[0]).date(),max_value=pd.Timestamp(fechas_d[-1]).date(),key="f1")
        f_max=st.date_input("Hasta",value=pd.Timestamp(fechas_d[-1]).date(),
                            min_value=pd.Timestamp(fechas_d[0]).date(),max_value=pd.Timestamp(fechas_d[-1]).date(),key="f2")
    else:
        f_min=f_max=pd.Timestamp(fechas_d[0]).date() if fechas_d else datetime.today().date()

    st.markdown("---")
    st.markdown("**Estado del laboratorio**")
    for an in sorted(df_all["Analito"].unique()):
        for niv in sorted(df_all[df_all["Analito"]==an]["Nivel"].unique()):
            sub=evaluar_westgard(df_all[(df_all["Analito"]==an)&(df_all["Nivel"]==niv)].copy())
            est=sub.iloc[-1]["Estado"]; led={"Verde":"🟢","Ámbar":"🟡","Rojo":"🔴"}.get(est,"⚪")
            st.markdown(f"{led} **{an}** · {NIVELES.get(niv,NIVELES['N'])['label']} — {est}")

    st.markdown("---")
    if st.button("Cerrar sesión",use_container_width=True):
        st.session_state["auth"]=False; st.rerun()
    st.caption(f"Fuente: {data_src}")


# ==============================================================
#  12. DATOS ACTIVOS
# ==============================================================
df_raw=df_all[(df_all["Analito"]==analito)&(df_all["Nivel"]==nivel_activo)&
              (df_all["Fecha"]>=pd.Timestamp(f_min))&(df_all["Fecha"]<=pd.Timestamp(f_max))].copy()
df_series=evaluar_westgard(df_raw)
ultima=df_series.iloc[-1] if not df_series.empty else None
analitos_ls=sorted(df_all["Analito"].unique())


# ==============================================================
#  13. CABECERA
# ==============================================================
c1,c2=st.columns([4,1])
with c1:
    st.markdown("## 🔬 AIQC – Control de Calidad")
    st.markdown(
        f"<span style='color:#6C757D;font-size:.9rem'>"
        f"<b>Analito:</b> {analito} &nbsp;·&nbsp; {nivel_badge(nivel_activo)} &nbsp;·&nbsp; "
        f"<b>Período:</b> {f_min.strftime('%d/%m/%Y')} → {f_max.strftime('%d/%m/%Y')} "
        f"&nbsp;·&nbsp; <b>Fuente:</b> {data_src}</span>",unsafe_allow_html=True)
with c2:
    if ultima is not None:
        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown(estado_badge(ultima["Estado"]),unsafe_allow_html=True)
st.markdown("<hr>",unsafe_allow_html=True)


# ==============================================================
#  14. TABS
# ==============================================================
tab_dash,tab_sigma,tab_biorad,tab_chat,tab_log=st.tabs([
    "📊  Dashboard","📈  Sigma Metrics","📋  Guía Bio-Rad","🤖  Asistente IA (Gemini)","📝  Registro",
])


# ── TAB 1: DASHBOARD ─────────────────────────────────────────
with tab_dash:
    if df_series.empty or ultima is None:
        st.warning("No hay datos para el analito/nivel/rango seleccionado.")
    else:
        score=int(ultima["Score_Riesgo"]); zscore=round(ultima["Z_Score"],2)
        risk_c={"Verde":"#1A7F4B","Ámbar":"#856404","Rojo":"#9B1C1C"}.get(ultima["Estado"],"#1A7F4B")
        k1,k2,k3,k4,k5=st.columns(5)
        for col,val,lbl,color,sub in [
            (k1,f"{ultima['Valor']}","Valor Actual","#0066CC","Última medición"),
            (k2,f"{ultima['Media_Objetivo']}","Media Objetivo","#5A6ACA","μ objetivo"),
            (k3,f"±{ultima['SD_Objetivo']}","SD Objetivo","#7952B3","σ objetivo"),
            (k4,f"{zscore:+.2f}σ","Z-Score","#C0392B" if abs(zscore)>=2 else "#1A7F4B","Z=(x-μ)/σ"),
            (k5,f"{score}/100","Score de Riesgo",risk_c,ultima["Estado"]),
        ]:
            with col:
                st.markdown(f'<div class="kpi-card"><div class="kpi-val" style="color:{color}">{val}</div>'
                            f'<div class="kpi-lbl">{lbl}</div><div class="kpi-sub">{sub}</div></div>',
                            unsafe_allow_html=True)

        # Mostrar guía Bio-Rad inline si hay alarma
        if ultima["Estado"] != "Verde":
            st.markdown("<br>", unsafe_allow_html=True)
            render_kb_panel(analito, ultima["Estado"], ultima["Regla_Violada"], nivel_activo)

        st.markdown("<br>",unsafe_allow_html=True)
        nivs_analito=sorted(df_all[df_all["Analito"]==analito]["Nivel"].unique())
        if len(nivs_analito)>1:
            st.markdown('<div class="sec-head">Comparativa de niveles — Levey-Jennings</div>',unsafe_allow_html=True)
            tabs_niveles=st.tabs([f"{NIVELES.get(n,NIVELES['N'])['icon']} {NIVELES.get(n,NIVELES['N'])['label']}" for n in nivs_analito])
            for tab_n,niv in zip(tabs_niveles,nivs_analito):
                with tab_n:
                    sub_n=evaluar_westgard(df_all[(df_all["Analito"]==analito)&(df_all["Nivel"]==niv)&
                                                   (df_all["Fecha"]>=pd.Timestamp(f_min))&
                                                   (df_all["Fecha"]<=pd.Timestamp(f_max))].copy())
                    if sub_n.empty: st.info("Sin datos para este nivel.")
                    else:
                        fig_n=build_lj_figure(sub_n,analito,niv)
                        fig_n.update_layout(height=400,margin=dict(l=10,r=130,t=60,b=10))
                        st.plotly_chart(fig_n,use_container_width=True)
        else:
            fig=build_lj_figure(df_series,analito,nivel_activo)
            fig.update_layout(height=460,width=None,margin=dict(l=10,r=130,t=60,b=10))
            st.plotly_chart(fig,use_container_width=True)

        st.markdown('<div class="sec-head">Últimas 7 mediciones</div>',unsafe_allow_html=True)
        tail=df_series.tail(7)[["Fecha","Valor","Z_Score","Regla_Violada","Score_Riesgo","Estado","Lote"]].copy()
        tail["Fecha"]=tail["Fecha"].dt.strftime("%d/%m/%Y")
        tail["Estado"]=tail["Estado"].apply(estado_badge)
        st.write(tail.rename(columns={"Z_Score":"Z-Score","Regla_Violada":"Regla","Score_Riesgo":"Score"})
                     .to_html(escape=False,index=False),unsafe_allow_html=True)


# ── TAB 2: SIGMA METRICS ─────────────────────────────────────
with tab_sigma:
    st.markdown("### 📈 Sigma Metrics — Evaluación de Calidad Analítica")
    st.caption("Sigma = (TEa% − Sesgo%) / CV%  ·  TEa según criterios CLIA  ·  Desglosado por nivel.")
    with st.expander("⚙️ Editar límites TEa por analito",expanded=False):
        tea_editado={}
        cols_tea=st.columns(min(len(analitos_ls),3))
        for i,an in enumerate(analitos_ls):
            default_tea=TEA_CLIA.get(an,(TEA_DEFAULT,"",""))[0]
            with cols_tea[i%len(cols_tea)]:
                tea_editado[an]=st.number_input(f"TEa% — {an.split('(')[0].strip()}",
                    min_value=1.0,max_value=50.0,value=float(default_tea),step=0.5,key=f"tea_{an}")
    st.markdown("<br>",unsafe_allow_html=True)
    niveles_globales=sorted(df_all["Nivel"].unique())
    sigma_data=[]
    for an in analitos_ls:
        for niv in niveles_globales:
            sub=df_all[(df_all["Analito"]==an)&(df_all["Nivel"]==niv)&
                       (df_all["Fecha"]>=pd.Timestamp(f_min))&(df_all["Fecha"]<=pd.Timestamp(f_max))].copy()
            if sub.empty: continue
            tea=tea_editado.get(an,TEA_DEFAULT); sig=calcular_sigma(sub,tea)
            if sig: sigma_data.append({"analito":an,"nivel":niv,"nivel_label":NIVELES.get(niv,NIVELES["N"])["label"],**sig})
    if not sigma_data:
        st.warning("Sin datos suficientes.")
    else:
        for niv in niveles_globales:
            niv_cfg=NIVELES.get(niv,NIVELES["N"]); niv_data=[d for d in sigma_data if d["nivel"]==niv]
            if not niv_data: continue
            st.markdown(f'<div class="sec-head">{niv_cfg["icon"]} {niv_cfg["label"]}</div>',unsafe_allow_html=True)
            cols_s=st.columns(len(niv_data))
            for col,d in zip(cols_s,niv_data):
                with col:
                    st.markdown(f'<div class="kpi-card"><div class="kpi-val" style="color:{d["color"]}">{d["sigma"]}σ</div>'
                                f'<div class="kpi-lbl">{d["analito"].split("(")[0].strip()}</div>'
                                f'<div class="kpi-sub">{d["categoria"]}</div></div>',unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        fig_s=go.Figure()
        colores_nivel={"N":"#0066CC","PB":"#FD7E14","PA":"#DC3545"}
        for niv in niveles_globales:
            niv_data=[d for d in sigma_data if d["nivel"]==niv]
            if not niv_data: continue
            fig_s.add_trace(go.Bar(
                name=NIVELES.get(niv,NIVELES["N"])["label"],
                x=[d["analito"].split("(")[0].strip() for d in niv_data],
                y=[d["sigma"] for d in niv_data],
                marker_color=colores_nivel.get(niv,"#0066CC"),
                marker_line_color="#FFFFFF",marker_line_width=1.5,
                text=[f"{d['sigma']}σ" for d in niv_data],textposition="outside",
                hovertemplate="<b>%{x}</b><br>Sigma: <b>%{y}σ</b><extra></extra>"))
        for y_v,color,lbl in [(6,"#198754","6σ"),(4,"#0066CC","4σ"),(3,"#FD7E14","3σ")]:
            fig_s.add_hline(y=y_v,line_color=color,line_width=1.5,line_dash="dash",
                            annotation_text=lbl,annotation_position="right",
                            annotation_font=dict(color=color,size=11))
        fig_s.add_hrect(y0=6,y1=10,fillcolor="rgba(25,135,84,.07)",line_width=0)
        fig_s.add_hrect(y0=4,y1=6,fillcolor="rgba(0,102,204,.06)",line_width=0)
        fig_s.add_hrect(y0=3,y1=4,fillcolor="rgba(253,126,20,.06)",line_width=0)
        fig_s.add_hrect(y0=0,y1=3,fillcolor="rgba(220,53,69,.06)",line_width=0)
        fig_s.update_layout(template="plotly_white",barmode="group",
            title=dict(text="Sigma Metrics por Analito y Nivel",font=dict(size=15,color="#212529",family="Inter")),
            paper_bgcolor="#FFFFFF",plot_bgcolor="#FFFFFF",font=dict(color="#495057",family="Inter"),
            xaxis=dict(gridcolor="#F1F3F5",linecolor="#DEE2E6",title="Analito"),
            yaxis=dict(gridcolor="#F1F3F5",linecolor="#DEE2E6",title="Sigma (σ)",range=[0,11]),
            height=440,margin=dict(l=10,r=130,t=60,b=10),
            legend=dict(orientation="h",y=1.08,x=0.5,xanchor="center"))
        st.plotly_chart(fig_s,use_container_width=True)
        st.write(pd.DataFrame([{
            "Analito":d["analito"],"Nivel":d["nivel_label"],"N":d["n"],"Media":d["media"],"SD":d["sd"],
            "CV%":f"{d['cv_pct']}%","Sesgo%":f"{d['sesgo_pct']}%","TEa%":f"{d['tea_pct']}%",
            "Sigma":d["sigma"],"Categoría":d["categoria"]} for d in sigma_data
        ]).to_html(escape=False,index=False),unsafe_allow_html=True)
        for d in sigma_data:
            s=d["sigma"]; lbl=f"**{d['analito']} [{d['nivel_label']}]** — **{s}σ**"
            if s>=6:   st.success(f"{lbl} clase mundial.")
            elif s>=4: st.info(f"{lbl} buena calidad.")
            elif s>=3: st.warning(f"{lbl} aceptable. Aumenta frecuencia de controles.")
            else:      st.error(f"{lbl} deficiente. Revisar calibración y reactivos.")


# ── TAB 3: GUÍA BIO-RAD ──────────────────────────────────────
with tab_biorad:
    st.markdown("### 📋 Guía Bio-Rad de Acciones Correctivas")
    st.markdown(
        "Base de conocimiento basada en los inserts de **Liquichek** (bioquímica) y **Lyphochek** "
        "(inmunoensayo/hormonal) de Bio-Rad, complementada con CLSI y Westgard Associates. "
        "Consulta siempre el insert de tu lote específico en "
        "[myeInserts QCNet](https://myeinserts-app.qcnet.com/home).")

    # Selector de analito para consulta manual
    col_sel1, col_sel2 = st.columns([2, 1])
    with col_sel1:
        an_kb = st.selectbox("Analito a consultar",
                             options=list(BIORAD_KB.keys()),
                             key="kb_analito_sel")
    with col_sel2:
        estado_kb = st.selectbox("Simular estado",
                                 options=["Rojo (1_3s)","Ámbar (4_1s / 10_x)","Verde (informativo)"],
                                 key="kb_estado_sel")

    estado_sim = "Rojo" if "Rojo" in estado_kb else "Ámbar" if "Ámbar" in estado_kb else "Verde"
    regla_sim  = "1_3s" if estado_sim=="Rojo" else "4_1s" if estado_sim=="Ámbar" else "—"

    st.markdown("<br>", unsafe_allow_html=True)
    render_kb_panel(an_kb, estado_sim, regla_sim, nivel_activo)

    st.markdown("---")
    st.markdown("### 🔴 Alarmas activas en el período seleccionado")
    hay_alarmas = False
    for an in analitos_ls:
        for niv in sorted(df_all["Nivel"].unique()):
            sub=evaluar_westgard(df_all[(df_all["Analito"]==an)&(df_all["Nivel"]==niv)&
                                        (df_all["Fecha"]>=pd.Timestamp(f_min))&
                                        (df_all["Fecha"]<=pd.Timestamp(f_max))].copy())
            if sub.empty: continue
            u=sub.iloc[-1]
            if u["Estado"]!="Verde":
                hay_alarmas=True
                render_kb_panel(an, u["Estado"], u["Regla_Violada"], niv)
    if not hay_alarmas:
        st.success("✅ No hay alarmas activas en el período seleccionado. ¡El laboratorio opera correctamente!")

    st.markdown("---")
    st.markdown("### 📚 Cobertura de la base de conocimiento")
    for grupo, analitos_grupo in GRUPOS_ANALITICOS.items():
        con_ficha = [a for a in analitos_grupo if a in BIORAD_KB]
        st.markdown(f"**{grupo}:** " + " · ".join([f"`{a}`" for a in con_ficha]))


# ── TAB 4: ASISTENTE IA ──────────────────────────────────────
with tab_chat:
    st.markdown("### 🤖 Asistente AIQC — Powered by Google Gemini")
    modelo_activo=st.session_state.get("gemini_model_active","models/gemini-2.5-flash")
    st.markdown(
        f'<div class="gemini-banner">🟢 <b>Google Gemini activo</b> · Modelo: <code>{modelo_activo}</code> · '
        f'Historial: {MAX_TURNS} turnos · Base de conocimiento Bio-Rad integrada en contexto.</div>',
        unsafe_allow_html=True)
    if "messages" not in st.session_state:
        st.session_state["messages"]=[{"role":"assistant","content":(
            "¡Hola! Soy el **Asistente AIQC v4.8** con base de conocimiento **Bio-Rad** integrada.\n\n"
            "Prueba a preguntarme:\n"
            "- *¿Por qué puede fallar el control de ALT en el nivel Patológico Alto?*\n"
            "- *¿Qué hago si el Potasio da 1_3s en el nivel Normal?*\n"
            "- *Explícame las interferencias del colesterol según Bio-Rad*\n"
            "- *Dame un plan correctivo completo para las alarmas activas*"
        )}]
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"],avatar="🤖" if msg["role"]=="assistant" else "👤"):
            st.markdown(msg["content"])
    if prompt:=st.chat_input("Escribe tu consulta clínica…"):
        st.session_state["messages"].append({"role":"user","content":prompt})
        with st.chat_message("user",avatar="👤"): st.markdown(prompt)
        with st.chat_message("assistant",avatar="🤖"):
            with st.spinner("Analizando datos y consultando Base Bio-Rad…"):
                resp=ia_responde_gemini(prompt,st.session_state["messages"],df_all,analitos_ls,f_min,f_max)
                st.markdown(resp)
        st.session_state["messages"].append({"role":"assistant","content":resp})
    if st.button("🗑️ Nueva conversación",key="clr"):
        st.session_state["messages"]=[st.session_state["messages"][0]]; st.rerun()


# ── TAB 5: REGISTRO ───────────────────────────────────────────
with tab_log:
    col_ttl,col_pdf=st.columns([3,1])
    with col_ttl:
        st.markdown("### 📝 Registro de Incidencias y Trazabilidad")
        st.caption("Acciones persistentes en SQLite. Desglose por nivel de control.")
    with col_pdf:
        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("📄 Descargar PDF",use_container_width=True,type="primary"):
            with st.spinner("Generando informe con guía Bio-Rad…"):
                try:
                    pdf_bytes=generar_pdf(df_all,analitos_ls,data_src)
                    fname=f"AIQC_Informe_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                    st.download_button("⬇️ Guardar PDF",data=pdf_bytes,file_name=fname,
                                       mime="application/pdf",use_container_width=True)
                    st.success("✅ Informe generado.")
                except Exception as e:
                    st.error(f"Error: {e}")

    niveles_globales_log=sorted(df_all["Nivel"].unique())
    all_log_frames=[]
    for an in analitos_ls:
        for niv in niveles_globales_log:
            sub=evaluar_westgard(df_all[(df_all["Analito"]==an)&(df_all["Nivel"]==niv)&
                                        (df_all["Fecha"]>=pd.Timestamp(f_min))&
                                        (df_all["Fecha"]<=pd.Timestamp(f_max))].copy())
            if not sub.empty:
                sub["_nivel_label"]=NIVELES.get(niv,NIVELES["N"])["label"]; all_log_frames.append(sub)

    df_full_log=pd.concat(all_log_frames) if all_log_frames else pd.DataFrame()
    df_log=df_full_log[df_full_log["Estado"]!="Verde"].copy().reset_index(drop=True) if not df_full_log.empty else pd.DataFrame()

    if df_log.empty:
        st.success("✅ Sin violaciones en el período seleccionado.")
    else:
        acciones_db=load_acciones(db_con)
        hcols=st.columns([1.4,2.0,1.4,1.1,1.2,1.3,1.4,1.4,1.3])
        for c,lbl in zip(hcols,["📅 Fecha","🔬 Analito","Nivel","Valor","Z-Score","Regla","Score","Estado","✅ Acción"]):
            c.markdown(f"**{lbl}**")
        st.markdown("<hr>",unsafe_allow_html=True)
        for idx,row in df_log.iterrows():
            key=f"{row['Fecha'].date()}_{row['Analito']}_{row.get('_nivel_label','N')}_{idx}"
            rcols=st.columns([1.4,2.0,1.4,1.1,1.2,1.3,1.4,1.4,1.3])
            rcols[0].write(row["Fecha"].strftime("%d/%m/%Y"))
            rcols[1].write(row["Analito"])
            rcols[2].markdown(nivel_badge(row.get("Nivel","N")),unsafe_allow_html=True)
            rcols[3].write(str(row["Valor"]))
            rcols[4].write(f"{row['Z_Score']:+.2f}σ")
            rcols[5].write(row["Regla_Violada"])
            rcols[6].write(f"{int(row['Score_Riesgo'])}/100")
            rcols[7].markdown(estado_badge(row["Estado"]),unsafe_allow_html=True)
            prev=acciones_db.get(key,False)
            nuevo=rcols[8].checkbox("Hecha",value=prev,key=f"accion_{key}")
            if nuevo!=prev: save_accion(db_con,key,nuevo)

        st.markdown("<hr>",unsafe_allow_html=True)
        acciones_db=load_acciones(db_con)
        claves_log=[f"{row['Fecha'].date()}_{row['Analito']}_{row.get('_nivel_label','N')}_{idx}" for idx,row in df_log.iterrows()]
        total=len(df_log); hechas=sum(acciones_db.get(k,False) for k in claves_log); pend=total-hechas
        m1,m2,m3,m4=st.columns(4)
        m1.metric("Total violaciones",total); m2.metric("Acciones tomadas ✅",hechas)
        m3.metric("Pendientes ⏳",pend); m4.metric("% completado",f"{int(hechas/total*100) if total else 0}%")
        if hechas==total: st.success("🎉 Trazabilidad completa.")
        elif pend: st.warning(f"⚠️ {pend} violación(es) pendiente(s).")
