# ==============================================================
#  AIQC – Artificial Intelligence for Quality Control
#  Versión: 4.7 – Multi-nivel de control (Normal / Pat. Bajo / Pat. Alto)
#  Deploy:  streamlit run app.py
#  Deps:    pip install streamlit plotly pandas numpy fpdf2 openpyxl google-generativeai kaleido
# ==============================================================

import os
import io
import sqlite3
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
#  CONSTANTES DE NIVELES
# ==============================================================
NIVELES = {
    "N":  {"label": "Normal",          "pill": "nivel-N",  "icon": "🔵"},
    "PB": {"label": "Patológico Bajo",  "pill": "nivel-PB", "icon": "🟡"},
    "PA": {"label": "Patológico Alto",  "pill": "nivel-PA", "icon": "🔴"},
}

def nivel_badge(codigo: str) -> str:
    cfg = NIVELES.get(codigo, NIVELES["N"])
    return (f'<span class="nivel-pill {cfg["pill"]}">'
            f'{cfg["icon"]} {cfg["label"]}</span>')


# ==============================================================
#  1. GOOGLE GEMINI
# ==============================================================
GEMINI_MODELS = [
    "models/gemini-2.5-flash",
    "models/gemini-2.0-flash",
    "models/gemini-2.0-flash-lite",
]
GEMINI_SYSTEM = (
    "Eres AIQC, el sistema automatizado de Control de Calidad de un laboratorio clínico. "
    "REGLA ABSOLUTA: Cada respuesta DEBE incluir los valores numéricos reales del laboratorio "
    "(valor medido, media, SD, Z-Score calculado, estado, regla violada, nivel de control). "
    "NUNCA respondas de forma genérica. Si te piden un plan de corrección, menciona "
    "explícitamente qué analito y nivel (Normal/Patológico Bajo/Patológico Alto) tiene el problema, "
    "su Z-Score y la regla de Westgard violada. "
    "Respondes en español, de forma concisa y técnica. Usas Markdown para mayor claridad. "
    "Fórmula Z-Score: Z = (x − μ) / σ. Muéstrala con valores reales."
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
        user = st.secrets["auth"]["user"]
        pwd  = st.secrets["auth"]["password"]
    except KeyError:
        st.error(
            "⚠️ **Credenciales no configuradas.** "
            "Crea `.streamlit/secrets.toml` con:\n\n"
            "```toml\n[auth]\nuser = \"admin\"\npassword = \"qc2026\"\n```\n\n"
            "En Streamlit Cloud: Settings → Secrets."
        )
        st.stop()
    return user, pwd

VALID_USER, VALID_PASS = get_credentials()

def render_login():
    st.markdown("""
    <div class="login-card">
        <div style="font-size:3rem;text-align:center">🔬</div>
        <div style="text-align:center;font-size:1.8rem;font-weight:800;color:#0066CC">AIQC</div>
        <div style="text-align:center;font-size:.86rem;color:#6C757D;margin-bottom:28px">
            Artificial Intelligence for Quality Control · v4.7
        </div>
    </div>""", unsafe_allow_html=True)
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

def init_db() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.execute("""
        CREATE TABLE IF NOT EXISTS acciones (
            clave TEXT PRIMARY KEY,
            hecha INTEGER DEFAULT 0,
            ts    TEXT
        )
    """)
    con.commit()
    return con

def load_acciones(con: sqlite3.Connection) -> dict:
    rows = con.execute("SELECT clave, hecha FROM acciones").fetchall()
    return {r[0]: bool(r[1]) for r in rows}

def save_accion(con: sqlite3.Connection, clave: str, hecha: bool):
    con.execute(
        "INSERT OR REPLACE INTO acciones VALUES (?, ?, datetime('now'))",
        (clave, int(hecha))
    )
    con.commit()

if "db_con" not in st.session_state:
    st.session_state["db_con"] = init_db()
db_con = st.session_state["db_con"]


# ==============================================================
#  4. DATOS DEMO — 3 niveles por analito
# ==============================================================
# Configuración de niveles demo: {analito: {nivel: (media, sd)}}
NIVELES_DEMO = {
    "Potasio (K+)": {
        "N":  (4.5,  0.15),   # Normal
        "PB": (2.8,  0.12),   # Patológico Bajo (hipopotasemia)
        "PA": (6.2,  0.18),   # Patológico Alto (hiperpotasemia)
    },
    "ALT (Transaminasa)": {
        "N":  (35.0, 2.5),    # Normal
        "PB": (12.0, 1.5),    # Patológico Bajo
        "PA": (120.0, 8.0),   # Patológico Alto (hepatitis)
    },
}

@st.cache_data(show_spinner=False)
def build_demo(ref_date: str = "") -> pd.DataFrame:
    np.random.seed(2026)
    today = pd.Timestamp(ref_date).replace(hour=0, minute=0, second=0, microsecond=0)
    dates = [today - timedelta(days=29 - i) for i in range(30)]
    rows  = []

    for analito, niveles in NIVELES_DEMO.items():
        for nivel_cod, (media, sd) in niveles.items():
            for i, d in enumerate(dates):
                # Simular deriva en el nivel PA del ALT (últimos 5 días)
                drift = 0.0
                if analito == "ALT (Transaminasa)" and nivel_cod == "PA" and i >= 25:
                    drift = 2.5 * (i - 24) * 0.65

                rows.append({
                    "Fecha":          d,
                    "Analito":        analito,
                    "Nivel":          nivel_cod,
                    "Valor":          round(np.random.normal(media + drift, sd * 0.85), 3),
                    "Media_Objetivo": media,
                    "SD_Objetivo":    sd,
                    "Lote":           f"LOT-{2026 + i // 10}",
                })

    return pd.DataFrame(rows)


# ==============================================================
#  5. CARGA CSV/XLSX — ahora con columna Nivel (opcional)
# ==============================================================
COL_SYNONYMS = {
    "Fecha":          ["fecha","date","dia","timestamp","time","datetime"],
    "Analito":        ["analito","analyte","test","prueba","parametro","magnitud"],
    "Nivel":          ["nivel","level","control_level","qc_level","tipo_control"],
    "Valor":          ["valor","value","resultado","result","medicion","concentracion"],
    "Media_Objetivo": ["media_objetivo","media","mean","target","objetivo","xbar"],
    "SD_Objetivo":    ["sd_objetivo","sd","desviacion","std","sigma","desvest"],
    "Lote":           ["lote","lot","batch","lote_reactivo","reactivo"],
}

def _norm(s):
    trans = str.maketrans("áéíóúàèìòùäëïöüÁÉÍÓÚ","aeiouaeiouaeiouAEIOU")
    return s.lower().strip().translate(trans)

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
    # Nivel y Lote son opcionales
    if "Nivel" not in df2.columns: df2["Nivel"] = "N"
    if "Lote"  not in df2.columns: df2["Lote"]  = "N/A"
    df2["Fecha"]          = pd.to_datetime(df2["Fecha"], dayfirst=True, errors="coerce")
    df2["Valor"]          = pd.to_numeric(df2["Valor"],          errors="coerce")
    df2["Media_Objetivo"] = pd.to_numeric(df2["Media_Objetivo"],  errors="coerce")
    df2["SD_Objetivo"]    = pd.to_numeric(df2["SD_Objetivo"],     errors="coerce")
    # Normalizar códigos de nivel
    nivel_map = {
        "n":"N","normal":"N","nivel 1":"N","nivel1":"N","n1":"N","1":"N",
        "pb":"PB","patologico bajo":"PB","bajo":"PB","nivel 2":"PB","nivel2":"PB","n2":"PB","2":"PB",
        "pa":"PA","patologico alto":"PA","alto":"PA","nivel 3":"PA","nivel3":"PA","n3":"PA","3":"PA",
    }
    df2["Nivel"] = df2["Nivel"].astype(str).str.lower().str.strip().map(
        lambda x: nivel_map.get(x, "N"))
    df2 = df2.dropna(subset=obligatorias)
    if df2.empty: return None, "Sin filas válidas."
    cols = obligatorias + ["Nivel", "Lote"]
    return df2[cols].reset_index(drop=True), ""

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
REGLAS_DESC = (
    "1_3s: ±3SD → Rojo | "
    "2_2s: 2 consec ±2SD → Rojo | "
    "4_1s: 4 consec ±1SD → Ámbar | "
    "10_x: 10 consec mismo lado → Ámbar"
)

def evaluar_westgard(serie):
    df = serie.copy().sort_values("Fecha").reset_index(drop=True)
    df["Z_Score"]       = (df["Valor"] - df["Media_Objetivo"]) / df["SD_Objetivo"]
    df["Regla_Violada"] = "—"
    df["Score_Riesgo"]  = 0
    df["Estado"]        = "Verde"

    for i in range(len(df)):
        z = df.at[i, "Z_Score"]
        if abs(z) >= 3.0:
            df.at[i, "Regla_Violada"] = "1_3s"; df.at[i, "Score_Riesgo"] = 90; df.at[i, "Estado"] = "Rojo"; continue
        if i >= 1:
            zp = df.at[i-1, "Z_Score"]
            if abs(z) >= 2.0 and abs(zp) >= 2.0 and np.sign(z) == np.sign(zp):
                df.at[i, "Regla_Violada"] = "2_2s"; df.at[i, "Score_Riesgo"] = 75; df.at[i, "Estado"] = "Rojo"; continue
        if i >= 3:
            w4 = df.loc[i-3:i, "Z_Score"].values
            if all(abs(x) >= 1.0 for x in w4) and len(set(np.sign(w4))) == 1:
                df.at[i, "Regla_Violada"] = "4_1s"; df.at[i, "Score_Riesgo"] = 60; df.at[i, "Estado"] = "Ámbar"; continue
        if i >= 9:
            w10 = df.loc[i-9:i, "Z_Score"].values
            signos = set(np.sign(w10))
            if len(signos) == 1 and 0.0 not in signos:
                df.at[i, "Regla_Violada"] = "10_x"; df.at[i, "Score_Riesgo"] = 55; df.at[i, "Estado"] = "Ámbar"; continue
        if abs(z) >= 2.0:
            df.at[i, "Regla_Violada"] = "1_2s (warn)"; df.at[i, "Score_Riesgo"] = 45; df.at[i, "Estado"] = "Ámbar"; continue
        df.at[i, "Score_Riesgo"] = max(0, int(abs(z) * 18))

    return df

def estado_badge(e):
    cfg = {"Verde":("badge-green","●"),"Ámbar":("badge-amber","▲"),"Rojo":("badge-red","■")}
    cls, ico = cfg.get(e, ("badge-green","●"))
    return f'<span class="badge {cls}">{ico} {e}</span>'


# ==============================================================
#  7. SIGMA METRICS
# ==============================================================
TEA_CLIA = {
    "Potasio (K+)":       (8.0,  "mmol/L", "CLIA ±0.5 mmol/L → ~8% a nivel normal"),
    "ALT (Transaminasa)": (20.0, "U/L",    "CLIA ±20%"),
    "Glucosa":            (10.0, "mg/dL",  "CLIA ±10%"),
    "Sodio":              (4.0,  "mmol/L", "CLIA ±4 mmol/L"),
    "Creatinina":         (15.0, "mg/dL",  "CLIA ±15%"),
    "Colesterol":         (10.0, "mg/dL",  "CLIA ±10%"),
    "Hemoglobina":        (7.0,  "g/dL",   "CLIA ±7%"),
    "Calcio":             (8.0,  "mg/dL",  "CLIA ±8%"),
}
TEA_DEFAULT = 15.0

def calcular_sigma(df_analito: pd.DataFrame, tea_pct: float) -> dict:
    if df_analito.empty: return {}
    media     = df_analito["Media_Objetivo"].iloc[0]
    sd        = df_analito["SD_Objetivo"].iloc[0]
    vals      = df_analito["Valor"]
    cv_pct    = (sd / media) * 100 if media != 0 else 0
    sesgo_pct = abs((vals.mean() - media) / media) * 100 if media != 0 else 0
    sigma     = (tea_pct - sesgo_pct) / cv_pct if cv_pct > 0 else 0
    if sigma >= 6:   categoria = "🏆 Clase Mundial";  color = "#198754"
    elif sigma >= 4: categoria = "✅ Buena calidad";  color = "#0066CC"
    elif sigma >= 3: categoria = "⚠️ Aceptable";      color = "#FD7E14"
    else:            categoria = "🔴 Revisar método"; color = "#DC3545"
    return {
        "sigma": round(sigma, 2), "cv_pct": round(cv_pct, 2),
        "sesgo_pct": round(sesgo_pct, 2), "tea_pct": tea_pct,
        "categoria": categoria, "color": color,
        "media": round(media, 3), "sd": round(sd, 4), "n": len(vals),
    }


# ==============================================================
#  8. LEVEY-JENNINGS
# ==============================================================
def build_lj_figure(df_series: pd.DataFrame, analito: str, nivel: str) -> go.Figure:
    u  = df_series.iloc[-1]
    m  = u["Media_Objetivo"]
    sd = u["SD_Objetivo"]
    nivel_label = NIVELES.get(nivel, NIVELES["N"])["label"]

    fig = go.Figure()
    fig.add_hrect(y0=m+2*sd, y1=m+3*sd, fillcolor="rgba(220,53,69,.10)",  line_width=0)
    fig.add_hrect(y0=m-3*sd, y1=m-2*sd, fillcolor="rgba(220,53,69,.10)",  line_width=0)
    fig.add_hrect(y0=m+sd,   y1=m+2*sd, fillcolor="rgba(255,193,7,.08)",  line_width=0)
    fig.add_hrect(y0=m-2*sd, y1=m-sd,   fillcolor="rgba(255,193,7,.08)",  line_width=0)
    fig.add_hrect(y0=m-sd,   y1=m+sd,   fillcolor="rgba(25,135,84,.06)",  line_width=0)

    for y_v, color, width, dash, name in [
        (m,      "#198754", 2.0, "solid", "Media"),
        (m+sd,   "#ADB5BD", 1.0, "dash",  "+1 SD"),
        (m-sd,   "#ADB5BD", 1.0, "dash",  "−1 SD"),
        (m+2*sd, "#FD7E14", 1.4, "dash",  "+2 SD"),
        (m-2*sd, "#FD7E14", 1.4, "dash",  "−2 SD"),
        (m+3*sd, "#DC3545", 1.8, "dot",   "+3 SD"),
        (m-3*sd, "#DC3545", 1.8, "dot",   "−3 SD"),
    ]:
        fig.add_hline(y=y_v, line_color=color, line_width=width, line_dash=dash,
                      annotation_text=name, annotation_position="right",
                      annotation_font=dict(color=color, size=10, family="Arial"))

    fig.add_trace(go.Scatter(
        x=df_series["Fecha"], y=df_series["Valor"],
        mode="lines", line=dict(color="#CED4DA", width=1.5),
        showlegend=False, hoverinfo="skip"))

    for estado, color in [("Verde","#198754"), ("Ámbar","#FD7E14"), ("Rojo","#DC3545")]:
        sub = df_series[df_series["Estado"] == estado]
        if sub.empty: continue
        fig.add_trace(go.Scatter(
            x=sub["Fecha"], y=sub["Valor"], mode="markers", name=estado,
            marker=dict(size=9, color=color, line=dict(color="#FFFFFF", width=1.5)),
        ))

    fig.update_layout(
        template="plotly_white",
        title=dict(
            text=f"Levey-Jennings — {analito} · Nivel: {nivel_label}",
            font=dict(size=13, color="#212529", family="Arial")),
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font=dict(color="#495057", family="Arial"),
        legend=dict(orientation="h", y=1.08, x=1, xanchor="right"),
        xaxis=dict(gridcolor="#F1F3F5", linecolor="#DEE2E6",
                   tickformat="%d %b", title="Fecha"),
        yaxis=dict(gridcolor="#F1F3F5", linecolor="#DEE2E6", title="Valor"),
        height=380, width=760,
        margin=dict(l=10, r=110, t=55, b=40),
    )
    return fig

def fig_to_png_bytes(fig: go.Figure) -> bytes | None:
    try:
        return fig.to_image(format="png", scale=2)
    except Exception:
        return None


# ==============================================================
#  9. PDF — con sección multi-nivel
# ==============================================================
def generar_pdf(df_all, analitos, fuente):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Cabecera
    pdf.set_fill_color(0, 102, 204); pdf.rect(0, 0, 210, 36, "F")
    pdf.set_font("Helvetica", "B", 18); pdf.set_text_color(255, 255, 255); pdf.ln(8)
    pdf.cell(0, 10, "AIQC – Informe de Incidencias de Calidad", ln=True, align="C")
    pdf.set_font("Helvetica", "", 9); pdf.set_text_color(220, 235, 255)
    pdf.cell(0, 6,
             f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}  |  "
             f"Fuente: {fuente}  |  Analitos: {', '.join(analitos)}",
             ln=True, align="C")
    pdf.ln(10)

    niveles_disponibles = sorted(df_all["Nivel"].unique()) if "Nivel" in df_all.columns else ["N"]

    def sec(txt):
        pdf.set_font("Helvetica", "B", 12); pdf.set_text_color(0, 102, 204)
        pdf.cell(0, 8, txt, ln=True)
        pdf.set_draw_color(0, 102, 204)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(3)

    # Resumen ejecutivo por nivel
    sec("1. Resumen Ejecutivo por Nivel de Control")
    for niv in niveles_disponibles:
        niv_label = NIVELES.get(niv, NIVELES["N"])["label"]
        frames = [evaluar_westgard(
            df_all[(df_all["Analito"] == an) & (df_all["Nivel"] == niv)].copy())
            for an in analitos]
        df_ev = pd.concat([f for f in frames if not f.empty])
        if df_ev.empty: continue
        total = len(df_ev)
        rojos = int((df_ev["Estado"] == "Rojo").sum())
        ambar = int((df_ev["Estado"] == "Ámbar").sum())
        ok    = int((df_ev["Estado"] == "Verde").sum())
        pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(33, 37, 41)
        pdf.cell(0, 7, f"Nivel: {niv_label}", ln=True)
        pdf.set_font("Helvetica", "", 9)
        for line in [
            f"  Total mediciones: {total}  |  Verde: {ok} ({100*ok//total if total else 0}%)  |  "
            f"Ámbar: {ambar}  |  Rojo: {rojos}"
        ]:
            pdf.cell(0, 6, line, ln=True)
        pdf.ln(2)

    # Estado por analito y nivel
    sec("2. Estado por Analito y Nivel  [Z = (x - media) / SD]")
    pdf.set_font("Helvetica", "", 8); pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 5, REGLAS_DESC, ln=True); pdf.ln(2)

    col_w = [42, 28, 20, 22, 22, 28, 22, 20]
    hdrs  = ["Analito", "Nivel", "Valor", "Z-Score", "Score", "Regla", "Estado", "N pts"]
    pdf.set_fill_color(240, 242, 245); pdf.set_text_color(73, 80, 87)
    pdf.set_font("Helvetica", "B", 8)
    for w, h in zip(col_w, hdrs): pdf.cell(w, 8, h, border=1, fill=True)
    pdf.ln()
    for an in analitos:
        for niv in niveles_disponibles:
            sub = evaluar_westgard(
                df_all[(df_all["Analito"] == an) & (df_all["Nivel"] == niv)].copy())
            if sub.empty: continue
            u = sub.iloc[-1]
            niv_label = NIVELES.get(niv, NIVELES["N"])["label"]
            if u["Estado"] == "Rojo":   pdf.set_fill_color(252,232,232); pdf.set_text_color(155,28,28)
            elif u["Estado"] == "Ámbar":pdf.set_fill_color(255,243,205); pdf.set_text_color(133,100,4)
            else:                        pdf.set_fill_color(209,247,231); pdf.set_text_color(10,102,64)
            pdf.set_font("Helvetica", "", 8)
            for w, v in zip(col_w, [
                an[:22], niv_label[:14], str(u["Valor"]),
                f"{u['Z_Score']:+.2f}", f"{int(u['Score_Riesgo'])}/100",
                u["Regla_Violada"], u["Estado"], str(len(sub))
            ]):
                pdf.cell(w, 7, str(v), border=1, fill=True)
            pdf.ln()
    pdf.ln(5)

    # Sigma Metrics por nivel
    sec("3. Sigma Metrics (CLIA) por Nivel")
    sw  = [42, 28, 18, 18, 18, 18, 42]
    sh  = ["Analito", "Nivel", "TEa%", "CV%", "Sesgo%", "Sigma", "Categoría"]
    pdf.set_fill_color(240,242,245); pdf.set_text_color(73,80,87)
    pdf.set_font("Helvetica", "B", 8)
    for w, h in zip(sw, sh): pdf.cell(w, 8, h, border=1, fill=True)
    pdf.ln()
    for an in analitos:
        for niv in niveles_disponibles:
            sub = df_all[(df_all["Analito"] == an) & (df_all["Nivel"] == niv)].copy()
            tea = TEA_CLIA.get(an, (TEA_DEFAULT, "", ""))[0]
            sig = calcular_sigma(sub, tea)
            if not sig: continue
            s = sig["sigma"]
            if s >= 6:   pdf.set_fill_color(209,247,231); pdf.set_text_color(10,102,64)
            elif s >= 4: pdf.set_fill_color(219,234,254); pdf.set_text_color(0,102,204)
            elif s >= 3: pdf.set_fill_color(255,243,205); pdf.set_text_color(133,100,4)
            else:        pdf.set_fill_color(252,232,232); pdf.set_text_color(155,28,28)
            pdf.set_font("Helvetica", "", 8)
            niv_label = NIVELES.get(niv, NIVELES["N"])["label"]
            cat_clean = (sig["categoria"]
                         .replace("🏆","").replace("✅","").replace("⚠️","").replace("🔴","").strip())
            for w, v in zip(sw, [
                an[:22], niv_label[:14], f"{sig['tea_pct']}%", f"{sig['cv_pct']}%",
                f"{sig['sesgo_pct']}%", str(sig['sigma']), cat_clean
            ]):
                pdf.cell(w, 7, str(v), border=1, fill=True)
            pdf.ln()
    pdf.ln(5)

    # Gráficos Levey-Jennings por analito y nivel
    sec("4. Gráficos Levey-Jennings por Analito y Nivel")
    kaleido_ok = True
    for an in analitos:
        for niv in niveles_disponibles:
            sub_ev = evaluar_westgard(
                df_all[(df_all["Analito"] == an) & (df_all["Nivel"] == niv)].copy())
            if sub_ev.empty: continue
            fig       = build_lj_figure(sub_ev, an, niv)
            png_bytes = fig_to_png_bytes(fig)
            niv_label = NIVELES.get(niv, NIVELES["N"])["label"]
            if png_bytes:
                tmp_path = f"/tmp/lj_{an.replace(' ','_').replace('(','').replace(')','_')}_{niv}.png"
                with open(tmp_path, "wb") as f:
                    f.write(png_bytes)
                pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(33, 37, 41)
                pdf.cell(0, 7, f"{an} — Nivel: {niv_label}", ln=True)
                pdf.image(tmp_path, x=10, w=190)
                pdf.ln(4)
            else:
                kaleido_ok = False
                pdf.set_font("Helvetica", "I", 9); pdf.set_text_color(108, 117, 125)
                pdf.cell(0, 7, f"[Gráfico no disponible para {an} / {niv_label}]", ln=True)

    if not kaleido_ok:
        pdf.ln(2)
        pdf.set_font("Helvetica", "I", 8); pdf.set_text_color(108,117,125)
        pdf.cell(0, 5, "Para incluir gráficos ejecuta: pip install kaleido", ln=True)
    pdf.ln(3)

    # Detalle de violaciones
    all_frames = []
    for an in analitos:
        for niv in niveles_disponibles:
            sub = evaluar_westgard(
                df_all[(df_all["Analito"] == an) & (df_all["Nivel"] == niv)].copy())
            if not sub.empty:
                sub["_nivel_label"] = NIVELES.get(niv, NIVELES["N"])["label"]
                all_frames.append(sub)
    df_full = pd.concat(all_frames) if all_frames else pd.DataFrame()
    viol = df_full[df_full["Estado"] != "Verde"].copy() if not df_full.empty else pd.DataFrame()

    sec(f"5. Detalle de Violaciones ({len(viol)})")
    if viol.empty:
        pdf.set_font("Helvetica", "I", 10); pdf.set_text_color(10, 102, 64)
        pdf.cell(0, 7, "Sin violaciones en el periodo.", ln=True)
    else:
        vc  = [24, 38, 20, 20, 20, 22, 18, 20]
        vhd = ["Fecha", "Analito", "Nivel", "Valor", "Z-Score", "Regla", "Score", "Estado"]
        pdf.set_fill_color(240,242,245); pdf.set_text_color(73,80,87)
        pdf.set_font("Helvetica", "B", 7)
        for w, h in zip(vc, vhd): pdf.cell(w, 7, h, border=1, fill=True)
        pdf.ln(); pdf.set_font("Helvetica", "", 7)
        for _, row in viol.iterrows():
            if row["Estado"] == "Rojo": pdf.set_fill_color(252,232,232); pdf.set_text_color(155,28,28)
            else:                        pdf.set_fill_color(255,243,205); pdf.set_text_color(133,100,4)
            for w, v in zip(vc, [
                row["Fecha"].strftime("%d/%m/%Y"), str(row["Analito"])[:20],
                str(row.get("_nivel_label","N/A"))[:10],
                str(row["Valor"]), f"{row['Z_Score']:+.2f}",
                row["Regla_Violada"], f"{int(row['Score_Riesgo'])}/100", row["Estado"]
            ]):
                pdf.cell(w, 6, str(v), border=1, fill=True)
            pdf.ln()
    pdf.ln(5)

    # Recomendaciones
    total_rojo = len(viol[viol["Estado"] == "Rojo"]) if not viol.empty else 0
    total_amb  = len(viol[viol["Estado"] == "Ámbar"]) if not viol.empty else 0
    sec("6. Recomendaciones")
    pdf.set_font("Helvetica", "", 10); pdf.set_text_color(33, 37, 41)
    recs = (
        ["ACCION URGENTE: alertas rojas detectadas. No liberar resultados.",
         "Recalibrar el analizador con material trazable.",
         "Verificar lote, temperatura y caducidad de reactivos.",
         "Repetir los controles de TODOS los niveles tras las acciones correctivas.",
         "Documentar todas las acciones con fecha y responsable."]
        if total_rojo > 0 else
        ["Alertas de advertencia detectadas. Monitoreo estrecho recomendado.",
         "Verificar cadena de frío y almacenamiento de reactivos.",
         "Registrar observaciones en el sistema por nivel de control."]
        if total_amb > 0 else
        ["El laboratorio opera dentro de los criterios de Westgard en todos los niveles.",
         "Continuar con la rutina de QC diaria en los 3 niveles.",
         "Revisar periódicamente los límites por nivel."]
    )
    for i, r in enumerate(recs, 1):
        pdf.multi_cell(0, 6, f"{i}. {r}"); pdf.ln(1)

    pdf.ln(4)
    pdf.set_draw_color(222,226,230); pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(2)
    pdf.set_font("Helvetica", "I", 8); pdf.set_text_color(108, 117, 125)
    pdf.cell(0, 5, "AIQC v4.7 · Informe automatico · Uso interno del laboratorio",
             ln=True, align="C")

    return bytes(pdf.output())


