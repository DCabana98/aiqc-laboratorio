# ==============================================================
#  AIQC – Artificial Intelligence for Quality Control
#  Versión: 4.0 – High-Clarity Light Mode
#  Deploy:  streamlit run app.py
#  Deps:    pip install streamlit plotly pandas numpy fpdf2 openpyxl
# ==============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from fpdf import FPDF

# ── Configuración de página ────────────────────────────────
st.set_page_config(
    page_title="AIQC – Quality Control",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================
#  ESTILOS GLOBALES – HIGH-CLARITY LIGHT MODE
# ==============================================================
st.markdown("""
<style>
/* ── Reset y base ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"] {
    background-color: #FFFFFF !important;
    color: #212529;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* Ocultar elementos de Streamlit */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #F8F9FA !important;
    border-right: 1px solid #DEE2E6;
}
[data-testid="stSidebar"] * { color: #212529 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stDateInput label,
[data-testid="stSidebar"] .stFileUploader label { color: #495057 !important; font-size:.87rem; }

/* ── Inputs, selectboxes ── */
[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
[data-testid="stTextInput"] input,
[data-testid="stDateInput"] input {
    background-color: #FFFFFF !important;
    border: 1px solid #CED4DA !important;
    border-radius: 8px !important;
    color: #212529 !important;
}
[data-baseweb="select"] > div:focus-within,
[data-testid="stTextInput"] input:focus {
    border-color: #0066CC !important;
    box-shadow: 0 0 0 3px rgba(0,102,204,.12) !important;
}

/* ── Botones primarios ── */
.stButton > button[kind="primary"],
button[data-testid="baseButton-primary"] {
    background-color: #0066CC !important;
    border: none !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    transition: background .2s, box-shadow .2s !important;
}
.stButton > button[kind="primary"]:hover,
button[data-testid="baseButton-primary"]:hover {
    background-color: #0052A3 !important;
    box-shadow: 0 4px 12px rgba(0,102,204,.25) !important;
}
/* Botones secundarios */
.stButton > button[kind="secondary"],
button[data-testid="baseButton-secondary"] {
    background-color: #FFFFFF !important;
    border: 1.5px solid #0066CC !important;
    color: #0066CC !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
.stButton > button[kind="secondary"]:hover {
    background-color: #EBF3FF !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: transparent;
    border-bottom: 2px solid #DEE2E6;
    padding-bottom: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 3px solid transparent !important;
    border-radius: 0 !important;
    color: #6C757D !important;
    font-weight: 500;
    padding: 10px 20px !important;
    margin-bottom: -2px;
    transition: color .15s, border-color .15s;
}
.stTabs [data-baseweb="tab"]:hover { color: #0066CC !important; }
.stTabs [aria-selected="true"] {
    color: #0066CC !important;
    border-bottom-color: #0066CC !important;
    font-weight: 700 !important;
    background: transparent !important;
}

/* ── KPI cards ── */
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E9ECEF;
    border-radius: 12px;
    padding: 20px 18px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.04);
    transition: box-shadow .2s, transform .2s;
}
.kpi-card:hover {
    box-shadow: 0 6px 20px rgba(0,0,0,.10);
    transform: translateY(-2px);
}
.kpi-val {
    font-size: 1.9rem; font-weight: 700;
    letter-spacing: -.5px; line-height: 1.15;
}
.kpi-lbl {
    font-size: .73rem; font-weight: 600; color: #6C757D;
    text-transform: uppercase; letter-spacing: .08em; margin-top: 6px;
}
.kpi-sub { font-size: .78rem; color: #ADB5BD; margin-top: 3px; }

/* ── Badges de estado ── */
.badge {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 4px 12px; border-radius: 20px;
    font-size: .78rem; font-weight: 600; letter-spacing: .03em;
}
.badge-green { background: #D1F7E7; color: #0A6640; border: 1px solid #A3EFD0; }
.badge-amber { background: #FFF3CD; color: #856404; border: 1px solid #FFE082; }
.badge-red   { background: #FCE8E8; color: #9B1C1C; border: 1px solid #F5C6C6; }

/* ── Login card ── */
.login-card {
    background: #FFFFFF;
    border: 1px solid #DEE2E6;
    border-radius: 16px;
    padding: 48px 44px;
    max-width: 420px;
    margin: 60px auto 0 auto;
    box-shadow: 0 8px 32px rgba(0,0,0,.10);
}
.login-logo  { font-size: 3rem; text-align: center; margin-bottom: 4px; }
.login-title { text-align: center; font-size: 1.8rem; font-weight: 800;
               color: #0066CC; margin-bottom: 4px; }
.login-sub   { text-align: center; font-size: .86rem; color: #6C757D;
               margin-bottom: 28px; }

/* ── Section heading ── */
.sec-head {
    font-size: 1rem; font-weight: 700; color: #0066CC;
    border-left: 3px solid #0066CC; padding-left: 10px;
    margin: 24px 0 14px 0;
}

/* ── Sidebar branding ── */
.sb-logo  { text-align:center; font-size:2.6rem; margin-bottom:2px; }
.sb-title { text-align:center; font-size:1.1rem; font-weight:800;
            color:#0066CC; margin-bottom:4px; }
.sb-sub   { text-align:center; font-size:.78rem; color:#6C757D; margin-bottom:16px; }

/* ── Info pill (fuente de datos) ── */
.data-pill {
    background:#EBF3FF; border:1px solid #B3D1F5;
    border-radius:8px; padding:10px 14px;
    font-size:.82rem; color:#004A99; margin-top:6px;
}

/* ── Tabla HTML ── */
table { width:100%; border-collapse:collapse; font-size:.87rem; }
thead tr { background:#F8F9FA; }
th { padding:10px 12px; text-align:left; font-weight:600;
     color:#495057; border-bottom:2px solid #DEE2E6; }
td { padding:9px 12px; border-bottom:1px solid #F1F3F5; color:#212529; }
tr:hover td { background:#F8F9FA; }

/* ── Alertas y mensajes ── */
[data-testid="stAlert"] { border-radius: 10px !important; }

/* ── Chat ── */
[data-testid="stChatMessage"] { background:#F8F9FA !important;
    border:1px solid #E9ECEF !important; border-radius:12px !important; }
[data-testid="stChatInput"] > div {
    border:1.5px solid #CED4DA !important;
    border-radius:10px !important;
    background:#FFFFFF !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color:#0066CC !important;
    box-shadow:0 0 0 3px rgba(0,102,204,.10) !important;
}

/* ── Divider ── */
hr { border:none; border-top:1px solid #E9ECEF; margin:16px 0; }

/* ── Métricas nativas de Streamlit ── */
[data-testid="stMetric"] {
    background:#FFFFFF; border:1px solid #E9ECEF;
    border-radius:12px; padding:16px 14px;
    box-shadow:0 2px 8px rgba(0,0,0,.05);
}
[data-testid="stMetricLabel"] { color:#6C757D !important; font-size:.78rem !important; }
[data-testid="stMetricValue"] { color:#212529 !important; font-weight:700 !important; }
</style>
""", unsafe_allow_html=True)


# ==============================================================
#  1. AUTENTICACIÓN
# ==============================================================
VALID_USER, VALID_PASS = "admin", "qc2026"

def render_login():
    st.markdown("""
    <div class="login-card">
        <div class="login-logo">🔬</div>
        <div class="login-title">AIQC</div>
        <div class="login-sub">Artificial Intelligence for Quality Control · v4.0</div>
    </div>""", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.8, 1])
    with mid:
        st.markdown("<br>", unsafe_allow_html=True)
        user = st.text_input("Usuario", placeholder="admin", key="_u")
        pwd  = st.text_input("Contraseña", type="password", placeholder="••••••", key="_p")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Acceder al sistema →", use_container_width=True, type="primary"):
            if user == VALID_USER and pwd == VALID_PASS:
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas. Por favor, inténtalo de nuevo.")

