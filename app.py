# ==============================================================
#  AIQC – Artificial Intelligence for Quality Control
#  Versión: 4.9 – Rediseño SaaS médico (gris + azul/verde)
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
#  ESTILOS GLOBALES v4.9
# ==============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── BASE ─────────────────────────────────────────────────── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"] {
    background-color: #F4F6F9 !important;
    color: #1C2B3A;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }

/* ── SIDEBAR ───────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1E2D40 0%, #16202E 100%) !important;
    border-right: none !important;
    box-shadow: 4px 0 24px rgba(0,0,0,.18);
}
[data-testid="stSidebar"] * { color: #CBD5E1 !important; }
[data-testid="stSidebar"] strong,
[data-testid="stSidebar"] b   { color: #E2E8F0 !important; }
[data-testid="stSidebar"] hr  { border-color: rgba(255,255,255,.10) !important; }
[data-testid="stSidebar"] .stCaption { color: #64748B !important; }
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background: rgba(255,255,255,.05) !important;
    border: 1.5px dashed rgba(255,255,255,.20) !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: rgba(255,255,255,.08) !important;
    border: 1px solid rgba(255,255,255,.15) !important;
    border-radius: 8px !important;
    color: #E2E8F0 !important;
}
[data-testid="stSidebar"] [data-testid="stDateInput"] input {
    background: rgba(255,255,255,.08) !important;
    border: 1px solid rgba(255,255,255,.15) !important;
    border-radius: 8px !important;
    color: #E2E8F0 !important;
}

/* ── INPUTS (área principal) ───────────────────────────────── */
[data-baseweb="select"] > div,
[data-testid="stTextInput"] input,
[data-testid="stDateInput"] input {
    background-color: #FFFFFF !important;
    border: 1.5px solid #D1D9E0 !important;
    border-radius: 8px !important;
    color: #1C2B3A !important;
    transition: border-color .2s;
}