# ==============================================================
#  10. ASISTENTE IA GEMINI
# ==============================================================
MAX_TURNS = 10

def ia_responde_gemini(pregunta, historial, df_all, analitos_ls, f_min, f_max):
    api_key = get_api_key()
    if not api_key:
        return "❌ **API Key de Gemini no configurada.**\n\nVe a Streamlit Cloud → Settings → Secrets."
    genai.configure(api_key=api_key)

    niveles_disponibles = sorted(df_all["Nivel"].unique()) if "Nivel" in df_all.columns else ["N"]
    resumen = []
    for an in analitos_ls:
        for niv in niveles_disponibles:
            sub = evaluar_westgard(
                df_all[(df_all["Analito"] == an) &
                       (df_all["Nivel"] == niv) &
                       (df_all["Fecha"] >= pd.Timestamp(f_min)) &
                       (df_all["Fecha"] <= pd.Timestamp(f_max))].copy())
            if sub.empty: continue
            u      = sub.iloc[-1]
            z_calc = (u['Valor'] - u['Media_Objetivo']) / u['SD_Objetivo']
            tea    = TEA_CLIA.get(an, (TEA_DEFAULT, "", ""))[0]
            sig    = calcular_sigma(sub, tea)
            niv_label = NIVELES.get(niv, NIVELES["N"])["label"]
            resumen.append(
                f"• Analito: {an} | Nivel: {niv_label}\n"
                f"  - Último valor: {u['Valor']} | Media: {u['Media_Objetivo']} | SD: {u['SD_Objetivo']}\n"
                f"  - Z = ({u['Valor']} - {u['Media_Objetivo']}) / {u['SD_Objetivo']} = {z_calc:+.3f}\n"
                f"  - Estado: {u['Estado']} | Regla: {u['Regla_Violada']} | Score: {int(u['Score_Riesgo'])}/100\n"
                f"  - Rojos: {(sub['Estado']=='Rojo').sum()} | Ámbar: {(sub['Estado']=='Ámbar').sum()}\n"
                f"  - Sigma: {sig.get('sigma','N/A')}σ | CV: {sig.get('cv_pct','N/A')}% | "
                f"Sesgo: {sig.get('sesgo_pct','N/A')}% | TEa: {tea}% | {sig.get('categoria','')}"
            )

    contexto = (
        f"=== DATOS REALES DEL LABORATORIO ({f_min} → {f_max}) ===\n"
        f"INSTRUCCIÓN CRÍTICA: USA ESTOS DATOS EXACTOS.\n\n"
        f"{chr(10).join(resumen)}\n\n"
        f"=== REGLAS WESTGARD ===\n{REGLAS_DESC}\n\n"
        f"=== SIGMA METRICS ===\n"
        f"≥6σ: Clase Mundial | ≥4σ: Buena | ≥3σ: Aceptable | <3σ: Revisar\n"
        f"Fórmula: Sigma = (TEa% - Sesgo%) / CV%\n\n"
        f"=== NIVELES DE CONTROL ===\n"
        f"N: Normal | PB: Patológico Bajo | PA: Patológico Alto\n\n"
        f"=== PREGUNTA ===\n{pregunta}"
    )

    recent      = historial[1:][-MAX_TURNS * 2:]
    gemini_hist = [
        {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
        for m in recent
    ]
    last_error = ""
    for model_name in GEMINI_MODELS:
        try:
            m    = genai.GenerativeModel(model_name=model_name,
                                         generation_config=GEMINI_CFG,
                                         system_instruction=GEMINI_SYSTEM)
            chat = m.start_chat(history=gemini_hist)
            resp = chat.send_message(contexto)
            st.session_state["gemini_model_active"] = model_name
            return resp.text
        except Exception as e:
            last_error = str(e)
            if "api_key" in last_error.lower() or "403" in last_error:
                return "❌ API Key inválida. Verifica en Secrets."
            continue
    return f"⚠️ **Todos los modelos han alcanzado su límite.**\n\n_Error: {last_error}_"


# ==============================================================
#  11. SIDEBAR
# ==============================================================
with st.sidebar:
    st.markdown('<div class="sb-logo">🔬</div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-title">AIQC</div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-sub">Quality Control · v4.7</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("**📂 Fuente de datos**")
    uploaded = st.file_uploader("CSV o Excel", type=["csv","xlsx","xls"],
        help="Columnas: Fecha, Analito, Nivel (N/PB/PA), Valor, Media_Objetivo, SD_Objetivo, Lote (opcionales: Nivel, Lote).")

    if uploaded:
        df_cargado, err = leer_archivo(uploaded)
        if df_cargado is not None:
            df_all   = df_cargado
            data_src = f"📄 {uploaded.name}"
            niveles_en_datos = sorted(df_all["Nivel"].unique())
            st.markdown(
                f'<div class="data-pill">✅ <b>{uploaded.name}</b><br>'
                f'{len(df_all)} filas · {df_all["Analito"].nunique()} analito(s) · '
                f'{len(niveles_en_datos)} nivel(es)</div>',
                unsafe_allow_html=True)
        else:
            st.error(err)
            _hoy   = datetime.today().strftime("%Y-%m-%d")
            df_all = build_demo(_hoy)
            data_src = "Demo (error carga)"
    else:
        _hoy     = datetime.today().strftime("%Y-%m-%d")
        df_all   = build_demo(_hoy)
        data_src = "🔬 Modo Demo"
        st.caption("Datos simulados con 3 niveles de control.")

    st.markdown("---")

    # Selector de analito y NIVEL
    analito = st.selectbox("Analito activo", options=sorted(df_all["Analito"].unique()), key="sel_analito")

    niveles_analito = sorted(df_all[df_all["Analito"] == analito]["Nivel"].unique())
    nivel_options   = {NIVELES.get(n, NIVELES["N"])["label"]: n for n in niveles_analito}
    nivel_sel_label = st.selectbox(
        "Nivel de control",
        options=list(nivel_options.keys()),
        key="sel_nivel",
        help="N = Normal · PB = Patológico Bajo · PA = Patológico Alto"
    )
    nivel_activo = nivel_options[nivel_sel_label]

    fechas_d = sorted(df_all["Fecha"].dropna().unique())
    if len(fechas_d) >= 2:
        f_min = st.date_input("Desde",
                              value=pd.Timestamp(fechas_d[0]).date(),
                              min_value=pd.Timestamp(fechas_d[0]).date(),
                              max_value=pd.Timestamp(fechas_d[-1]).date(), key="f1")
        f_max = st.date_input("Hasta",
                              value=pd.Timestamp(fechas_d[-1]).date(),
                              min_value=pd.Timestamp(fechas_d[0]).date(),
                              max_value=pd.Timestamp(fechas_d[-1]).date(), key="f2")
    else:
        f_min = f_max = pd.Timestamp(fechas_d[0]).date() if fechas_d else datetime.today().date()

    st.markdown("---")
    st.markdown("**Estado del laboratorio**")
    for an in sorted(df_all["Analito"].unique()):
        nivs = sorted(df_all[df_all["Analito"] == an]["Nivel"].unique())
        for niv in nivs:
            sub = evaluar_westgard(
                df_all[(df_all["Analito"] == an) & (df_all["Nivel"] == niv)].copy())
            est = sub.iloc[-1]["Estado"]
            led = {"Verde":"🟢","Ámbar":"🟡","Rojo":"🔴"}.get(est,"⚪")
            niv_lbl = NIVELES.get(niv, NIVELES["N"])["label"]
            st.markdown(f"{led} **{an}** · {niv_lbl} — {est}")

    st.markdown("---")
    if st.button("Cerrar sesión", use_container_width=True):
        st.session_state["auth"] = False; st.rerun()
    st.caption(f"Fuente: {data_src}")


# ==============================================================
#  12. DATOS ACTIVOS (analito + nivel seleccionado)
# ==============================================================
df_raw = df_all[
    (df_all["Analito"] == analito) &
    (df_all["Nivel"]   == nivel_activo) &
    (df_all["Fecha"]   >= pd.Timestamp(f_min)) &
    (df_all["Fecha"]   <= pd.Timestamp(f_max))
].copy()
df_series   = evaluar_westgard(df_raw)
ultima      = df_series.iloc[-1] if not df_series.empty else None
analitos_ls = sorted(df_all["Analito"].unique())


# ==============================================================
#  13. CABECERA
# ==============================================================
c1, c2 = st.columns([4, 1])
with c1:
    st.markdown("## 🔬 AIQC – Control de Calidad")
    st.markdown(
        f"<span style='color:#6C757D;font-size:.9rem'>"
        f"<b>Analito:</b> {analito} &nbsp;·&nbsp; "
        f"{nivel_badge(nivel_activo)} &nbsp;·&nbsp; "
        f"<b>Período:</b> {f_min.strftime('%d/%m/%Y')} → {f_max.strftime('%d/%m/%Y')} "
        f"&nbsp;·&nbsp; <b>Fuente:</b> {data_src}</span>", unsafe_allow_html=True)
with c2:
    if ultima is not None:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(estado_badge(ultima["Estado"]), unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)


# ==============================================================
#  14. TABS
# ==============================================================
tab_dash, tab_sigma, tab_chat, tab_log = st.tabs([
    "📊  Dashboard",
    "📈  Sigma Metrics",
    "🤖  Asistente IA (Gemini)",
    "📋  Registro de Acciones",
])


# ── TAB 1: DASHBOARD ─────────────────────────────────────────
with tab_dash:
    if df_series.empty or ultima is None:
        st.warning("No hay datos para el analito/nivel/rango seleccionado.")
    else:
        score  = int(ultima["Score_Riesgo"])
        zscore = round(ultima["Z_Score"], 2)
        risk_c = {"Verde":"#1A7F4B","Ámbar":"#856404","Rojo":"#9B1C1C"}.get(ultima["Estado"],"#1A7F4B")

        k1, k2, k3, k4, k5 = st.columns(5)
        for col, val, lbl, color, sub in [
            (k1, f"{ultima['Valor']}",         "Valor Actual",   "#0066CC", "Última medición"),
            (k2, f"{ultima['Media_Objetivo']}", "Media Objetivo", "#5A6ACA", "μ objetivo"),
            (k3, f"±{ultima['SD_Objetivo']}",  "SD Objetivo",    "#7952B3", "σ objetivo"),
            (k4, f"{zscore:+.2f}σ",            "Z-Score",
             "#C0392B" if abs(zscore) >= 2 else "#1A7F4B", "Z=(x-μ)/σ"),
            (k5, f"{score}/100",               "Score de Riesgo", risk_c,   ultima["Estado"]),
        ]:
            with col:
                st.markdown(
                    f'<div class="kpi-card">'
                    f'<div class="kpi-val" style="color:{color}">{val}</div>'
                    f'<div class="kpi-lbl">{lbl}</div>'
                    f'<div class="kpi-sub">{sub}</div></div>',
                    unsafe_allow_html=True)

        # Vista comparativa de niveles en el mismo analito
        st.markdown("<br>", unsafe_allow_html=True)
        nivs_analito = sorted(df_all[df_all["Analito"] == analito]["Nivel"].unique())
        if len(nivs_analito) > 1:
            st.markdown('<div class="sec-head">Comparativa de niveles — Levey-Jennings</div>',
                        unsafe_allow_html=True)
            tabs_niveles = st.tabs(
                [f"{NIVELES.get(n, NIVELES['N'])['icon']} {NIVELES.get(n, NIVELES['N'])['label']}"
                 for n in nivs_analito])
            for tab_n, niv in zip(tabs_niveles, nivs_analito):
                with tab_n:
                    sub_n = evaluar_westgard(
                        df_all[(df_all["Analito"] == analito) &
                               (df_all["Nivel"]   == niv) &
                               (df_all["Fecha"]   >= pd.Timestamp(f_min)) &
                               (df_all["Fecha"]   <= pd.Timestamp(f_max))].copy())
                    if sub_n.empty:
                        st.info("Sin datos para este nivel en el rango seleccionado.")
                    else:
                        fig_n = build_lj_figure(sub_n, analito, niv)
                        fig_n.update_layout(height=400, margin=dict(l=10, r=130, t=60, b=10))
                        st.plotly_chart(fig_n, use_container_width=True)
        else:
            fig = build_lj_figure(df_series, analito, nivel_activo)
            fig.update_layout(height=460, width=None, margin=dict(l=10, r=130, t=60, b=10))
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="sec-head">Últimas 7 mediciones — nivel activo</div>',
                    unsafe_allow_html=True)
        tail = df_series.tail(7)[
            ["Fecha","Valor","Z_Score","Regla_Violada","Score_Riesgo","Estado","Lote"]].copy()
        tail["Fecha"]  = tail["Fecha"].dt.strftime("%d/%m/%Y")
        tail["Estado"] = tail["Estado"].apply(estado_badge)
        st.write(
            tail.rename(columns={"Z_Score":"Z-Score","Regla_Violada":"Regla","Score_Riesgo":"Score"})
                .to_html(escape=False, index=False),
            unsafe_allow_html=True)


# ── TAB 2: SIGMA METRICS ─────────────────────────────────────
with tab_sigma:
    st.markdown("### 📈 Sigma Metrics — Evaluación de Calidad Analítica")
    st.caption("Sigma = (TEa% − Sesgo%) / CV%  ·  TEa según criterios CLIA  ·  Desglosado por nivel.")

    with st.expander("⚙️ Editar límites TEa por analito", expanded=False):
        tea_editado = {}
        cols_tea = st.columns(min(len(analitos_ls), 3))
        for i, an in enumerate(analitos_ls):
            default_tea = TEA_CLIA.get(an, (TEA_DEFAULT,"",""))[0]
            with cols_tea[i % len(cols_tea)]:
                tea_editado[an] = st.number_input(
                    f"TEa% — {an.split('(')[0].strip()}",
                    min_value=1.0, max_value=50.0,
                    value=float(default_tea), step=0.5, key=f"tea_{an}")

    st.markdown("<br>", unsafe_allow_html=True)
    niveles_globales = sorted(df_all["Nivel"].unique())
    sigma_data = []
    for an in analitos_ls:
        for niv in niveles_globales:
            sub = df_all[
                (df_all["Analito"] == an) &
                (df_all["Nivel"]   == niv) &
                (df_all["Fecha"]   >= pd.Timestamp(f_min)) &
                (df_all["Fecha"]   <= pd.Timestamp(f_max))
            ].copy()
            if sub.empty: continue
            tea = tea_editado.get(an, TEA_DEFAULT)
            sig = calcular_sigma(sub, tea)
            if sig:
                sigma_data.append({"analito": an, "nivel": niv,
                                    "nivel_label": NIVELES.get(niv,NIVELES["N"])["label"], **sig})

    if not sigma_data:
        st.warning("Sin datos suficientes para calcular Sigma Metrics.")
    else:
        # KPIs agrupados por nivel
        for niv in niveles_globales:
            niv_cfg  = NIVELES.get(niv, NIVELES["N"])
            niv_data = [d for d in sigma_data if d["nivel"] == niv]
            if not niv_data: continue
            st.markdown(
                f'<div class="sec-head">{niv_cfg["icon"]} {niv_cfg["label"]}</div>',
                unsafe_allow_html=True)
            cols_s = st.columns(len(niv_data))
            for col, d in zip(cols_s, niv_data):
                with col:
                    st.markdown(
                        f'<div class="kpi-card">'
                        f'<div class="kpi-val" style="color:{d["color"]}">{d["sigma"]}σ</div>'
                        f'<div class="kpi-lbl">{d["analito"].split("(")[0].strip()}</div>'
                        f'<div class="kpi-sub">{d["categoria"]}</div></div>',
                        unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Gráfico de barras multi-nivel
        fig_s = go.Figure()
        colores_nivel = {"N": "#0066CC", "PB": "#FD7E14", "PA": "#DC3545"}
        for niv in niveles_globales:
            niv_data = [d for d in sigma_data if d["nivel"] == niv]
            if not niv_data: continue
            niv_label = NIVELES.get(niv, NIVELES["N"])["label"]
            fig_s.add_trace(go.Bar(
                name=niv_label,
                x=[d["analito"].split("(")[0].strip() for d in niv_data],
                y=[d["sigma"] for d in niv_data],
                marker_color=colores_nivel.get(niv, "#0066CC"),
                marker_line_color="#FFFFFF", marker_line_width=1.5,
                text=[f"{d['sigma']}σ" for d in niv_data], textposition="outside",
                hovertemplate="<b>%{x}</b><br>Nivel: " + niv_label + "<br>Sigma: <b>%{y}σ</b><extra></extra>",
            ))

        for y_v, color, lbl in [(6,"#198754","6σ"),(4,"#0066CC","4σ"),(3,"#FD7E14","3σ")]:
            fig_s.add_hline(y=y_v, line_color=color, line_width=1.5, line_dash="dash",
                            annotation_text=lbl, annotation_position="right",
                            annotation_font=dict(color=color, size=11))
        fig_s.add_hrect(y0=6, y1=10, fillcolor="rgba(25,135,84,.07)",  line_width=0)
        fig_s.add_hrect(y0=4, y1=6,  fillcolor="rgba(0,102,204,.06)",  line_width=0)
        fig_s.add_hrect(y0=3, y1=4,  fillcolor="rgba(253,126,20,.06)", line_width=0)
        fig_s.add_hrect(y0=0, y1=3,  fillcolor="rgba(220,53,69,.06)",  line_width=0)
        fig_s.update_layout(
            template="plotly_white", barmode="group",
            title=dict(text="Sigma Metrics por Analito y Nivel — Criterios CLIA",
                       font=dict(size=15, color="#212529", family="Inter")),
            paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
            font=dict(color="#495057", family="Inter"),
            xaxis=dict(gridcolor="#F1F3F5", linecolor="#DEE2E6", title="Analito"),
            yaxis=dict(gridcolor="#F1F3F5", linecolor="#DEE2E6", title="Sigma (σ)", range=[0, 11]),
            height=440, margin=dict(l=10, r=130, t=60, b=10),
            legend=dict(orientation="h", y=1.08, x=0.5, xanchor="center"),
        )
        st.plotly_chart(fig_s, use_container_width=True)

        st.markdown('<div class="sec-head">Detalle de cálculo por nivel</div>', unsafe_allow_html=True)
        st.write(pd.DataFrame([{
            "Analito": d["analito"], "Nivel": d["nivel_label"],
            "N datos": d["n"], "Media": d["media"], "SD": d["sd"],
            "CV%": f"{d['cv_pct']}%", "Sesgo%": f"{d['sesgo_pct']}%",
            "TEa%": f"{d['tea_pct']}%", "Sigma (σ)": d["sigma"], "Categoría": d["categoria"],
        } for d in sigma_data]).to_html(escape=False, index=False), unsafe_allow_html=True)

        st.markdown('<div class="sec-head">Interpretación clínica</div>', unsafe_allow_html=True)
        for d in sigma_data:
            s   = d["sigma"]
            an  = d["analito"]
            niv = d["nivel_label"]
            if s >= 6:
                st.success(f"**{an} [{niv}]** — **{s}σ** clase mundial.")
            elif s >= 4:
                st.info(f"**{an} [{niv}]** — **{s}σ** buena calidad.")
            elif s >= 3:
                st.warning(f"**{an} [{niv}]** — **{s}σ** aceptable. Aumenta frecuencia de controles.")
            else:
                st.error(f"**{an} [{niv}]** — **{s}σ** deficiente. Revisar calibración y reactivos.")


# ── TAB 3: ASISTENTE IA ──────────────────────────────────────
with tab_chat:
    st.markdown("### 🤖 Asistente AIQC — Powered by Google Gemini")
    modelo_activo = st.session_state.get("gemini_model_active", "models/gemini-2.5-flash")
    st.markdown(
        f'<div class="gemini-banner">🟢 <b>Google Gemini activo</b> · '
        f'Modelo: <code>{modelo_activo}</code> · '
        f'Historial limitado a {MAX_TURNS} turnos · '
        f'Datos con {len(sorted(df_all["Nivel"].unique()))} nivel(es) de control.</div>',
        unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role":"assistant","content":(
            "¡Hola! Soy el **Asistente AIQC v4.7** con soporte multi-nivel.\n\n"
            "Prueba a preguntarme:\n"
            "- *¿Cuál nivel del Potasio tiene peor Sigma?*\n"
            "- *¿Hay violaciones en el nivel Patológico Alto?*\n"
            "- *Dame un plan correctivo para todos los niveles del ALT*\n"
            "- *¿Hay tendencia sostenida (regla 10_x) en algún nivel?*"
        )}]

    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"]=="assistant" else "👤"):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Escribe tu consulta clínica…"):
        st.session_state["messages"].append({"role":"user","content":prompt})
        with st.chat_message("user", avatar="👤"): st.markdown(prompt)
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Analizando datos…"):
                resp = ia_responde_gemini(
                    prompt, st.session_state["messages"],
                    df_all, analitos_ls, f_min, f_max)
                st.markdown(resp)
        st.session_state["messages"].append({"role":"assistant","content":resp})

    if st.button("🗑️ Nueva conversación", key="clr"):
        st.session_state["messages"] = [st.session_state["messages"][0]]; st.rerun()