if not st.session_state.get("auth"):
    render_login()
    st.stop()


# ==============================================================
#  2. GENERADOR DE DATOS DEMO
# ==============================================================
@st.cache_data(show_spinner=False)
def build_demo() -> pd.DataFrame:
    np.random.seed(2026)
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    dates = [today - timedelta(days=29 - i) for i in range(30)]
    lotes = [f"LOT-{2026 + i // 10}" for i in range(30)]
    rows  = []
    for i, d in enumerate(dates):
        rows.append({"Fecha": d, "Analito": "Potasio (K+)",
                     "Valor": round(np.random.normal(4.5, 0.15 * 0.85), 3),
                     "Media_Objetivo": 4.5, "SD_Objetivo": 0.15, "Lote": lotes[i]})
    for i, d in enumerate(dates):
        drift = 2.5 * (i - 24) * 0.65 if i >= 25 else 0.0
        rows.append({"Fecha": d, "Analito": "ALT (Transaminasa)",
                     "Valor": round(np.random.normal(35.0 + drift, 2.5), 2),
                     "Media_Objetivo": 35.0, "SD_Objetivo": 2.5, "Lote": lotes[i]})
    return pd.DataFrame(rows)


# ==============================================================
#  3. CARGA CSV / XLSX – NORMALIZACIÓN FLEXIBLE
# ==============================================================
COL_SYNONYMS = {
    "Fecha":          ["fecha","date","dia","timestamp","time","datetime"],
    "Analito":        ["analito","analyte","test","prueba","parametro","magnitud"],
    "Valor":          ["valor","value","resultado","result","medicion","concentracion"],
    "Media_Objetivo": ["media_objetivo","media","mean","target","objetivo","xbar"],
    "SD_Objetivo":    ["sd_objetivo","sd","desviacion","std","sigma","desvest"],
    "Lote":           ["lote","lot","batch","lote_reactivo","reactivo"],
}

def _norm(s: str) -> str:
    trans = str.maketrans("áéíóúàèìòùäëïöüÁÉÍÓÚ","aeiouaeiouaeiouAEIOU")
    return s.lower().strip().translate(trans)