/* ── BOTONES ───────────────────────────────────────────────── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1A6FC4 0%, #1557A0 100%) !important;
    border: none !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    letter-spacing: .02em !important;
    box-shadow: 0 2px 8px rgba(26,111,196,.30) !important;
    transition: all .2s !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #1557A0 0%, #0F3F78 100%) !important;
    box-shadow: 0 4px 16px rgba(26,111,196,.40) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"] {
    background-color: #FFFFFF !important;
    border: 1.5px solid #1A6FC4 !important;
    color: #1A6FC4 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all .2s !important;
}
.stButton > button[kind="secondary"]:hover { background-color: #EBF3FF !important; }

/* ── TABS ──────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 5px 6px;
    box-shadow: 0 1px 4px rgba(0,0,0,.06);
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-radius: 8px !important;
    color: #64748B !important;
    font-weight: 500 !important;
    font-size: .875rem !important;
    padding: 8px 18px !important;
    transition: all .18s !important;
}
.stTabs [data-baseweb="tab"]:hover {
    background: #F1F5F9 !important;
    color: #1A6FC4 !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #1A6FC4 0%, #0D9E6E 100%) !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 8px rgba(26,111,196,.28) !important;
}

/* ── KPI CARDS ─────────────────────────────────────────────── */
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E8EDF2;
    border-top: 3px solid #1A6FC4;
    border-radius: 14px;
    padding: 22px 20px 18px 20px;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,.06);
    transition: box-shadow .22s, transform .22s;
}
.kpi-card:hover {
    box-shadow: 0 8px 28px rgba(0,0,0,.11);
    transform: translateY(-3px);
}
.kpi-card.estado-verde { border-top-color: #0D9E6E; }
.kpi-card.estado-ambar { border-top-color: #F59E0B; }
.kpi-card.estado-rojo  { border-top-color: #E53E3E; }
.kpi-val {
    font-size: 2.1rem; font-weight: 800;
    letter-spacing: -.6px; line-height: 1.1;
}
.kpi-lbl {
    font-size: .70rem; font-weight: 700; color: #94A3B8;
    text-transform: uppercase; letter-spacing: .10em; margin-top: 8px;
}
.kpi-sub { font-size: .76rem; color: #B0BAC9; margin-top: 3px; }

/* ── BADGES DE ESTADO ──────────────────────────────────────── */
.badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 5px 14px; border-radius: 999px;
    font-size: .78rem; font-weight: 700; letter-spacing: .03em;
    box-shadow: 0 1px 4px rgba(0,0,0,.10);
}
.badge-green { background: linear-gradient(135deg,#D1FAE5,#A7F3D0); color:#065F46; border:1px solid #6EE7B7; }
.badge-amber { background: linear-gradient(135deg,#FEF3C7,#FDE68A); color:#92400E; border:1px solid #FCD34D; }
.badge-red   { background: linear-gradient(135deg,#FEE2E2,#FECACA); color:#991B1B; border:1px solid #FCA5A5; }

/* ── BADGES DE NIVEL ───────────────────────────────────────── */
.nivel-pill { display:inline-block; padding:4px 13px; border-radius:999px; font-size:.76rem; font-weight:700; letter-spacing:.03em; }
.nivel-N  { background:#EFF6FF; color:#1D4ED8; border:1px solid #BFDBFE; }
.nivel-PB { background:#FFFBEB; color:#92400E; border:1px solid #FDE68A; }
.nivel-PA { background:#FFF1F2; color:#9F1239; border:1px solid #FECDD3; }

/* ── HEADER PRINCIPAL ──────────────────────────────────────── */
.aiqc-header {
    background: linear-gradient(135deg, #1A6FC4 0%, #0D9E6E 100%);
    border-radius: 16px; padding: 22px 28px; margin-bottom: 24px;
    box-shadow: 0 4px 20px rgba(26,111,196,.22);
}
.aiqc-header h2 { color:#FFFFFF !important; margin:0 0 4px 0; font-size:1.5rem; font-weight:800; }
.aiqc-header .meta { color:rgba(255,255,255,.82); font-size:.875rem; }

/* ── SIDEBAR LOGO / TÍTULO ─────────────────────────────────── */
.sb-logo  { text-align:center; font-size:2.8rem; margin-bottom:2px; }
.sb-title {
    text-align:center; font-size:1.2rem; font-weight:800;
    background:linear-gradient(135deg,#60A5FA,#34D399);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:2px;
}
.sb-sub { text-align:center; font-size:.75rem; color:#64748B !important; margin-bottom:16px; }

/* ── DATA PILL ─────────────────────────────────────────────── */
.data-pill {
    background:rgba(96,165,250,.12); border:1px solid rgba(96,165,250,.28);
    border-radius:10px; padding:10px 14px; font-size:.82rem;
    color:#93C5FD !important; margin-top:8px;
}

/* ── SECCIÓN HEADING ───────────────────────────────────────── */
.sec-head {
    font-size:.95rem; font-weight:700; color:#1A6FC4;
    border-left:3px solid #0D9E6E; padding-left:10px; margin:26px 0 14px 0;
}

/* ── LOGIN CARD ────────────────────────────────────────────── */
.login-card {
    background:#FFFFFF; border:1px solid #E2E8F0; border-radius:20px;
    padding:52px 48px; max-width:420px; margin:60px auto 0 auto;
    box-shadow:0 12px 40px rgba(0,0,0,.10);
}

/* ── GEMINI BANNER ─────────────────────────────────────────── */
.gemini-banner {
    background:linear-gradient(135deg,#EFF6FF 0%,#ECFDF5 100%);
    border:1px solid #BFDBFE; border-radius:10px;
    padding:10px 16px; font-size:12.5px; color:#1E40AF; margin-bottom:14px;
}

/* ── BIO-RAD CARDS ─────────────────────────────────────────── */
.biorad-card {
    background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #1A6FC4;
    border-radius:12px; padding:18px 20px; margin-bottom:12px;
    box-shadow:0 2px 8px rgba(0,0,0,.05);
}
.biorad-card-red {
    background:#FFFAFA; border:1px solid #FECACA; border-left:4px solid #E53E3E;
    border-radius:12px; padding:18px 20px; margin-bottom:12px;
    box-shadow:0 2px 12px rgba(229,62,62,.08);
}
.biorad-card-amber {
    background:#FFFDF5; border:1px solid #FDE68A; border-left:4px solid #F59E0B;
    border-radius:12px; padding:18px 20px; margin-bottom:12px;
    box-shadow:0 2px 12px rgba(245,158,11,.08);
}

/* ── TABLAS ────────────────────────────────────────────────── */
table { width:100%; border-collapse:collapse; font-size:.86rem; }
thead tr { background:#F8FAFC; }
th {
    padding:11px 13px; text-align:left; font-weight:700; color:#475569;
    border-bottom:2px solid #E2E8F0; text-transform:uppercase;
    font-size:.72rem; letter-spacing:.06em;
}
td { padding:10px 13px; border-bottom:1px solid #F1F5F9; color:#1C2B3A; }
tr:hover td { background:#F8FAFC; }

/* ── CHAT ──────────────────────────────────────────────────── */
[data-testid="stChatMessage"] {
    background:#FFFFFF !important; border:1px solid #E2E8F0 !important;
    border-radius:14px !important; box-shadow:0 1px 4px rgba(0,0,0,.05) !important;
}

/* ── METRIC WIDGET ─────────────────────────────────────────── */
[data-testid="stMetric"] {
    background:#FFFFFF; border:1px solid #E2E8F0;
    border-radius:12px; padding:16px 14px; box-shadow:0 2px 8px rgba(0,0,0,.05);
}

/* ── EXPANDERS ─────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background:#FFFFFF !important; border:1px solid #E2E8F0 !important;
    border-radius:10px !important;
}

/* ── SCROLLBAR ─────────────────────────────────────────────── */
::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-track { background:#F1F5F9; }
::-webkit-scrollbar-thumb { background:#CBD5E1; border-radius:3px; }
::-webkit-scrollbar-thumb:hover { background:#94A3B8; }
</style>
""", unsafe_allow_html=True)


# ==============================================================
#  BASE DE CONOCIMIENTO BIO-RAD
# ==============================================================
BIORAD_KB = {
    "Glucosa": {
        "producto":   "Liquichek Chemistry Control / Lyphochek Chemistry",
        "grupo":      "Bioquímica básica",
        "causas_comunes": [
            "Evaporación del vial (apertura prolongada o temperatura elevada)",
            "Degradación glucolítica in vitro si el control no se procesa en ≤2 h tras reconstitución",
            "Interferencia por hemólisis severa (libera glucosa eritrocitaria)",
            "Calibración desactualizada o curva de calibración no lineal en el rango del control",
            "Contaminación cruzada con reactivos de otros analitos en analizadores multicanal",
        ],
        "acciones_1_3s": [
            "🔴 No liberar resultados de pacientes hasta resolver la alarma",
            "Repetir el control con un NUEVO vial del mismo lote",
            "Si persiste: repetir con vial de LOTE DIFERENTE para descartar lote defectuoso",
            "Verificar temperatura de almacenamiento (2–8 °C según insert Bio-Rad)",
            "Comprobar fecha de caducidad y tiempo desde reconstitución (máx. 5 días refrigerado)",
            "Recalibrar con estándar trazable IDMS y repetir control",
            "Documentar acción y responsable en el registro de trazabilidad",
        ],
        "acciones_warn": [
            "🟡 Monitoreo estrecho — no bloquear resultados pero aumentar vigilancia",
            "Revisar si hay tendencia en el gráfico Levey-Jennings",
            "Verificar temperatura del baño termostatizado del analizador",
            "Comprobar que el vial se ha mezclado correctamente antes de pipetear",
            "Registrar observación en el libro de incidencias",
        ],
        "causas_deriva": [
            "Deterioro progresivo del reactivo (degradación enzimática)",
            "Deriva del calibrador (recalibrar según protocolo del fabricante)",
            "Fluctuación de temperatura ambiente del laboratorio",
        ],
        "estabilidad_biorad": "Reconstituido: 5 días a 2-8 °C / 30 días a -20 °C",
        "interferencias": "Hemólisis (↑), lipemia severa (↓ GOD-PAP), ácido ascórbico >30 mg/dL (↓)",
        "referencia": "Liquichek Chemistry Control Insert · Bio-Rad cat. 66796 / CLSI EP7-A2",
    },
    "Potasio (K+)": {
        "producto":   "Liquichek Chemistry Control / Liquichek Electrolyte Plus",
        "grupo":      "Bioquímica básica",
        "causas_comunes": [
            "Evaporación del vial (concentra el analito → resultado falsamente elevado)",
            "Contaminación por EDTA (eleva K⁺ falsamente)",
            "Hemólisis in vitro del control (libera K⁺ intracelular)",
            "Interferencia del sodio en electrodos ISE por ruptura de membrana selectiva",
            "Temperatura incorrecta del módulo de electrodos ISE",
        ],
        "acciones_1_3s": [
            "🔴 Verificar que el vial no lleva abierto más de 8 horas",
            "Repetir con vial nuevo — si corrige, el problema era el vial",
            "Revisar el electrodo ISE de potasio (limpieza, membrana, solución de referencia)",
            "Recalibrar el módulo ISE con soluciones estándar trazables",
            "Si persiste: contactar soporte técnico del analizador",
        ],
        "acciones_warn": [
            "Verificar tiempo de apertura del vial de control",
            "Comprobar limpieza del electrodo ISE (ciclo de lavado automático)",
            "Revisar temperatura de la celda de medida (37 °C ± 0,5 °C)",
        ],
        "causas_deriva": [
            "Desgaste progresivo de la membrana del electrodo ISE (vida útil: 3-6 meses)",
            "Acumulación de proteínas en el electrodo",
            "Deriva del calibrador de 2 puntos ISE",
        ],
        "estabilidad_biorad": "Reconstituido: 8 h a temperatura ambiente / 5 días a 2-8 °C",
        "interferencias": "Hemólisis (↑↑), EDTA (↑), heparina litio (efecto mínimo)",
        "referencia": "Liquichek Electrolyte Plus Insert · Bio-Rad · CLSI EP9-A3",
    },
    "Sodio": {
        "producto":   "Liquichek Chemistry Control / Liquichek Electrolyte Plus",
        "grupo":      "Bioquímica básica",
        "causas_comunes": [
            "Pseudohiponatremia por lipemia severa en métodos de llama",
            "Dilución incorrecta del control durante la reconstitución",
            "Electrodo ISE de sodio con membrana deteriorada o contaminada",
        ],
        "acciones_1_3s": [
            "🔴 Repetir control con vial nuevo del mismo lote",
            "Verificar el volumen de reconstitución (agua ultrapura, volumen exacto del insert)",
            "Revisar y limpiar el electrodo ISE de sodio",
            "Recalibrar con solución estándar de NaCl trazable NIST",
        ],
        "acciones_warn": [
            "Revisar que el control se ha mezclado por inversión suave",
            "Verificar temperatura de la celda ISE",
        ],
        "causas_deriva": [
            "Envejecimiento de la membrana del electrodo ISE de sodio",
            "Cambio de lote de reactivo sin recalibración",
        ],
        "estabilidad_biorad": "Reconstituido: 8 h a temperatura ambiente / 5 días a 2-8 °C",
        "interferencias": "Lipemia (↓ métodos fotométricos), hemólisis (efecto mínimo en ISE)",
        "referencia": "Liquichek Electrolyte Plus Insert · Bio-Rad · CLSI EP7-A2",
    },
    "Creatinina": {
        "producto":   "Liquichek Chemistry Control",
        "grupo":      "Bioquímica básica",
        "causas_comunes": [
            "Interferencia por cromógenos de Jaffé (cefalosporinas, acetona, bilirrubina)",
            "Diferencia de método: Jaffé cinético vs enzimático",
            "Calibración no trazable a IDMS genera sesgo",
        ],
        "acciones_1_3s": [
            "🔴 Confirmar que el insert tiene valores para TU método/instrumento",
            "Cambiar a método enzimático si hay interferencia por bilirrubina",
            "Recalibrar con calibrador trazable a IDMS (NIST SRM 967)",
            "Repetir control con vial nuevo",
        ],
        "acciones_warn": [
            "Verificar el método utilizado (Jaffé vs enzimático)",
            "Revisar fecha de caducidad del reactivo Jaffé",
        ],
        "causas_deriva": [
            "Degradación del ácido pícrico en método Jaffé",
            "Deriva del calibrador entre lotes",
        ],
        "estabilidad_biorad": "Reconstituido: 5 días a 2-8 °C",
        "interferencias": "Bilirrubina >10 mg/dL (↑ Jaffé), cefalosporinas (↑), acetona (↑)",
        "referencia": "Liquichek Chemistry Control Insert · Bio-Rad · CLSI EP6-A",
    },
    "ALT (Transaminasa)": {
        "producto":   "Liquichek Chemistry Control / Lyphochek Chemistry",
        "grupo":      "Enzimas hepáticas",
        "causas_comunes": [
            "Temperatura de incubación incorrecta (muy sensible a T°)",
            "Degradación enzimática por ciclos de congelación/descongelación",
            "Longitud de onda del fotómetro fuera de tolerancia (340 nm para NADH)",
            "Reactivo de piridoxal fosfato (P-5-P) faltante o degradado",
        ],
        "acciones_1_3s": [
            "🔴 Verificar temperatura del baño termostatizado (37,0 °C ± 0,1 °C)",
            "Repetir con vial nuevo — la actividad enzimática es sensible al manejo",
            "Comprobar que el reactivo contiene piridoxal fosfato (P-5-P) activado",
            "Verificar longitud de onda del espectrofotómetro",
            "Si ALT y AST fallan simultáneamente: sospechar problema de temperatura",
            "Recalibrar si no se ha realizado en las últimas 24 h",
        ],
        "acciones_warn": [
            "Comprobar temperatura del módulo fotométrico",
            "Verificar mezcla correcta del vial antes de pipetear",
            "Controlar la absorbancia del blanco de reactivo (no debe superar 1.5 AU)",
        ],
        "causas_deriva": [
            "Deterioro progresivo del coenzima NADH (sensible a luz UV)",
            "Fluctuación de temperatura del módulo termostatizado",
            "Cambio de lote de reactivo sin ajuste de valores objetivo",
        ],
        "estabilidad_biorad": "Reconstituido: 5 días a 2-8 °C (la actividad enzimática decrece con el tiempo)",
        "interferencias": "Hemólisis severa (↑), lipemia >500 mg/dL (variable), bilirrubina >20 mg/dL (↑ leve)",
        "referencia": "Liquichek Chemistry Control Insert · Bio-Rad · IFCC EP9 / CLSI EP15-A3",
    },
    "AST": {
        "producto":   "Liquichek Chemistry Control / Lyphochek Chemistry",
        "grupo":      "Enzimas hepáticas",
        "causas_comunes": [
            "Hemólisis in vitro (AST eritrocitaria es 15× mayor que en plasma)",
            "Temperatura incorrecta (cada grado cambia la actividad ~7%)",
            "Piridoxal fosfato ausente o degradado en el reactivo",
        ],
        "acciones_1_3s": [
            "🔴 Inspeccionar el vial — ¿hay hemólisis visible (color rosado)?",
            "Repetir con vial nuevo sin hemólisis",
            "Verificar temperatura del baño (37,0 °C ± 0,1 °C)",
            "Recalibrar si ALT también falla simultáneamente",
        ],
        "acciones_warn": [
            "Revisar manejo del vial (mezclar por inversión suave)",
            "Verificar absorbancia inicial del blanco de reactivo",
        ],
        "causas_deriva": [
            "Degradación del NADH por exposición a luz",
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
            "Temperatura de reacción incorrecta (sensible a ±0,5 °C)",
            "pH del reactivo fuera de rango (óptimo 7,9–8,2)",
            "Evaporación del substrato por mal sellado",
        ],
        "acciones_1_3s": [
            "🔴 Verificar temperatura del módulo fotométrico",
            "Comprobar pH del tampón del reactivo",
            "Repetir con vial nuevo y reactivo recién preparado",
        ],
        "acciones_warn": [
            "Revisar fecha de preparación del reactivo",
            "Verificar ausencia de precipitados en el reactivo",
        ],
        "causas_deriva": [
            "Hidrólisis espontánea del substrato en el reactivo abierto",
            "Fluctuación de pH por exposición al CO₂ ambiental",
        ],
        "estabilidad_biorad": "Reconstituido: 5 días a 2-8 °C",
        "interferencias": "Hemólisis leve (mínimo), lipemia >1000 mg/dL (↑)",
        "referencia": "Liquichek Chemistry Control Insert · Bio-Rad · ECCLS / DGKC",
    },
    "LDH": {
        "producto":   "Liquichek Chemistry Control / Lyphochek Chemistry",
        "grupo":      "Enzimas hepáticas",
        "causas_comunes": [
            "Hemólisis (LDH eritrocitaria es 160× mayor que en plasma)",
            "Temperatura crítica: cada °C modifica la actividad ~8–10%",
            "Inhibición por exceso de piruvato en método inverso",
        ],
        "acciones_1_3s": [
            "🔴 Inspeccionar el vial — hemólisis es la causa más frecuente",
            "Repetir con vial nuevo sin hemólisis",
            "Verificar temperatura del módulo (37,0 °C)",
        ],
        "acciones_warn": [
            "Verificar que el reactivo no tiene precipitados (NADH precipita en frío)",
            "Atemperar el reactivo antes de su uso",
        ],
        "causas_deriva": [
            "Degradación del NADH por congelación repetida",
            "Cambio de isoenzimas en el control por lote diferente",
        ],
        "estabilidad_biorad": "Reconstituido: 24 h a 2-8 °C (muy lábil — usar el mismo día)",
        "interferencias": "Hemólisis (↑↑↑ crítico), oxalato (↓), urea elevada (↓ leve)",
        "referencia": "Liquichek Chemistry Control Insert · Bio-Rad · IFCC/DGKC",
    },
    "Colesterol": {
        "producto":   "Liquichek Lipid Control / Lyphochek Lipid",
        "grupo":      "Lípidos",
        "causas_comunes": [
            "Diferencia de método: CHOD-PAP vs Abell-Kendall",
            "Interferencia por bilirrubina >5 mg/dL (inhibe la peroxidasa)",
            "Calibrador no trazable a NIST SRM 1951c",
        ],
        "acciones_1_3s": [
            "🔴 Verificar que los valores del insert corresponden a TU método",
            "Repetir con vial nuevo del mismo lote",
            "Recalibrar con calibrador trazable a NIST SRM 1951c",
        ],
        "acciones_warn": [
            "Verificar la mezcla del vial (colesterol puede precipitar)",
            "Confirmar que el blanco de reactivo está dentro del rango de linealidad",
        ],
        "causas_deriva": [
            "Degradación de la colesterol oxidasa (CHOD) por temperatura o luz",
            "Cambio de lote de reactivo",
        ],
        "estabilidad_biorad": "Reconstituido: 7 días a 2-8 °C",
        "interferencias": "Bilirrubina >5 mg/dL (↓ CHOD-PAP), hemólisis (↑ leve), ácido ascórbico (↓)",
        "referencia": "Liquichek Lipid Control Insert · Bio-Rad · CDC/NHLBI",
    },
    "Triglicéridos": {
        "producto":   "Liquichek Lipid Control / Lyphochek Lipid",
        "grupo":      "Lípidos",
        "causas_comunes": [
            "Glicerol endógeno libre en el control",
            "Interferencia por hemólisis (inhibe la peroxidasa)",
        ],
        "acciones_1_3s": [
            "🔴 Verificar si el insert especifica valores con/sin corrección por glicerol",
            "Repetir control con vial nuevo",
            "Recalibrar con calibrador trazable a NIST SRM 1951c",
        ],
        "acciones_warn": [
            "Verificar que el control se ha atemperado correctamente",
            "Revisar el tiempo de incubación del reactivo",
        ],
        "causas_deriva": [
            "Degradación de la lipasa pancreática en el reactivo",
            "Acumulación de glicerol libre en el vial abierto",
        ],
        "estabilidad_biorad": "Reconstituido: 7 días a 2-8 °C",
        "interferencias": "Hemólisis (↓ peroxidasa), glicerol libre (↑), bilirrubina >5 mg/dL (↓)",
        "referencia": "Liquichek Lipid Control Insert · Bio-Rad",
    },
    "HDL-Colesterol": {
        "producto":   "Liquichek Lipid Control",
        "grupo":      "Lípidos",
        "causas_comunes": [
            "Efecto matriz del control en métodos de precipitación directa",
            "Interferencia de VLDL elevadas con métodos homogéneos",
            "Calibración incorrecta del método homogéneo directo",
        ],
        "acciones_1_3s": [
            "🔴 Verificar los valores del insert para TU método específico de HDL",
            "Repetir con vial nuevo",
            "Recalibrar — los métodos de HDL directo requieren calibración frecuente",
        ],
        "acciones_warn": [
            "Confirmar que el tipo de método coincide con los valores del insert",
            "Verificar la integridad del blanco de HDL",
        ],
        "causas_deriva": [
            "Cambio de lote de reactivo sin recalibración",
        ],
        "estabilidad_biorad": "Reconstituido: 7 días a 2-8 °C",
        "interferencias": "Triglicéridos >400 mg/dL (↑ falso en directo), bilirrubina >10 mg/dL (↑)",
        "referencia": "Liquichek Lipid Control Insert · Bio-Rad · CDC Lipid Standardization",
    },
    "TSH": {
        "producto":   "Lyphochek Immunoassay Plus Control",
        "grupo":      "Inmunoensayo hormonal",
        "causas_comunes": [
            "Anticuerpos heterófilos (HAMA) que interfieren en ensayos sandwich",
            "Degradación por ciclos de congelación/descongelación inadecuados",
            "Variabilidad inter-ensayo elevada (CV% típico 5-8%)",
            "Reactividad cruzada con LH, FSH",
        ],
        "acciones_1_3s": [
            "🔴 Verificar que el control está asignado a TU plataforma de inmunoensayo",
            "Repetir con vial nuevo",
            "Revisar número de ciclos de congelación/descongelación (máx. 3)",
            "Verificar calibración del inmunoensayo (los kits se calibran en lote)",
        ],
        "acciones_warn": [
            "Revisar número de lote del reactivo vs calibración activa",
            "Verificar que el cartucho/reactivo no está próximo a caducidad",
        ],
        "causas_deriva": [
            "Cambio de lote de reactivo (recalibrar obligatoriamente)",
            "Degradación gradual del conjugado enzimático",
        ],
        "estabilidad_biorad": "Reconstituido: 30 días a 2-8 °C (Lyphochek)",
        "interferencias": "HAMA (↑↑), biotina >20 ng/mL (↓), hemólisis severa (variable)",
        "referencia": "Lyphochek Immunoassay Plus Control Insert · Bio-Rad · CLSI EP15-A3",
    },
    "T4 Libre (FT4)": {
        "producto":   "Lyphochek Immunoassay Plus Control",
        "grupo":      "Inmunoensayo hormonal",
        "causas_comunes": [
            "Interferencia por proteínas de unión (TBG, albúmina)",
            "Dilución incorrecta del control liofilizado",
            "Variabilidad entre plataformas (valores método-dependientes)",
        ],
        "acciones_1_3s": [
            "🔴 Confirmar que los valores objetivo son específicos para TU analizador",
            "Repetir con vial nuevo reconstituido correctamente",
            "Recalibrar el inmunoensayo de FT4",
        ],
        "acciones_warn": [
            "Comprobar el volumen de reconstitución exacto",
            "Verificar que se ha mezclado por inversión suave (no vortex)",
        ],
        "causas_deriva": [
            "Cambio de lote de reactivo (FT4 muy sensible a variaciones de calibración)",
            "Degradación por temperatura de almacenamiento inadecuada",
        ],
        "estabilidad_biorad": "Reconstituido: 30 días a 2-8 °C (Lyphochek)",
        "interferencias": "Biotina >20 ng/mL (↓), HAMA (variable), heparina IV (↑ artefactual)",
        "referencia": "Lyphochek Immunoassay Plus Control Insert · Bio-Rad",
    },
    "Hemoglobina": {
        "producto":   "Lyphochek Hematology / Liquichek Hematology",
        "grupo":      "Hematología",
        "causas_comunes": [
            "Envejecimiento del control (eritrocitos se fragmentan con el tiempo)",
            "Temperatura de almacenamiento incorrecta",
            "Variabilidad entre analizadores de hematología",
        ],
        "acciones_1_3s": [
            "🔴 Verificar la fecha de caducidad del vial abierto (5-7 días según insert)",
            "Repetir con vial nuevo dentro de fecha",
            "Recalibrar con material de referencia del fabricante del analizador",
        ],
        "acciones_warn": [
            "Verificar temperatura de almacenamiento (2-8 °C, NO congelar)",
            "Invertir suavemente 8-10 veces antes de analizar",
            "Estabilización de 15 min a T° ambiente tras sacar de nevera",
        ],
        "causas_deriva": [
            "Fragmentación progresiva de eritrocitos en el control envejecido",
            "Variación del canal HGB por suciedad en la cubeta",
        ],
        "estabilidad_biorad": "Abierto: 5-7 días a 2-8 °C / No congelar",
        "interferencias": "Lipemia severa (↑ HGB fotométrico), ictericia severa (↑ HGB)",
        "referencia": "Lyphochek Hematology Control Insert · Bio-Rad · CLSI H26-A2",
    },
    "Calcio": {
        "producto":   "Liquichek Chemistry Control",
        "grupo":      "Bioquímica básica",
        "causas_comunes": [
            "Interferencia por EDTA (quelante del calcio)",
            "pH del control fuera de rango",
            "Interferencia por magnesio elevado en método de o-cresolftaleína",
            "Evaporación del vial (concentra el calcio)",
        ],
        "acciones_1_3s": [
            "🔴 Descartar contaminación con EDTA",
            "Repetir con vial nuevo",
            "Verificar el pH del reactivo de o-cresolftaleína",
            "Recalibrar con calibrador trazable a SRM NIST 956c",
        ],
        "acciones_warn": [
            "Verificar tiempo de apertura del vial de control",
            "Comprobar temperatura de incubación (37 °C)",
        ],
        "causas_deriva": [
            "Degradación del indicador o-cresolftaleína",
            "Cambio de lote de reactivo con diferente concentración de indicador",
        ],
        "estabilidad_biorad": "Reconstituido: 5 días a 2-8 °C",
        "interferencias": "EDTA (↓↓↓ crítico), magnesio elevado (↑ leve), hemólisis (↑ leve)",
        "referencia": "Liquichek Chemistry Control Insert · Bio-Rad · CLSI EP7-A2",
    },
}

GRUPOS_ANALITICOS = {
    "Bioquímica básica":     ["Glucosa","Potasio (K+)","Sodio","Creatinina","Calcio"],
    "Enzimas hepáticas":     ["ALT (Transaminasa)","AST","GGT","LDH"],
    "Lípidos":               ["Colesterol","Triglicéridos","HDL-Colesterol"],
    "Inmunoensayo hormonal": ["TSH","T4 Libre (FT4)"],
    "Hematología":           ["Hemoglobina"],
}

def buscar_kb(analito, estado):
    if analito in BIORAD_KB: return BIORAD_KB[analito]
    an_norm = analito.lower()
    for key in BIORAD_KB:
        if an_norm in key.lower() or key.lower() in an_norm: return BIORAD_KB[key]
    return None

def render_kb_panel(analito, estado, regla, nivel):
    kb = buscar_kb(analito, estado)
    nivel_label = NIVELES.get(nivel, NIVELES["N"])["label"]
    card_class  = "biorad-card-red" if estado=="Rojo" else "biorad-card-amber" if estado=="Ámbar" else "biorad-card"
    if kb is None:
        st.markdown(
            f'<div class="{card_class}"><b>📋 Bio-Rad KB:</b> No hay ficha específica para <b>{analito}</b>. '
            f'Consulta el insert en <a href="https://myeinserts-app.qcnet.com/home" target="_blank">myeInserts QCNet</a>.</div>',
            unsafe_allow_html=True); return
    ico = "🔴" if estado=="Rojo" else "🟡"
    st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
    st.markdown(f"#### {ico} Guía Bio-Rad — **{analito}** · {nivel_label} · Regla `{regla}`\n*Producto: {kb['producto']} · Grupo: {kb['grupo']}*")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🔍 Causas más probables:**")
        for c in kb["causas_comunes"]: st.markdown(f"- {c}")
        if estado=="Ámbar" and any(r in regla for r in ["10_x","4_1s","2_2s"]):
            st.markdown("**📉 Causas de deriva:**")
            for c in kb.get("causas_deriva",[]): st.markdown(f"- {c}")
    with col2:
        acciones = kb["acciones_1_3s"] if estado=="Rojo" else kb["acciones_warn"]
        st.markdown("**✅ Acciones correctivas:**")
        for a in acciones: st.markdown(f"- {a}")
    st.markdown(
        f"**⚠️ Interferencias:** {kb['interferencias']}\n\n"
        f"**🧪 Estabilidad:** {kb['estabilidad_biorad']}\n\n"
        f"**📖 Referencia:** {kb['referencia']}")
    st.markdown(
        f'<small>🔗 <a href="https://myeinserts-app.qcnet.com/home" target="_blank">myeInserts QCNet Bio-Rad</a></small>',
        unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================
#  CONSTANTES DE NIVELES
# ==============================================================
NIVELES = {
    "N":  {"label":"Normal",         "pill":"nivel-N",  "icon":"🔵"},
    "PB": {"label":"Patológico Bajo", "pill":"nivel-PB", "icon":"🟡"},
    "PA": {"label":"Patológico Alto", "pill":"nivel-PA", "icon":"🔴"},
}

def nivel_badge(codigo):
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
    "Cuando hay alarma, menciona causas probables según el insert Bio-Rad y acciones correctivas. "
    "NUNCA respondas de forma genérica. Respondes en español, de forma concisa y técnica. "
    "Usas Markdown. Fórmula Z-Score: Z = (x − μ) / σ."
)
GEMINI_CFG = {"temperature":0.2,"max_output_tokens":2048,"top_p":0.85}

def get_api_key():
    return (st.secrets.get("gemini",{}).get("api_key") or
            st.secrets.get("GEMINI_API_KEY","") or os.environ.get("GEMINI_API_KEY",""))


# ==============================================================
#  2. AUTENTICACIÓN
# ==============================================================
def get_credentials():
    try: return st.secrets["auth"]["user"], st.secrets["auth"]["password"]
    except KeyError:
        st.error("⚠️ Crea `.streamlit/secrets.toml` con [auth] user y password."); st.stop()

VALID_USER, VALID_PASS = get_credentials()

def render_login():
    st.markdown("""<div class="login-card">
        <div style="font-size:3rem;text-align:center">🔬</div>
        <div style="text-align:center;font-size:1.8rem;font-weight:800;color:#1A6FC4;margin-bottom:4px">AIQC</div>
        <div style="text-align:center;font-size:.86rem;color:#64748B;margin-bottom:28px">
            Artificial Intelligence for Quality Control · v4.9
        </div></div>""", unsafe_allow_html=True)
    _, mid, _ = st.columns([1,1.8,1])
    with mid:
        st.markdown("<br>", unsafe_allow_html=True)
        user = st.text_input("Usuario", placeholder="admin", key="_u")
        pwd  = st.text_input("Contraseña", type="password", placeholder="••••••", key="_p")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Acceder al sistema →", use_container_width=True, type="primary"):
            if user==VALID_USER and pwd==VALID_PASS:
                st.session_state["auth"]=True; st.rerun()
            else: st.error("Credenciales incorrectas.")

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

def load_acciones(con): return {r[0]:bool(r[1]) for r in con.execute("SELECT clave,hecha FROM acciones").fetchall()}
def save_accion(con,clave,hecha):
    con.execute("INSERT OR REPLACE INTO acciones VALUES (?,?,datetime('now'))",(clave,int(hecha))); con.commit()

if "db_con" not in st.session_state: st.session_state["db_con"]=init_db()
db_con = st.session_state["db_con"]


# ==============================================================
#  4. DATOS DEMO
# ==============================================================
NIVELES_DEMO = {
    "Potasio (K+)":       {"N":(4.5,0.15),"PB":(2.8,0.12),"PA":(6.2,0.18)},
    "ALT (Transaminasa)": {"N":(35.0,2.5),"PB":(12.0,1.5),"PA":(120.0,8.0)},
}

@st.cache_data(show_spinner=False)
def build_demo(ref_date=""):
    np.random.seed(2026)
    today = pd.Timestamp(ref_date).replace(hour=0,minute=0,second=0,microsecond=0)
    dates = [today-timedelta(days=29-i) for i in range(30)]
    rows  = []
    for analito,niveles in NIVELES_DEMO.items():
        for nivel_cod,(media,sd) in niveles.items():
            for i,d in enumerate(dates):
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
    df_n={_norm(c):c for c in df.columns}; rename={}
    for interno,sins in COL_SYNONYMS.items():
        for s in sins:
            if s in df_n: rename[df_n[s]]=interno; break
        if interno not in rename.values():
            for cn,co in df_n.items():
                if any(s in cn or cn in s for s in sins): rename[co]=interno; break
    df2=df.rename(columns=rename)
    obligatorias=["Fecha","Analito","Valor","Media_Objetivo","SD_Objetivo"]
    faltan=[c for c in obligatorias if c not in df2.columns]
    if faltan: return None, f"Columnas no encontradas: {', '.join(faltan)}."
    if "Nivel" not in df2.columns: df2["Nivel"]="N"
    if "Lote"  not in df2.columns: df2["Lote"]="N/A"
    df2["Fecha"]=pd.to_datetime(df2["Fecha"],dayfirst=True,errors="coerce")
    df2["Valor"]=pd.to_numeric(df2["Valor"],errors="coerce")
    df2["Media_Objetivo"]=pd.to_numeric(df2["Media_Objetivo"],errors="coerce")
    df2["SD_Objetivo"]=pd.to_numeric(df2["SD_Objetivo"],errors="coerce")
    nivel_map={"n":"N","normal":"N","nivel 1":"N","nivel1":"N","n1":"N","1":"N",
               "pb":"PB","patologico bajo":"PB","bajo":"PB","nivel 2":"PB","n2":"PB","2":"PB",
               "pa":"PA","patologico alto":"PA","alto":"PA","nivel 3":"PA","n3":"PA","3":"PA"}
    df2["Nivel"]=df2["Nivel"].astype(str).str.lower().str.strip().map(lambda x:nivel_map.get(x,"N"))
    df2=df2.dropna(subset=obligatorias)
    if df2.empty: return None,"Sin filas válidas."
    return df2[obligatorias+["Nivel","Lote"]].reset_index(drop=True),""

def leer_archivo(uploaded):
    name=uploaded.name.lower()
    try:
        raw=pd.read_csv(uploaded,sep=None,engine="python") if name.endswith(".csv") else pd.read_excel(uploaded)
        return normalizar_df(raw)
    except Exception as e: return None,f"Error: {e}"


# ==============================================================
#  6. WESTGARD
# ==============================================================
REGLAS_DESC="1_3s: ±3SD → Rojo | 2_2s: 2 consec ±2SD → Rojo | 4_1s: 4 consec ±1SD → Ámbar | 10_x: 10 consec mismo lado → Ámbar"

def evaluar_westgard(serie):
    df=serie.copy().sort_values("Fecha").reset_index(drop=True)
    df["Z_Score"]=(df["Valor"]-df["Media_Objetivo"])/df["SD_Objetivo"]
    df["Regla_Violada"]="—"; df["Score_Riesgo"]=0; df["Estado"]="Verde"
    for i in range(len(df)):
        z=df.at[i,"Z_Score"]
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
TEA_DEFAULT=15.0

def calcular_sigma(df_analito,tea_pct):
    if df_analito.empty: return {}
    media=df_analito["Media_Objetivo"].iloc[0]; sd=df_analito["SD_Objetivo"].iloc[0]; vals=df_analito["Valor"]
    cv_pct=(sd/media)*100 if media!=0 else 0
    sesgo_pct=abs((vals.mean()-media)/media)*100 if media!=0 else 0
    sigma=(tea_pct-sesgo_pct)/cv_pct if cv_pct>0 else 0
    if sigma>=6:   cat="🏆 Clase Mundial"; color="#0D9E6E"
    elif sigma>=4: cat="✅ Buena calidad"; color="#1A6FC4"
    elif sigma>=3: cat="⚠️ Aceptable";    color="#F59E0B"
    else:          cat="🔴 Revisar método";color="#E53E3E"
    return {"sigma":round(sigma,2),"cv_pct":round(cv_pct,2),"sesgo_pct":round(sesgo_pct,2),
            "tea_pct":tea_pct,"categoria":cat,"color":color,"media":round(media,3),"sd":round(sd,4),"n":len(vals)}


# ==============================================================
#  8. LEVEY-JENNINGS
# ==============================================================
def build_lj_figure(df_series,analito,nivel):
    u=df_series.iloc[-1]; m=u["Media_Objetivo"]; sd=u["SD_Objetivo"]
    nivel_label=NIVELES.get(nivel,NIVELES["N"])["label"]
    fig=go.Figure()
    for y0,y1,col in [(m+2*sd,m+3*sd,"rgba(229,62,62,.10)"),(m-3*sd,m-2*sd,"rgba(229,62,62,.10)"),
                       (m+sd,m+2*sd,"rgba(245,158,11,.08)"),(m-2*sd,m-sd,"rgba(245,158,11,.08)"),
                       (m-sd,m+sd,"rgba(13,158,110,.06)")]:
        fig.add_hrect(y0=y0,y1=y1,fillcolor=col,line_width=0)
    for y_v,color,width,dash,name in [
        (m,"#0D9E6E",2.0,"solid","Media"),(m+sd,"#94A3B8",1.0,"dash","+1 SD"),(m-sd,"#94A3B8",1.0,"dash","−1 SD"),
        (m+2*sd,"#F59E0B",1.4,"dash","+2 SD"),(m-2*sd,"#F59E0B",1.4,"dash","−2 SD"),
        (m+3*sd,"#E53E3E",1.8,"dot","+3 SD"),(m-3*sd,"#E53E3E",1.8,"dot","−3 SD"),
    ]:
        fig.add_hline(y=y_v,line_color=color,line_width=width,line_dash=dash,
                      annotation_text=name,annotation_position="right",
                      annotation_font=dict(color=color,size=10,family="Inter"))
    fig.add_trace(go.Scatter(x=df_series["Fecha"],y=df_series["Valor"],
                             mode="lines",line=dict(color="#CBD5E1",width=1.5),showlegend=False,hoverinfo="skip"))
    for estado,color in [("Verde","#0D9E6E"),("Ámbar","#F59E0B"),("Rojo","#E53E3E")]:
        sub=df_series[df_series["Estado"]==estado]
        if sub.empty: continue
        fig.add_trace(go.Scatter(x=sub["Fecha"],y=sub["Valor"],mode="markers",name=estado,
                                 marker=dict(size=9,color=color,line=dict(color="#FFFFFF",width=1.5))))
    fig.update_layout(
        template="plotly_white",
        title=dict(text=f"Levey-Jennings — {analito} · {nivel_label}",
                   font=dict(size=13,color="#1C2B3A",family="Inter")),
        paper_bgcolor="#FFFFFF",plot_bgcolor="#FAFBFC",
        font=dict(color="#475569",family="Inter"),
        legend=dict(orientation="h",y=1.08,x=1,xanchor="right"),
        xaxis=dict(gridcolor="#F1F5F9",linecolor="#E2E8F0",tickformat="%d %b",title="Fecha"),
        yaxis=dict(gridcolor="#F1F5F9",linecolor="#E2E8F0",title="Valor"),
        height=380,width=760,margin=dict(l=10,r=110,t=55,b=40))
    return fig

def fig_to_png_bytes(fig):
    try: return fig.to_image(format="png",scale=2)
    except: return None


# ==============================================================
#  9. PDF
# ==============================================================
def generar_pdf(df_all,analitos,fuente):
    pdf=FPDF(); pdf.set_auto_page_break(auto=True,margin=15); pdf.add_page()
    pdf.set_fill_color(26,111,196); pdf.rect(0,0,210,36,"F")
    pdf.set_font("Helvetica","B",18); pdf.set_text_color(255,255,255); pdf.ln(8)
    pdf.cell(0,10,"AIQC – Informe de Incidencias de Calidad",ln=True,align="C")
    pdf.set_font("Helvetica","",9); pdf.set_text_color(220,235,255)
    pdf.cell(0,6,f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}  |  Fuente: {fuente}  |  Analitos: {', '.join(analitos)}",ln=True,align="C")
    pdf.ln(10)
    niveles_disponibles=sorted(df_all["Nivel"].unique()) if "Nivel" in df_all.columns else ["N"]

    def sec(txt):
        pdf.set_font("Helvetica","B",12); pdf.set_text_color(26,111,196)
        pdf.cell(0,8,txt,ln=True)
        pdf.set_draw_color(13,158,110); pdf.line(10,pdf.get_y(),200,pdf.get_y()); pdf.ln(3)

    sec("1. Resumen Ejecutivo por Nivel de Control")
    for niv in niveles_disponibles:
        frames=[evaluar_westgard(df_all[(df_all["Analito"]==an)&(df_all["Nivel"]==niv)].copy()) for an in analitos]
        df_ev=pd.concat([f for f in frames if not f.empty])
        if df_ev.empty: continue
        total=len(df_ev); rojos=int((df_ev["Estado"]=="Rojo").sum())
        ambar=int((df_ev["Estado"]=="Ámbar").sum()); ok=int((df_ev["Estado"]=="Verde").sum())
        pdf.set_font("Helvetica","B",10); pdf.set_text_color(28,43,58)
        pdf.cell(0,7,f"Nivel: {NIVELES.get(niv,NIVELES['N'])['label']}",ln=True)
        pdf.set_font("Helvetica","",9)
        pdf.cell(0,6,f"  Total: {total}  |  Verde: {ok} ({100*ok//total if total else 0}%)  |  Ambar: {ambar}  |  Rojo: {rojos}",ln=True)
        pdf.ln(2)

    sec("2. Estado por Analito y Nivel  [Z = (x - media) / SD]")
    pdf.set_font("Helvetica","",8); pdf.set_text_color(80,80,80)
    pdf.cell(0,5,REGLAS_DESC,ln=True); pdf.ln(2)
    col_w=[40,26,20,22,22,26,22,20]; hdrs=["Analito","Nivel","Valor","Z-Score","Score","Regla","Estado","N pts"]
    pdf.set_fill_color(240,242,245); pdf.set_text_color(71,85,105); pdf.set_font("Helvetica","B",8)
    for w,h in zip(col_w,hdrs): pdf.cell(w,8,h,border=1,fill=True)
    pdf.ln()
    for an in analitos:
        for niv in niveles_disponibles:
            sub=evaluar_westgard(df_all[(df_all["Analito"]==an)&(df_all["Nivel"]==niv)].copy())
            if sub.empty: continue
            u=sub.iloc[-1]; niv_label=NIVELES.get(niv,NIVELES["N"])["label"]
            if u["Estado"]=="Rojo":    pdf.set_fill_color(254,226,226); pdf.set_text_color(153,27,27)
            elif u["Estado"]=="Ámbar": pdf.set_fill_color(254,243,199); pdf.set_text_color(146,64,14)
            else:                       pdf.set_fill_color(209,250,229); pdf.set_text_color(6,95,70)
            pdf.set_font("Helvetica","",8)
            for w,v in zip(col_w,[an[:22],niv_label[:14],str(u["Valor"]),f"{u['Z_Score']:+.2f}",
                                   f"{int(u['Score_Riesgo'])}/100",u["Regla_Violada"],u["Estado"],str(len(sub))]):
                pdf.cell(w,7,str(v),border=1,fill=True)
            pdf.ln()
    pdf.ln(5)

    sec("3. Graficos Levey-Jennings por Analito y Nivel")
    for an in analitos:
        for niv in niveles_disponibles:
            sub_ev=evaluar_westgard(df_all[(df_all["Analito"]==an)&(df_all["Nivel"]==niv)].copy())
            if sub_ev.empty: continue
            fig=build_lj_figure(sub_ev,an,niv); png=fig_to_png_bytes(fig)
            niv_label=NIVELES.get(niv,NIVELES["N"])["label"]
            if png:
                tmp=f"/tmp/lj_{an.replace(' ','_').replace('(','').replace(')','_')}_{niv}.png"
                open(tmp,"wb").write(png)
                pdf.set_font("Helvetica","B",10); pdf.set_text_color(28,43,58)
                pdf.cell(0,7,f"{an} — Nivel: {niv_label}",ln=True)
                pdf.image(tmp,x=10,w=190); pdf.ln(4)
    pdf.ln(3)

    sec("4. Guia Bio-Rad de Acciones Correctivas")
    pdf.set_font("Helvetica","",9); pdf.set_text_color(28,43,58)
    alarmas=set()
    for an in analitos:
        for niv in niveles_disponibles:
            sub=evaluar_westgard(df_all[(df_all["Analito"]==an)&(df_all["Nivel"]==niv)].copy())
            if sub.empty: continue
            u=sub.iloc[-1]
            if u["Estado"]!="Verde" and an not in alarmas:
                alarmas.add(an); kb=buscar_kb(an,u["Estado"])
                if not kb: continue
                niv_label=NIVELES.get(niv,NIVELES["N"])["label"]
                pdf.set_font("Helvetica","B",10)
                pdf.set_text_color(153,27,27) if u["Estado"]=="Rojo" else pdf.set_text_color(146,64,14)
                pdf.cell(0,7,f"{'Rojo' if u['Estado']=='Rojo' else 'Ambar'} — {an} [{niv_label}] — Regla {u['Regla_Violada']}",ln=True)
                pdf.set_font("Helvetica","",8); pdf.set_text_color(28,43,58)
                pdf.cell(0,5,f"Producto: {kb['producto']}",ln=True)
                pdf.set_font("Helvetica","B",8); pdf.cell(0,5,"Causas:",ln=True)
                pdf.set_font("Helvetica","",8)
                for c in kb["causas_comunes"][:3]: pdf.multi_cell(0,5,f"  - {c}")
                pdf.set_font("Helvetica","B",8); pdf.cell(0,5,"Acciones:",ln=True)
                pdf.set_font("Helvetica","",8)
                for a in (kb["acciones_1_3s"] if u["Estado"]=="Rojo" else kb["acciones_warn"])[:4]:
                    pdf.multi_cell(0,5,f"  - {a.replace('🔴','').replace('🟡','').strip()}")
                pdf.cell(0,5,f"Ref: {kb['referencia']}",ln=True); pdf.ln(3)
    if not alarmas:
        pdf.set_font("Helvetica","I",9); pdf.set_text_color(6,95,70)
        pdf.cell(0,7,"Sin alarmas activas.",ln=True)
    pdf.ln(4)
    pdf.set_draw_color(226,232,240); pdf.line(10,pdf.get_y(),200,pdf.get_y()); pdf.ln(2)
    pdf.set_font("Helvetica","I",8); pdf.set_text_color(100,116,139)
    pdf.cell(0,5,"AIQC v4.9 · Powered by Bio-Rad KB · Uso interno del laboratorio",ln=True,align="C")
    return bytes(pdf.output())


# ==============================================================
#  10. ASISTENTE IA GEMINI
# ==============================================================
MAX_TURNS=10

def ia_responde_gemini(pregunta,historial,df_all,analitos_ls,f_min,f_max):
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
            kb=buscar_kb(an,u["Estado"]); kb_txt=""
            if kb and u["Estado"]!="Verde":
                kb_txt=(f"\n  - Bio-Rad causas: {'; '.join(kb['causas_comunes'][:2])}"
                        f"\n  - Bio-Rad acciones: {'; '.join((kb['acciones_1_3s'] if u['Estado']=='Rojo' else kb['acciones_warn'])[:2])}")
            resumen.append(
                f"• {an} | Nivel: {niv_label}\n"
                f"  - Valor: {u['Valor']} | Media: {u['Media_Objetivo']} | SD: {u['SD_Objetivo']}\n"
                f"  - Z = {z_calc:+.3f} | Estado: {u['Estado']} | Regla: {u['Regla_Violada']} | Score: {int(u['Score_Riesgo'])}/100\n"
                f"  - Sigma: {sig.get('sigma','N/A')}σ | CV: {sig.get('cv_pct','N/A')}% | Sesgo: {sig.get('sesgo_pct','N/A')}%{kb_txt}")
    contexto=(f"=== DATOS REALES ({f_min} → {f_max}) ===\n{chr(10).join(resumen)}\n\n"
              f"=== REGLAS WESTGARD ===\n{REGLAS_DESC}\n\n"
              f"=== PREGUNTA ===\n{pregunta}")
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
    st.markdown('<div class="sb-logo">🔬</div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-title">AIQC</div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-sub">Quality Control · v4.9 · Bio-Rad KB</div>', unsafe_allow_html=True)
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
    nivel_sel_label=st.selectbox("Nivel de control",options=list(nivel_options.keys()),key="sel_nivel",
                                  help="N = Normal · PB = Patológico Bajo · PA = Patológico Alto")
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

ESTADO_CLS={"Verde":"estado-verde","Ámbar":"estado-ambar","Rojo":"estado-rojo"}


# ==============================================================
#  13. CABECERA — gradiente azul→verde
# ==============================================================
estado_actual=ultima["Estado"] if ultima is not None else "Verde"

st.markdown(f"""
<div class="aiqc-header">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px">
    <div>
      <h2>🔬 AIQC – Control de Calidad</h2>
      <div class="meta">
        <b>Analito:</b> {analito} &nbsp;·&nbsp;
        {nivel_badge(nivel_activo)} &nbsp;·&nbsp;
        <b>Período:</b> {f_min.strftime('%d/%m/%Y')} → {f_max.strftime('%d/%m/%Y')}
        &nbsp;·&nbsp; <b>Fuente:</b> {data_src}
      </div>
    </div>
    <div style="font-size:1.1rem">{estado_badge(estado_actual)}</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================
#  14. TABS
# ==============================================================
tab_dash,tab_sigma,tab_biorad,tab_chat,tab_log=st.tabs([
    "📊  Dashboard","📈  Sigma Metrics","📋  Guía Bio-Rad","🤖  Asistente IA","📝  Registro",
])


# ── TAB 1: DASHBOARD ─────────────────────────────────────────
with tab_dash:
    if df_series.empty or ultima is None:
        st.warning("No hay datos para el analito/nivel/rango seleccionado.")
    else:
        score=int(ultima["Score_Riesgo"]); zscore=round(ultima["Z_Score"],2)
        risk_c={"Verde":"#0D9E6E","Ámbar":"#F59E0B","Rojo":"#E53E3E"}.get(ultima["Estado"],"#0D9E6E")
        estado_cls=ESTADO_CLS.get(ultima["Estado"],"")

        k1,k2,k3,k4,k5=st.columns(5)
        for col,val,lbl,color,sub in [
            (k1,f"{ultima['Valor']}","Valor Actual","#1A6FC4","Última medición"),
            (k2,f"{ultima['Media_Objetivo']}","Media Objetivo","#4F6FA8","μ objetivo"),
            (k3,f"±{ultima['SD_Objetivo']}","SD Objetivo","#6B5CA5","σ objetivo"),
            (k4,f"{zscore:+.2f}σ","Z-Score","#E53E3E" if abs(zscore)>=2 else "#0D9E6E","Z=(x-μ)/σ"),
            (k5,f"{score}/100","Score de Riesgo",risk_c,ultima["Estado"]),
        ]:
            with col:
                st.markdown(
                    f'<div class="kpi-card {estado_cls}">'
                    f'<div class="kpi-val" style="color:{color}">{val}</div>'
                    f'<div class="kpi-lbl">{lbl}</div>'
                    f'<div class="kpi-sub">{sub}</div></div>',
                    unsafe_allow_html=True)

        if ultima["Estado"]!="Verde":
            st.markdown("<br>",unsafe_allow_html=True)
            render_kb_panel(analito,ultima["Estado"],ultima["Regla_Violada"],nivel_activo)

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
            with cols_tea[i%len(cols_tea)]:
                tea_editado[an]=st.number_input(f"TEa% — {an.split('(')[0].strip()}",
                    min_value=1.0,max_value=50.0,value=float(TEA_CLIA.get(an,(TEA_DEFAULT,"",""))[0]),step=0.5,key=f"tea_{an}")
    st.markdown("<br>",unsafe_allow_html=True)
    niveles_globales=sorted(df_all["Nivel"].unique())
    sigma_data=[]
    for an in analitos_ls:
        for niv in niveles_globales:
            sub=df_all[(df_all["Analito"]==an)&(df_all["Nivel"]==niv)&
                       (df_all["Fecha"]>=pd.Timestamp(f_min))&(df_all["Fecha"]<=pd.Timestamp(f_max))].copy()
            if sub.empty: continue
            sig=calcular_sigma(sub,tea_editado.get(an,TEA_DEFAULT))
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
        colores_nivel={"N":"#1A6FC4","PB":"#F59E0B","PA":"#E53E3E"}
        for niv in niveles_globales:
            niv_data=[d for d in sigma_data if d["nivel"]==niv]
            if not niv_data: continue
            fig_s.add_trace(go.Bar(
                name=NIVELES.get(niv,NIVELES["N"])["label"],
                x=[d["analito"].split("(")[0].strip() for d in niv_data],
                y=[d["sigma"] for d in niv_data],
                marker_color=colores_nivel.get(niv,"#1A6FC4"),
                marker_line_color="#FFFFFF",marker_line_width=1.5,
                text=[f"{d['sigma']}σ" for d in niv_data],textposition="outside",
                hovertemplate="<b>%{x}</b><br>Sigma: <b>%{y}σ</b><extra></extra>"))
        for y_v,color,lbl in [(6,"#0D9E6E","6σ"),(4,"#1A6FC4","4σ"),(3,"#F59E0B","3σ")]:
            fig_s.add_hline(y=y_v,line_color=color,line_width=1.5,line_dash="dash",
                            annotation_text=lbl,annotation_position="right",
                            annotation_font=dict(color=color,size=11))
        for y0,y1,col in [(6,10,"rgba(13,158,110,.07)"),(4,6,"rgba(26,111,196,.06)"),
                           (3,4,"rgba(245,158,11,.06)"),(0,3,"rgba(229,62,62,.06)")]:
            fig_s.add_hrect(y0=y0,y1=y1,fillcolor=col,line_width=0)
        fig_s.update_layout(template="plotly_white",barmode="group",
            title=dict(text="Sigma Metrics por Analito y Nivel",font=dict(size=15,color="#1C2B3A",family="Inter")),
            paper_bgcolor="#FFFFFF",plot_bgcolor="#FAFBFC",font=dict(color="#475569",family="Inter"),
            xaxis=dict(gridcolor="#F1F5F9",linecolor="#E2E8F0",title="Analito"),
            yaxis=dict(gridcolor="#F1F5F9",linecolor="#E2E8F0",title="Sigma (σ)",range=[0,11]),
            height=440,margin=dict(l=10,r=130,t=60,b=10),
            legend=dict(orientation="h",y=1.08,x=0.5,xanchor="center"))
        st.plotly_chart(fig_s,use_container_width=True)
        st.markdown('<div class="sec-head">Detalle de cálculo</div>',unsafe_allow_html=True)
        st.write(pd.DataFrame([{"Analito":d["analito"],"Nivel":d["nivel_label"],"N":d["n"],
            "Media":d["media"],"SD":d["sd"],"CV%":f"{d['cv_pct']}%","Sesgo%":f"{d['sesgo_pct']}%",
            "TEa%":f"{d['tea_pct']}%","Sigma":d["sigma"],"Categoría":d["categoria"]} for d in sigma_data
        ]).to_html(escape=False,index=False),unsafe_allow_html=True)
        st.markdown('<div class="sec-head">Interpretación clínica</div>',unsafe_allow_html=True)
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
        "(inmunoensayo/hormonal). Consulta siempre el insert de tu lote en "
        "[myeInserts QCNet](https://myeinserts-app.qcnet.com/home).")
    col_sel1,col_sel2=st.columns([2,1])
    with col_sel1:
        an_kb=st.selectbox("Analito a consultar",options=list(BIORAD_KB.keys()),key="kb_analito_sel")
    with col_sel2:
        estado_kb=st.selectbox("Simular estado",
            options=["Rojo (1_3s)","Ámbar (4_1s / 10_x)","Verde (informativo)"],key="kb_estado_sel")
    estado_sim="Rojo" if "Rojo" in estado_kb else "Ámbar" if "Ámbar" in estado_kb else "Verde"
    regla_sim="1_3s" if estado_sim=="Rojo" else "4_1s" if estado_sim=="Ámbar" else "—"
    st.markdown("<br>",unsafe_allow_html=True)
    render_kb_panel(an_kb,estado_sim,regla_sim,nivel_activo)
    st.markdown("---")
    st.markdown("### 🔴 Alarmas activas en el período seleccionado")
    hay_alarmas=False
    for an in analitos_ls:
        for niv in sorted(df_all["Nivel"].unique()):
            sub=evaluar_westgard(df_all[(df_all["Analito"]==an)&(df_all["Nivel"]==niv)&
                                        (df_all["Fecha"]>=pd.Timestamp(f_min))&
                                        (df_all["Fecha"]<=pd.Timestamp(f_max))].copy())
            if sub.empty: continue
            u=sub.iloc[-1]
            if u["Estado"]!="Verde":
                hay_alarmas=True; render_kb_panel(an,u["Estado"],u["Regla_Violada"],niv)
    if not hay_alarmas:
        st.success("✅ No hay alarmas activas. ¡El laboratorio opera correctamente!")
    st.markdown("---")
    st.markdown("### 📚 Cobertura de la base de conocimiento")
    for grupo,analitos_grupo in GRUPOS_ANALITICOS.items():
        con_ficha=[a for a in analitos_grupo if a in BIORAD_KB]
        st.markdown(f"**{grupo}:** "+" · ".join([f"`{a}`" for a in con_ficha]))


# ── TAB 4: ASISTENTE IA ──────────────────────────────────────
with tab_chat:
    st.markdown("### 🤖 Asistente AIQC — Powered by Google Gemini")
    modelo_activo=st.session_state.get("gemini_model_active","models/gemini-2.5-flash")
    st.markdown(
        f'<div class="gemini-banner">🟢 <b>Google Gemini activo</b> · Modelo: <code>{modelo_activo}</code> · '
        f'Historial: {MAX_TURNS} turnos · Base de conocimiento Bio-Rad integrada.</div>',
        unsafe_allow_html=True)
    if "messages" not in st.session_state:
        st.session_state["messages"]=[{"role":"assistant","content":(
            "¡Hola! Soy el **Asistente AIQC v4.9** con base de conocimiento **Bio-Rad** integrada.\n\n"
            "Prueba a preguntarme:\n"
            "- *¿Por qué puede fallar el control de ALT en el nivel Patológico Alto?*\n"
            "- *¿Qué hago si el Potasio da 1_3s en el nivel Normal?*\n"
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
        st.caption("Acciones persistentes en SQLite · Desglose por nivel de control.")
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
                except Exception as e: st.error(f"Error: {e}")

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
        st.markdown("<hr style='border-color:#E2E8F0'>",unsafe_allow_html=True)
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

        st.markdown("<hr style='border-color:#E2E8F0'>",unsafe_allow_html=True)
        acciones_db=load_acciones(db_con)
        claves_log=[f"{row['Fecha'].date()}_{row['Analito']}_{row.get('_nivel_label','N')}_{idx}" for idx,row in df_log.iterrows()]
        total=len(df_log); hechas=sum(acciones_db.get(k,False) for k in claves_log); pend=total-hechas
        m1,m2,m3,m4=st.columns(4)
        m1.metric("Total violaciones",total); m2.metric("Acciones tomadas ✅",hechas)
        m3.metric("Pendientes ⏳",pend); m4.metric("% completado",f"{int(hechas/total*100) if total else 0}%")

        st.markdown('<div class="sec-head">Resumen por nivel</div>',unsafe_allow_html=True)
        nivel_cols=st.columns(len(niveles_globales_log))
        for col,niv in zip(nivel_cols,niveles_globales_log):
            niv_cfg=NIVELES.get(niv,NIVELES["N"])
            n_viol=len(df_log[df_log.get("Nivel",pd.Series(dtype=str))==niv]) if "Nivel" in df_log.columns else 0
            n_rojos=len(df_log[(df_log.get("Nivel",pd.Series(dtype=str))==niv)&(df_log["Estado"]=="Rojo")]) if "Nivel" in df_log.columns else 0
            with col:
                st.markdown(f'<div class="kpi-card"><div class="kpi-val" style="color:#1A6FC4">{n_viol}</div>'
                            f'<div class="kpi-lbl">{niv_cfg["icon"]} {niv_cfg["label"]}</div>'
                            f'<div class="kpi-sub">{n_rojos} rojos</div></div>',unsafe_allow_html=True)

        if hechas==total: st.success("🎉 Trazabilidad completa. Todas las alertas gestionadas.")
        elif pend: st.warning(f"⚠️ {pend} violación(es) pendiente(s) de acción.")