# ── TAB 4: REGISTRO + PDF ─────────────────────────────────────
with tab_log:
    col_ttl, col_pdf = st.columns([3, 1])
    with col_ttl:
        st.markdown("### 📋 Registro de Incidencias y Trazabilidad")
        st.caption("Las acciones se guardan en base de datos y persisten entre sesiones. Desglose por nivel.")
    with col_pdf:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📄 Descargar Reporte PDF", use_container_width=True, type="primary"):
            with st.spinner("Generando informe multi-nivel con gráficos…"):
                try:
                    pdf_bytes = generar_pdf(df_all, analitos_ls, data_src)
                    fname = f"AIQC_Informe_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                    st.download_button("⬇️ Guardar PDF", data=pdf_bytes,
                                       file_name=fname, mime="application/pdf",
                                       use_container_width=True)
                    st.success("✅ Informe multi-nivel generado.")
                except Exception as e:
                    st.error(f"Error al generar PDF: {e}")

    # Tabla de violaciones agrupada por nivel
    niveles_globales_log = sorted(df_all["Nivel"].unique())
    all_log_frames = []
    for an in analitos_ls:
        for niv in niveles_globales_log:
            sub = evaluar_westgard(
                df_all[(df_all["Analito"] == an) &
                       (df_all["Nivel"]   == niv) &
                       (df_all["Fecha"]   >= pd.Timestamp(f_min)) &
                       (df_all["Fecha"]   <= pd.Timestamp(f_max))].copy())
            if not sub.empty:
                sub["_nivel_label"] = NIVELES.get(niv, NIVELES["N"])["label"]
                all_log_frames.append(sub)

    df_full_log = pd.concat(all_log_frames) if all_log_frames else pd.DataFrame()
    df_log      = df_full_log[df_full_log["Estado"] != "Verde"].copy().reset_index(drop=True) \
                  if not df_full_log.empty else pd.DataFrame()

    if df_log.empty:
        st.success("✅ Sin violaciones en el período seleccionado.")
    else:
        acciones_db = load_acciones(db_con)
        hcols = st.columns([1.4, 2.0, 1.4, 1.1, 1.2, 1.3, 1.4, 1.4, 1.3])
        for c, lbl in zip(hcols, ["📅 Fecha","🔬 Analito","Nivel","Valor",
                                    "Z-Score","Regla","Score","Estado","✅ Acción"]):
            c.markdown(f"**{lbl}**")
        st.markdown("<hr>", unsafe_allow_html=True)

        for idx, row in df_log.iterrows():
            key   = f"{row['Fecha'].date()}_{row['Analito']}_{row.get('_nivel_label','N')}_{idx}"
            rcols = st.columns([1.4, 2.0, 1.4, 1.1, 1.2, 1.3, 1.4, 1.4, 1.3])
            rcols[0].write(row["Fecha"].strftime("%d/%m/%Y"))
            rcols[1].write(row["Analito"])
            rcols[2].markdown(nivel_badge(row.get("Nivel","N")), unsafe_allow_html=True)
            rcols[3].write(str(row["Valor"]))
            rcols[4].write(f"{row['Z_Score']:+.2f}σ")
            rcols[5].write(row["Regla_Violada"])
            rcols[6].write(f"{int(row['Score_Riesgo'])}/100")
            rcols[7].markdown(estado_badge(row["Estado"]), unsafe_allow_html=True)
            prev  = acciones_db.get(key, False)
            nuevo = rcols[8].checkbox("Hecha", value=prev, key=f"accion_{key}")
            if nuevo != prev:
                save_accion(db_con, key, nuevo)

        st.markdown("<hr>", unsafe_allow_html=True)

        # Métricas globales y por nivel
        acciones_db = load_acciones(db_con)
        claves_log  = [
            f"{row['Fecha'].date()}_{row['Analito']}_{row.get('_nivel_label','N')}_{idx}"
            for idx, row in df_log.iterrows()
        ]
        total  = len(df_log)
        hechas = sum(acciones_db.get(k, False) for k in claves_log)
        pend   = total - hechas

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total violaciones",  total)
        m2.metric("Acciones tomadas ✅", hechas)
        m3.metric("Pendientes ⏳",       pend)
        m4.metric("% completado",       f"{int(hechas/total*100) if total else 0}%")

        # Resumen por nivel
        st.markdown('<div class="sec-head">Resumen de violaciones por nivel</div>', unsafe_allow_html=True)
        nivel_cols = st.columns(len(niveles_globales_log))
        for col, niv in zip(nivel_cols, niveles_globales_log):
            niv_cfg   = NIVELES.get(niv, NIVELES["N"])
            n_viol    = len(df_log[df_log.get("Nivel", pd.Series(dtype=str)) == niv]) \
                        if "Nivel" in df_log.columns else 0
            n_rojos   = len(df_log[(df_log.get("Nivel", pd.Series(dtype=str)) == niv) &
                                    (df_log["Estado"] == "Rojo")]) \
                        if "Nivel" in df_log.columns else 0
            with col:
                st.markdown(
                    f'<div class="kpi-card">'
                    f'<div class="kpi-val" style="color:#0066CC">{n_viol}</div>'
                    f'<div class="kpi-lbl">{niv_cfg["icon"]} {niv_cfg["label"]}</div>'
                    f'<div class="kpi-sub">{n_rojos} rojos</div></div>',
                    unsafe_allow_html=True)

        if hechas == total:
            st.success("🎉 Trazabilidad completa. Todas las alertas han sido gestionadas.")
        elif pend:
            st.warning(f"⚠️ {pend} violación(es) pendiente(s) de acción.")