def normalizar_df(df: pd.DataFrame):
    df_n   = {_norm(c): c for c in df.columns}
    rename = {}
    for interno, sins in COL_SYNONYMS.items():
        for s in sins:
            if s in df_n:
                rename[df_n[s]] = interno; break
        if interno not in rename.values():
            for col_n, col_o in df_n.items():
                if any(s in col_n or col_n in s for s in sins):
                    rename[col_o] = interno; break
    df2 = df.rename(columns=rename)
    obligatorias = ["Fecha","Analito","Valor","Media_Objetivo","SD_Objetivo"]
    faltan = [c for c in obligatorias if c not in df2.columns]
    if faltan:
        return None, f"Columnas no encontradas: {', '.join(faltan)}."
    if "Lote" not in df2.columns:
        df2["Lote"] = "N/A"
    df2["Fecha"]          = pd.to_datetime(df2["Fecha"], dayfirst=True, errors="coerce")
    df2["Valor"]          = pd.to_numeric(df2["Valor"],          errors="coerce")
    df2["Media_Objetivo"] = pd.to_numeric(df2["Media_Objetivo"],  errors="coerce")
    df2["SD_Objetivo"]    = pd.to_numeric(df2["SD_Objetivo"],     errors="coerce")
    df2 = df2.dropna(subset=obligatorias)
    if df2.empty:
        return None, "Sin filas válidas tras la limpieza."
    return df2[obligatorias + ["Lote"]].reset_index(drop=True), ""

def leer_archivo(uploaded):
    name = uploaded.name.lower()
    try:
        raw = pd.read_csv(uploaded, sep=None, engine="python") if name.endswith(".csv") \
              else pd.read_excel(uploaded)
        return normalizar_df(raw)
    except Exception as e:
        return None, f"Error al leer el archivo: {e}"


# ==============================================================
#  4. LÓGICA DE ALERTAS – WESTGARD
# ==============================================================
def evaluar_westgard(serie: pd.DataFrame) -> pd.DataFrame:
    df = serie.copy().sort_values("Fecha").reset_index(drop=True)
    df["Z_Score"]       = (df["Valor"] - df["Media_Objetivo"]) / df["SD_Objetivo"]
    df["Regla_Violada"] = "—"
    df["Score_Riesgo"]  = 0
    df["Estado"]        = "Verde"
    for i in range(len(df)):
        z = df.at[i, "Z_Score"]
        if abs(z) >= 3.0:
            df.at[i, "Regla_Violada"] = "1_3s"
            df.at[i, "Score_Riesgo"]  = 90
            df.at[i, "Estado"]        = "Rojo"; continue
        if i >= 1:
            zp = df.at[i-1, "Z_Score"]
            if abs(z) >= 2.0 and abs(zp) >= 2.0 and np.sign(z) == np.sign(zp):
                df.at[i, "Regla_Violada"] = "2_2s"
                df.at[i, "Score_Riesgo"]  = 75
                df.at[i, "Estado"]        = "Rojo"; continue
        if i >= 3:
            w = df.loc[i-3:i, "Z_Score"].values
            if all(abs(x) >= 1.0 for x in w) and len(set(np.sign(w))) == 1:
                df.at[i, "Regla_Violada"] = "4_1s"
                df.at[i, "Score_Riesgo"]  = 60
                df.at[i, "Estado"]        = "Ámbar"; continue
        if abs(z) >= 2.0:
            df.at[i, "Regla_Violada"] = "1_2s (warn)"
            df.at[i, "Score_Riesgo"]  = 45
            df.at[i, "Estado"]        = "Ámbar"; continue
        df.at[i, "Score_Riesgo"] = max(0, int(abs(z) * 18))
    return df

def estado_badge(e: str) -> str:
    cfg = {
        "Verde": ("badge-green", "●"),
        "Ámbar": ("badge-amber", "▲"),
        "Rojo":  ("badge-red",   "■"),
    }
    cls, ico = cfg.get(e, ("badge-green","●"))
    return f'<span class="badge {cls}">{ico} {e}</span>'


# ==============================================================
#  5. GENERADOR PDF
# ==============================================================
def generar_pdf(df_all: pd.DataFrame, analitos: list, fuente: str) -> bytes:
    pdf = FPDF(); pdf.set_auto_page_break(auto=True, margin=15); pdf.add_page()

    # Encabezado azul
    pdf.set_fill_color(0, 102, 204)
    pdf.rect(0, 0, 210, 36, "F")
    pdf.set_font("Helvetica","B",18); pdf.set_text_color(255,255,255)
    pdf.ln(8)
    pdf.cell(0, 10, "AIQC – Informe de Incidencias de Calidad", ln=True, align="C")
    pdf.set_font("Helvetica","",9); pdf.set_text_color(220,235,255)
    pdf.cell(0, 6,
             f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}  |  "
             f"Fuente: {fuente}  |  Analitos: {', '.join(analitos)}",
             ln=True, align="C")
    pdf.ln(10)

    frames = [evaluar_westgard(df_all[df_all["Analito"]==an].copy()) for an in analitos]
    df_ev  = pd.concat(frames)
    total_pts  = len(df_ev)
    total_rojo = int((df_ev["Estado"]=="Rojo").sum())
    total_amb  = int((df_ev["Estado"]=="Ámbar").sum())
    total_ok   = int((df_ev["Estado"]=="Verde").sum())
    f_ini = df_ev["Fecha"].min().strftime("%d/%m/%Y")
    f_fin = df_ev["Fecha"].max().strftime("%d/%m/%Y")

    def sec(txt):
        pdf.set_font("Helvetica","B",12); pdf.set_text_color(0,102,204)
        pdf.cell(0, 8, txt, ln=True)
        pdf.set_draw_color(0,102,204); pdf.line(10,pdf.get_y(),200,pdf.get_y()); pdf.ln(3)

    sec("1. Resumen Ejecutivo")
    pdf.set_font("Helvetica","",10); pdf.set_text_color(33,37,41)
    for line in [f"Periodo: {f_ini} a {f_fin}",
                 f"Total mediciones: {total_pts}",
                 f"Puntos en Verde: {total_ok} ({100*total_ok//total_pts if total_pts else 0}%)",
                 f"Alertas Ambar: {total_amb}",
                 f"Alertas Rojo: {total_rojo}"]:
        pdf.cell(0,7,line,ln=True)
    pdf.ln(4)

    sec("2. Estado por Analito  [Z = (x - media) / SD]")
    col_w=[55,28,24,24,30,25]; hdrs=["Analito","Valor","Z-Score","Score","Regla","Estado"]
    pdf.set_fill_color(240,242,245); pdf.set_text_color(73,80,87)
    pdf.set_font("Helvetica","B",9)
    for w,h in zip(col_w,hdrs): pdf.cell(w,8,h,border=1,fill=True)
    pdf.ln()
    for an in analitos:
        sub = evaluar_westgard(df_all[df_all["Analito"]==an].copy())
        u   = sub.iloc[-1]
        if u["Estado"]=="Rojo":   pdf.set_fill_color(252,232,232); pdf.set_text_color(155,28,28)
        elif u["Estado"]=="Ámbar":pdf.set_fill_color(255,243,205); pdf.set_text_color(133,100,4)
        else:                      pdf.set_fill_color(209,247,231); pdf.set_text_color(10,102,64)
        pdf.set_font("Helvetica","",9)
        for w,v in zip(col_w,[an[:28],str(u["Valor"]),f"{u['Z_Score']:+.2f}",
                               f"{int(u['Score_Riesgo'])}/100",u["Regla_Violada"],u["Estado"]]):
            pdf.cell(w,7,str(v),border=1,fill=True)
        pdf.ln()
    pdf.ln(5)

    viol = df_ev[df_ev["Estado"]!="Verde"].copy()
    sec(f"3. Detalle de Violaciones ({len(viol)})")
    if viol.empty:
        pdf.set_font("Helvetica","I",10); pdf.set_text_color(10,102,64)
        pdf.cell(0,7,"Sin violaciones en el periodo.",ln=True)
    else:
        vc=[28,48,22,22,22,24,18]; vhd=["Fecha","Analito","Valor","Z-Score","Regla","Score","Estado"]
        pdf.set_fill_color(240,242,245); pdf.set_text_color(73,80,87)
        pdf.set_font("Helvetica","B",8)
        for w,h in zip(vc,vhd): pdf.cell(w,7,h,border=1,fill=True)
        pdf.ln(); pdf.set_font("Helvetica","",8)
        for _,row in viol.iterrows():
            if row["Estado"]=="Rojo":   pdf.set_fill_color(252,232,232); pdf.set_text_color(155,28,28)
            else:                        pdf.set_fill_color(255,243,205); pdf.set_text_color(133,100,4)
            for w,v in zip(vc,[row["Fecha"].strftime("%d/%m/%Y"),str(row["Analito"])[:22],
                               str(row["Valor"]),f"{row['Z_Score']:+.2f}",
                               row["Regla_Violada"],f"{int(row['Score_Riesgo'])}/100",row["Estado"]]):
                pdf.cell(w,6,str(v),border=1,fill=True)
            pdf.ln()
    pdf.ln(5)

    sec("4. Recomendaciones del Asistente IA")
    pdf.set_font("Helvetica","",10); pdf.set_text_color(33,37,41)
    recs = (["ACCION URGENTE: alertas rojas activas. No liberar resultados de pacientes.",
             "Recalibrar el analizador con material de referencia trazable.",
             "Verificar lote, temperatura y caducidad de reactivos afectados.",
             "Repetir el control tras acciones correctivas antes de reanudar.",
             "Documentar todas las acciones con fecha y responsable."] if total_rojo > 0
            else ["Alertas de advertencia detectadas. Monitoreo estrecho recomendado.",
                  "Verificar cadena de frio y condiciones de almacenamiento.",
                  "Registrar observaciones en el sistema de trazabilidad."] if total_amb > 0
            else ["El laboratorio opera dentro de los criterios de Westgard.",
                  "Continuar con la rutina de control de calidad diaria.",
                  "Revisar periodicamente los limites con datos actualizados."])
    for i,r in enumerate(recs,1): pdf.multi_cell(0,6,f"{i}. {r}"); pdf.ln(1)

    pdf.ln(4)
    pdf.set_draw_color(222,226,230); pdf.line(10,pdf.get_y(),200,pdf.get_y()); pdf.ln(2)
    pdf.set_font("Helvetica","I",8); pdf.set_text_color(108,117,125)
    pdf.cell(0,5,"AIQC v4.0 · Informe automatico · Uso interno del laboratorio",
             ln=True,align="C")
    return bytes(pdf.output())


# ==============================================================
#  6. SIDEBAR
# ==============================================================
with st.sidebar:
    st.markdown('<div class="sb-logo">🔬</div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-title">AIQC</div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-sub">Quality Control · v4.0</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("**📂 Fuente de datos**")
    uploaded = st.file_uploader("CSV o Excel", type=["csv","xlsx","xls"],
        help="Columnas: Fecha, Analito, Valor, Media_Objetivo, SD_Objetivo, Lote (opcional).",
        key="csv_upload")

    if uploaded:
        df_cargado, err = leer_archivo(uploaded)
        if df_cargado is not None:
            df_all   = df_cargado; data_src = f"📄 {uploaded.name}"
            st.markdown(f'<div class="data-pill">✅ <b>{uploaded.name}</b><br>'
                        f'{len(df_all)} filas · {df_all["Analito"].nunique()} analito(s)</div>',
                        unsafe_allow_html=True)
        else:
            st.error(err); df_all = build_demo(); data_src = "Demo (archivo inválido)"
    else:
        df_all = build_demo(); data_src = "🔬 Modo Demo"
        st.caption("Usando datos simulados de demostración.")

    st.markdown("---")
    analito = st.selectbox("Analito activo", options=sorted(df_all["Analito"].unique()), key="sel_analito")

    fechas_d = sorted(df_all["Fecha"].dropna().unique())
    if len(fechas_d) >= 2:
        f_min = st.date_input("Desde", value=pd.Timestamp(fechas_d[0]).date(),
                              min_value=pd.Timestamp(fechas_d[0]).date(),
                              max_value=pd.Timestamp(fechas_d[-1]).date(), key="f1")
        f_max = st.date_input("Hasta", value=pd.Timestamp(fechas_d[-1]).date(),
                              min_value=pd.Timestamp(fechas_d[0]).date(),
                              max_value=pd.Timestamp(fechas_d[-1]).date(), key="f2")
    else:
        f_min = f_max = pd.Timestamp(fechas_d[0]).date() if fechas_d else datetime.today().date()

    st.markdown("<br>", unsafe_allow_html=True)

    # LEDs de estado rápido
    st.markdown("**Estado del laboratorio**")
    for an in sorted(df_all["Analito"].unique()):
        sub = evaluar_westgard(df_all[df_all["Analito"]==an].copy())
        est = sub.iloc[-1]["Estado"]
        led = {"Verde":"🟢","Ámbar":"🟡","Rojo":"🔴"}.get(est,"⚪")
        st.markdown(f"{led} **{an}** — {est}")

    st.markdown("---")
    if st.button("Cerrar sesión", use_container_width=True):
        st.session_state["auth"] = False; st.rerun()
    st.caption(f"Fuente: {data_src}")


# ==============================================================
#  7. DATOS ACTIVOS
# ==============================================================
df_raw = df_all[
    (df_all["Analito"] == analito) &
    (df_all["Fecha"] >= pd.Timestamp(f_min)) &
    (df_all["Fecha"] <= pd.Timestamp(f_max))
].copy()
df_series   = evaluar_westgard(df_raw)
ultima      = df_series.iloc[-1] if not df_series.empty else None
analitos_ls = sorted(df_all["Analito"].unique())


# ==============================================================
#  8. CABECERA
# ==============================================================
c1, c2 = st.columns([4, 1])
with c1:
    st.markdown(f"## 🔬 AIQC – Control de Calidad")
    st.markdown(
        f"<span style='color:#6C757D;font-size:.9rem'>"
        f"<b>Analito:</b> {analito} &nbsp;·&nbsp; "
        f"<b>Período:</b> {f_min.strftime('%d/%m/%Y')} → {f_max.strftime('%d/%m/%Y')} &nbsp;·&nbsp; "
        f"<b>Fuente:</b> {data_src}</span>", unsafe_allow_html=True)
with c2:
    if ultima is not None:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(estado_badge(ultima["Estado"]), unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)


# ==============================================================
#  9. TABS
# ==============================================================
tab_dash, tab_chat, tab_log = st.tabs(
    ["📊  Dashboard", "🤖  Asistente IA", "📋  Registro de Acciones"])


# ── TAB 1: DASHBOARD ─────────────────────────────────────────
with tab_dash:
    if df_series.empty or ultima is None:
        st.warning("No hay datos para el rango seleccionado.")
    else:
        score  = int(ultima["Score_Riesgo"])
        zscore = round(ultima["Z_Score"], 2)
        risk_c = {"Verde":"#1A7F4B","Ámbar":"#856404","Rojo":"#9B1C1C"}.get(ultima["Estado"],"#1A7F4B")

        # KPI cards
        k1,k2,k3,k4,k5 = st.columns(5)
        kpi_data = [
            (k1, f"{ultima['Valor']}",          "Valor Actual",     "#0066CC",  "Última medición"),
            (k2, f"{ultima['Media_Objetivo']}", "Media Objetivo",   "#5A6ACA",  "μ objetivo"),
            (k3, f"±{ultima['SD_Objetivo']}",   "SD Objetivo",      "#7952B3",  "σ objetivo"),
            (k4, f"{zscore:+.2f}σ",            "Z-Score Actual",   "#C0392B" if abs(zscore)>=2 else "#1A7F4B", "Z=(x-μ)/σ"),
            (k5, f"{score}/100",               "Score de Riesgo",  risk_c,     ultima["Estado"]),
        ]
        for col, (val, lbl, color, sub) in zip([k1,k2,k3,k4,k5],
                [(v,l,c,s) for _,v,l,c,s in kpi_data]):
            with col:
                st.markdown(
                    f'<div class="kpi-card">'
                    f'<div class="kpi-val" style="color:{color}">{val}</div>'
                    f'<div class="kpi-lbl">{lbl}</div>'
                    f'<div class="kpi-sub">{sub}</div>'
                    f'</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Gráfico Levey-Jennings – plotly_white
        m, sd = ultima["Media_Objetivo"], ultima["SD_Objetivo"]

        fig = go.Figure()

        # Zonas de fondo – colores pastel sobre blanco
        fig.add_hrect(y0=m+2*sd, y1=m+3*sd, fillcolor="rgba(220,53,69,.07)",  line_width=0)
        fig.add_hrect(y0=m-3*sd, y1=m-2*sd, fillcolor="rgba(220,53,69,.07)",  line_width=0)
        fig.add_hrect(y0=m+sd,   y1=m+2*sd, fillcolor="rgba(255,193,7,.06)",  line_width=0)
        fig.add_hrect(y0=m-2*sd, y1=m-sd,   fillcolor="rgba(255,193,7,.06)",  line_width=0)
        fig.add_hrect(y0=m-sd,   y1=m+sd,   fillcolor="rgba(25,135,84,.04)",  line_width=0)

        # Líneas de referencia
        for y_v,color,width,dash,name in [
            (m,       "#198754",2.0,"solid","Media"),
            (m+sd,    "#ADB5BD",1.0,"dash", "+1 SD"),
            (m-sd,    "#ADB5BD",1.0,"dash", "−1 SD"),
            (m+2*sd,  "#FD7E14",1.4,"dash", "+2 SD"),
            (m-2*sd,  "#FD7E14",1.4,"dash", "−2 SD"),
            (m+3*sd,  "#DC3545",1.8,"dot",  "+3 SD"),
            (m-3*sd,  "#DC3545",1.8,"dot",  "−3 SD"),
        ]:
            fig.add_hline(y=y_v, line_color=color, line_width=width,
                          line_dash=dash, annotation_text=name,
                          annotation_position="right",
                          annotation_font=dict(color=color, size=11, family="Inter"))

        # Línea de tendencia
        fig.add_trace(go.Scatter(
            x=df_series["Fecha"], y=df_series["Valor"],
            mode="lines", line=dict(color="#CED4DA", width=1.5),
            showlegend=False, hoverinfo="skip"))

        # Puntos coloreados
        color_map = {"Verde":"#198754","Ámbar":"#FD7E14","Rojo":"#DC3545"}
        for estado, color in color_map.items():
            sub_df = df_series[df_series["Estado"]==estado]
            if sub_df.empty: continue
            fig.add_trace(go.Scatter(
                x=sub_df["Fecha"], y=sub_df["Valor"],
                mode="markers", name=estado,
                marker=dict(size=11, color=color,
                            line=dict(color="#FFFFFF", width=2)),
                hovertemplate=(
                    f"<b>%{{x|%d %b %Y}}</b><br>"
                    f"Valor: <b>%{{y}}</b><br>"
                    f"Estado: {estado}<extra></extra>"
                ),
            ))

        fig.update_layout(
            template="plotly_white",
            title=dict(text=f"Gráfico de Levey-Jennings — {analito}",
                       font=dict(size=15, color="#212529", family="Inter")),
            paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
            font=dict(color="#495057", family="Inter"),
            legend=dict(orientation="h", y=1.06, x=1, xanchor="right",
                        bgcolor="rgba(0,0,0,0)", font=dict(size=12)),
            xaxis=dict(gridcolor="#F1F3F5", linecolor="#DEE2E6",
                       tickformat="%d %b", title="Fecha",
                       tickfont=dict(size=11, color="#6C757D")),
            yaxis=dict(gridcolor="#F1F3F5", linecolor="#DEE2E6",
                       title="Valor",
                       tickfont=dict(size=11, color="#6C757D")),
            height=460,
            margin=dict(l=10, r=130, t=60, b=10),
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)

        # Últimas 7 mediciones
        st.markdown('<div class="sec-head">Últimas 7 mediciones</div>', unsafe_allow_html=True)
        tail = df_series.tail(7)[["Fecha","Valor","Z_Score","Regla_Violada","Score_Riesgo","Estado","Lote"]].copy()
        tail["Fecha"]  = tail["Fecha"].dt.strftime("%d/%m/%Y")
        tail["Estado"] = tail["Estado"].apply(estado_badge)
        st.write(tail.rename(columns={"Z_Score":"Z-Score","Regla_Violada":"Regla",
                                       "Score_Riesgo":"Score"})
                     .to_html(escape=False, index=False), unsafe_allow_html=True)


# ── TAB 2: ASISTENTE IA ───────────────────────────────────────
with tab_chat:
    st.markdown("### 🤖 Asistente AIQC")
    st.caption("Consulta en lenguaje natural. El asistente analiza los datos actuales del laboratorio.")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role":"assistant","content":(
            "¡Hola! Soy el **Asistente AIQC**. Analizo los controles de calidad "
            "usando la fórmula **Z = (x − μ) / σ** y las reglas de Westgard.\n\n"
            "Prueba a preguntarme:\n"
            "- *¿Cómo está el ALT?*\n- *¿Hay alertas activas?*\n"
            "- *¿Qué significa la regla 2_2s?*\n- *Dame un resumen del laboratorio*"
        )}]

    def _stats(an: str) -> dict:
        sub = evaluar_westgard(
            df_all[(df_all["Analito"]==an) &
                   (df_all["Fecha"]>=pd.Timestamp(f_min)) &
                   (df_all["Fecha"]<=pd.Timestamp(f_max))].copy())
        if sub.empty: return {}
        u = sub.iloc[-1]
        return {"valor":u["Valor"],"media":u["Media_Objetivo"],"sd":u["SD_Objetivo"],
                "z":round(u["Z_Score"],3),"score":int(u["Score_Riesgo"]),
                "estado":u["Estado"],"regla":u["Regla_Violada"],
                "n_rojo":int((sub["Estado"]=="Rojo").sum()),
                "n_amb":int((sub["Estado"]=="Ámbar").sum())}

    def ia_responde(preg: str) -> str:
        p = preg.lower()
        all_stats = {an: _stats(an) for an in analitos_ls}

        mencionado = None
        for an in analitos_ls:
            tokens = [t for t in an.lower().replace("("," ").replace(")","").split() if len(t)>2]
            if any(t in p for t in tokens):
                mencionado = an; break

        if mencionado:
            d = all_stats.get(mencionado, {})
            if not d: return f"Sin datos de **{mencionado}** en el período seleccionado."
            zf = f"Z = ({d['valor']} − {d['media']}) / {d['sd']} = **{d['z']:+.3f}σ**"
            if d["n_rojo"] > 0 or d["n_amb"] > 0:
                return (f"📊 **Análisis de {mencionado}:**\n\n"
                        f"- Último valor: **{d['valor']}** · Regla activa: `{d['regla']}`\n"
                        f"- Cálculo Z-Score: {zf}\n"
                        f"- Score de riesgo: **{d['score']}/100** · Estado: {d['estado']}\n"
                        f"- Alertas en período: 🔴 {d['n_rojo']} roja(s) · 🟠 {d['n_amb']} ámbar\n\n"
                        f"**Recomendaciones:**\n"
                        f"1. Revisar calibración del analizador.\n"
                        f"2. Verificar lote y temperatura del reactivo.\n"
                        f"3. No liberar resultados hasta restablecer el control.\n"
                        f"4. Registrar la acción en el Tab 3.")
            return (f"✅ **{mencionado} en control.**\n\n"
                    f"- Último valor: {d['valor']}\n- {zf}\n"
                    f"- Score: {d['score']}/100 · {d['estado']}")

        if any(w in p for w in ["alerta","alertas","error","activa","critico"]):
            tr = sum(d.get("n_rojo",0) for d in all_stats.values())
            ta = sum(d.get("n_amb",0)  for d in all_stats.values())
            if tr+ta == 0: return "✅ Sin alertas activas. Todos los analitos están bajo control."
            tbl = "| Analito | 🔴 Rojo | 🟠 Ámbar |\n|---|---|---|\n"
            for an,d in all_stats.items(): tbl += f"| {an} | {d.get('n_rojo',0)} | {d.get('n_amb',0)} |\n"
            return f"**Alertas activas:**\n\n{tbl}"

        if any(w in p for w in ["westgard","regla","1_3s","2_2s","4_1s"]):
            return ("📏 **Reglas de Westgard:**\n\n"
                    "| Regla | Criterio | Tipo |\n|---|---|---|\n"
                    "| **1_3s** | 1 punto fuera ±3SD | Aleatorio grave |\n"
                    "| **2_2s** | 2 consecutivos fuera ±2SD (mismo lado) | Sistemático |\n"
                    "| **4_1s** | 4 consecutivos fuera ±1SD (mismo lado) | Deriva |\n"
                    "| **1_2s** | 1 punto fuera ±2SD | Advertencia |\n\n"
                    "Fórmula base: **Z = (x − μ) / σ**")

        if any(w in p for w in ["z-score","zscore","formula","calcular"]):
            lines = [f"- **{an}**: Z = ({d['valor']} − {d['media']}) / {d['sd']} = **{d['z']:+.3f}σ** → {d['estado']}"
                     for an,d in all_stats.items() if d]
            return "📐 **Z-Score por analito:**\n\nFórmula: **Z = (x − μ) / σ**\n\n" + "\n".join(lines)

        if any(w in p for w in ["cv","variacion","imprecision","precision"]):
            lines = [f"- **{an}**: CV = {round(d['sd']/d['media']*100,2)}%" for an,d in all_stats.items() if d]
            return "📐 **Coeficiente de Variación (CV%):**\n\n" + "\n".join(lines) + "\n\nAceptable: ≤5% (CLIA)."

        if any(w in p for w in ["hacer","accion","correcti","solucion","recomenda"]):
            tr = sum(d.get("n_rojo",0) for d in all_stats.values())
            if tr > 0:
                return ("🛠️ **Protocolo correctivo (alerta roja):**\n\n"
                        "1. Bloquear liberación de resultados del analito afectado.\n"
                        "2. Repetir el control con vial nuevo.\n"
                        "3. Recalibrar con material de referencia trazable.\n"
                        "4. Verificar temperatura de almacenamiento de reactivos.\n"
                        "5. Registrar todas las acciones en el Tab 3.")
            return "✅ Sin acciones urgentes. Continúe con el plan de QC habitual."

        if any(w in p for w in ["resumen","estado","laboratorio","informe","global"]):
            tbl = "| Analito | Valor | Z-Score | Score | Estado |\n|---|---|---|---|---|\n"
            for an,d in all_stats.items():
                if d: tbl += f"| {an} | {d['valor']} | {d['z']:+.2f}σ | {d['score']}/100 | {d['estado']} |\n"
            return f"📋 **Resumen del laboratorio:**\n\n{tbl}"

        if any(w in p for w in ["ayuda","puedes","capacidad","opciones"]):
            return ("🤖 **Capacidades:**\n\n"
                    "- Estado de analito: *¿Cómo está el ALT?*\n"
                    "- Alertas: *¿Hay alertas activas?*\n"
                    "- Reglas Westgard: *¿Qué es la regla 2_2s?*\n"
                    "- Z-Score con fórmula: *Calcula el Z del Potasio*\n"
                    "- Acciones: *¿Qué hago con una alerta roja?*\n"
                    "- Resumen global: *Dame un informe del laboratorio*")

        return "No encontré una respuesta específica. Escribe *ayuda* para ver mis capacidades."

    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"]=="assistant" else "👤"):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Escribe tu consulta…"):
        st.session_state["messages"].append({"role":"user","content":prompt})
        with st.chat_message("user", avatar="👤"): st.markdown(prompt)
        resp = ia_responde(prompt)
        st.session_state["messages"].append({"role":"assistant","content":resp})
        with st.chat_message("assistant", avatar="🤖"): st.markdown(resp)

    if st.button("🗑️ Nueva conversación", key="clr"):
        st.session_state["messages"] = [st.session_state["messages"][0]]; st.rerun()


# ── TAB 3: REGISTRO + PDF ─────────────────────────────────────
with tab_log:
    col_ttl, col_pdf = st.columns([3,1])
    with col_ttl:
        st.markdown("### 📋 Registro de Incidencias y Trazabilidad")
        st.caption("Marca cada alerta cuando se haya gestionado la acción correctiva.")
    with col_pdf:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📄 Descargar Reporte PDF", use_container_width=True, type="primary"):
            with st.spinner("Generando informe…"):
                try:
                    pdf_bytes = generar_pdf(df_all, analitos_ls, data_src)
                    fname = f"AIQC_Informe_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                    st.download_button("⬇️ Guardar PDF", data=pdf_bytes,
                                       file_name=fname, mime="application/pdf",
                                       use_container_width=True)
                    st.success("✅ Informe generado.")
                except Exception as e:
                    st.error(f"Error: {e}  →  pip install fpdf2")

    # Tabla de violaciones
    frames3 = [evaluar_westgard(
        df_all[(df_all["Analito"]==an) &
               (df_all["Fecha"]>=pd.Timestamp(f_min)) &
               (df_all["Fecha"]<=pd.Timestamp(f_max))].copy())
               for an in analitos_ls]
    df_full3 = pd.concat(frames3)
    df_log   = df_full3[df_full3["Estado"]!="Verde"].copy().reset_index(drop=True)

    if df_log.empty:
        st.success("✅ Sin violaciones en el período seleccionado.")
    else:
        if "acciones_log" not in st.session_state:
            st.session_state["acciones_log"] = {}

        hcols = st.columns([1.6,2.2,1.2,1.3,1.4,1.6,1.6,1.4])
        for c,lbl in zip(hcols,["📅 Fecha","🔬 Analito","Valor","Z-Score",
                                  "Regla","Score","Estado","✅ Acción"]):
            c.markdown(f"**{lbl}**")
        st.markdown("<hr>", unsafe_allow_html=True)

        for idx, row in df_log.iterrows():
            key   = f"{row['Fecha'].date()}_{row['Analito']}_{idx}"
            rcols = st.columns([1.6,2.2,1.2,1.3,1.4,1.6,1.6,1.4])
            rcols[0].write(row["Fecha"].strftime("%d/%m/%Y"))
            rcols[1].write(row["Analito"])
            rcols[2].write(str(row["Valor"]))
            rcols[3].write(f"{row['Z_Score']:+.2f}σ")
            rcols[4].write(row["Regla_Violada"])
            rcols[5].write(f"{int(row['Score_Riesgo'])}/100")
            rcols[6].markdown(estado_badge(row["Estado"]), unsafe_allow_html=True)
            prev  = st.session_state["acciones_log"].get(key, False)
            nuevo = rcols[7].checkbox("Hecha", value=prev, key=f"accion_{key}")
            st.session_state["acciones_log"][key] = nuevo

        st.markdown("<hr>", unsafe_allow_html=True)
        total  = len(df_log)
        hechas = sum(v for v in st.session_state["acciones_log"].values())
        pend   = total - hechas

        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Total violaciones",  total)
        m2.metric("Acciones tomadas ✅", hechas)
        m3.metric("Pendientes ⏳",       pend)
        m4.metric("% completado",       f"{int(hechas/total*100) if total else 0}%")

        if hechas == total:
            st.success("🎉 Trazabilidad completa. Todas las alertas han sido gestionadas.")
        elif pend:
            st.warning(f"⚠️ {pend} violación(es) pendiente(s) de acción.")
