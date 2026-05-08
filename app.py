# ==============================================================
#  AIQC – Artificial Intelligence for Quality Control
#  Versión: 3.0 DEFINITIVA
#  Deploy:  streamlit run app.py
#  Deps:    pip install streamlit plotly pandas numpy fpdf2 openpyxl
# ==============================================================

import streamlit as st
# --- FORZAR TEMA CLARO (COPIAR DESDE AQUÍ) ---
st.markdown("""
    <style>
    /* 1. FONDO GENERAL Y CONTENEDORES */
    /* Forzamos el fondo de toda la página a blanco hueso profesional */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #F8F9FA !important;
    }

    /* 2. TEXTO GLOBAL */
    /* Ponemos todas las letras en gris grafito oscuro para máxima legibilidad */
    html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, span {
        color: #212529 !important;
    }

    /* 3. BARRA LATERAL */
    /* Un tono gris muy suave para diferenciarla del fondo */
    [data-testid="stSidebar"] {
        background-color: #F0F2F6 !important;
        border-right: 1px solid #E0E0E0;
    }

    /* 4. TARJETAS DE MÉTRICAS (KPIs) */
    /* Tus cuadros negros ahora serán blancos con un borde elegante */
    div[data-testid="metric-container"], .stMetric {
        background-color: #FFFFFF !important;
        border: 1px solid #DEE2E6 !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        padding: 15px !important;
    }
    
    /* Aseguramos que los números de las tarjetas sean oscuros */
    [data-testid="stMetricValue"] {
        color: #000000 !important;
    }

    /* 5. PESTAÑAS (TABS) */
    /* Para que las pestañas de 'Dashboard', 'IA', etc. no se vean negras */
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        color: #495057 !important;
    }
    button[aria-selected="true"] {
        color: #007BFF !important; /* Color azul para la pestaña activa */
        border-bottom-color: #007BFF !important;
    }
    </style>
    """, unsafe_allow_html=True)
# --- FINAL DEL BLOQUE ---
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from io import BytesIO
from fpdf import FPDF

# ── Configuración de página ────────────────────────────────
st.set_page_config(
    page_title="AIQC – Quality Control AI",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================
#  ESTILOS GLOBALES
# ==============================================================
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    background-color: #080c14; color: #c9d1e0;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
[data-testid="stSidebar"] {
    background-color: #0d1120; border-right: 1px solid #1e2740;
}
/* Login */
.login-wrap {
    max-width: 420px; margin: 60px auto;
    background: #0d1120; border: 1px solid #1e2740;
    border-radius: 18px; padding: 44px 40px;
    box-shadow: 0 20px 60px rgba(0,0,0,.65);
}
.login-logo  { font-size: 3.2rem; text-align: center; margin-bottom: 4px; }
.login-title {
    text-align: center; font-size: 1.7rem; font-weight: 800;
    background: linear-gradient(90deg,#38bdf8,#818cf8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 4px;
}
.login-sub { text-align:center; color:#4a5568; font-size:.86rem; margin-bottom:28px; }
/* KPI */
.kpi { background:#0d1120; border:1px solid #1e2740; border-radius:14px;
       padding:20px 16px; text-align:center; transition:border-color .25s; }
.kpi:hover { border-color:#38bdf8; }
.kpi-val { font-size:2rem; font-weight:800; letter-spacing:-.5px; }
.kpi-lbl { font-size:.76rem; color:#4a5568; margin-top:6px;
           text-transform:uppercase; letter-spacing:.07em; }
/* Badges */
.badge { display:inline-block; padding:3px 12px; border-radius:20px;
         font-size:.78rem; font-weight:600; }
.badge-green { background:#052e16; color:#4ade80; border:1px solid #166534; }
.badge-amber { background:#431407; color:#fb923c; border:1px solid #9a3412; }
.badge-red   { background:#450a0a; color:#f87171; border:1px solid #991b1b; }
/* Section title */
.sec-title { font-size:1.05rem; font-weight:600; color:#38bdf8;
             border-left:3px solid #38bdf8; padding-left:10px;
             margin:22px 0 12px 0; }
/* Info box */
.info-box { background:#0d1120; border:1px solid #1e2740; border-radius:10px;
            padding:10px 14px; font-size:.82rem; color:#94a3b8; margin-top:6px; }
/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap:8px; }
.stTabs [data-baseweb="tab"] {
    background:#0d1120; border:1px solid #1e2740;
    border-radius:8px 8px 0 0; color:#4a5568;
    padding:8px 22px; font-weight:600; }
.stTabs [aria-selected="true"] {
    background:#111827 !important; color:#38bdf8 !important;
    border-bottom-color:#111827 !important; }
/* Sidebar branding */
.sb-logo  { text-align:center; font-size:2.8rem; margin-bottom:2px; }
.sb-title { text-align:center; font-size:1.1rem; font-weight:700;
            background:linear-gradient(90deg,#38bdf8,#818cf8);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent;
            margin-bottom:14px; }
</style>
""", unsafe_allow_html=True)


# ==============================================================
#  1. AUTENTICACIÓN
# ==============================================================
VALID_USER, VALID_PASS = "admin", "qc2026"

def render_login():
    st.markdown("""
    <div class="login-wrap">
        <div class="login-logo">🔬</div>
        <div class="login-title">AIQC</div>
        <div class="login-sub">Artificial Intelligence for Quality Control · v3.0</div>
    </div>""", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.8, 1])
    with mid:
        user = st.text_input("Usuario",    placeholder="admin",  key="_u")
        pwd  = st.text_input("Contraseña", type="password",
                             placeholder="••••••", key="_p")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Entrar →", use_container_width=True, type="primary"):
            if user == VALID_USER and pwd == VALID_PASS:
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas.")

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
    # Potasio – proceso estable
    for i, d in enumerate(dates):
        rows.append({"Fecha": d, "Analito": "Potasio (K+)",
                     "Valor": round(np.random.normal(4.5, 0.15 * 0.85), 3),
                     "Media_Objetivo": 4.5, "SD_Objetivo": 0.15, "Lote": lotes[i]})
    # ALT – deriva en últimos 5 días
    for i, d in enumerate(dates):
        drift = 2.5 * (i - 24) * 0.65 if i >= 25 else 0.0
        rows.append({"Fecha": d, "Analito": "ALT (Transaminasa)",
                     "Valor": round(np.random.normal(35.0 + drift, 2.5), 2),
                     "Media_Objetivo": 35.0, "SD_Objetivo": 2.5, "Lote": lotes[i]})
    return pd.DataFrame(rows)


# ==============================================================
#  3. CARGA DE CSV / XLSX – FLEXIBLE
# ==============================================================
# Sinónimos por columna interna (minúsculas, sin tildes)
COL_SYNONYMS = {
    "Fecha":          ["fecha","date","dia","dia","timestamp","time","datetime","f"],
    "Analito":        ["analito","analyte","test","prueba","parametro","parametro",
                       "analisis","examen","magnitud"],
    "Valor":          ["valor","value","resultado","result","medicion","medida",
                       "concentracion","concentración","v"],
    "Media_Objetivo": ["media_objetivo","media","mean","target","objetivo",
                       "mean_target","valor_objetivo","x_bar","xbar"],
    "SD_Objetivo":    ["sd_objetivo","sd","desviacion","desviación","std","std_dev",
                       "sigma","s","sd objetivo","desvest"],
    "Lote":           ["lote","lot","batch","lote_reactivo","reactivo","kit"],
}

def _norm(s: str) -> str:
    """Normaliza string: minúsculas, sin tildes, sin espacios extra."""
    trans = str.maketrans("áéíóúàèìòùäëïöüÁÉÍÓÚÀÈÌÒÙ","aeiouaeiouaeiouAEIOUAEIOU")
    return s.lower().strip().translate(trans)

def normalizar_df(df: pd.DataFrame) -> tuple[pd.DataFrame | None, str]:
    """
    Renombra columnas al esquema interno usando coincidencia fuzzy.
    Devuelve (df_normalizado, mensaje_error).
    """
    df_n  = {_norm(c): c for c in df.columns}
    rename = {}

    for interno, sinonimos in COL_SYNONYMS.items():
        for s in sinonimos:
            if s in df_n:
                rename[df_n[s]] = interno
                break
        # Fallback: coincidencia parcial
        if interno not in rename.values():
            for col_norm, col_orig in df_n.items():
                if any(s in col_norm or col_norm in s for s in sinonimos):
                    rename[col_orig] = interno
                    break

    df2 = df.rename(columns=rename)
    obligatorias = ["Fecha", "Analito", "Valor", "Media_Objetivo", "SD_Objetivo"]
    faltan = [c for c in obligatorias if c not in df2.columns]
    if faltan:
        return None, (f"No se encontraron las columnas: {', '.join(faltan)}. "
                      f"Columnas detectadas: {list(df.columns)}")

    if "Lote" not in df2.columns:
        df2["Lote"] = "N/A"

    df2["Fecha"]          = pd.to_datetime(df2["Fecha"], dayfirst=True, errors="coerce")
    df2["Valor"]          = pd.to_numeric(df2["Valor"],          errors="coerce")
    df2["Media_Objetivo"] = pd.to_numeric(df2["Media_Objetivo"],  errors="coerce")
    df2["SD_Objetivo"]    = pd.to_numeric(df2["SD_Objetivo"],     errors="coerce")
    df2 = df2.dropna(subset=obligatorias)

    if df2.empty:
        return None, "El archivo no contiene filas válidas tras la limpieza."

    return df2[obligatorias + ["Lote"]].reset_index(drop=True), ""


def leer_archivo(uploaded) -> tuple[pd.DataFrame | None, str]:
    name = uploaded.name.lower()
    try:
        if name.endswith(".csv"):
            raw = pd.read_csv(uploaded, sep=None, engine="python")
        elif name.endswith((".xlsx", ".xls")):
            raw = pd.read_excel(uploaded)
        else:
            return None, "Formato no soportado. Usa CSV o Excel (.xlsx/.xls)."
        return normalizar_df(raw)
    except Exception as e:
        return None, f"Error al leer el archivo: {e}"


# ==============================================================
#  4. LÓGICA DE ALERTAS – WESTGARD
# ==============================================================
def evaluar_westgard(serie: pd.DataFrame) -> pd.DataFrame:
    """Evalúa reglas 1_3s, 2_2s, 4_1s y asigna Z-Score, Score y Estado."""
    df = serie.copy().sort_values("Fecha").reset_index(drop=True)
    df["Z_Score"]       = (df["Valor"] - df["Media_Objetivo"]) / df["SD_Objetivo"]
    df["Regla_Violada"] = "—"
    df["Score_Riesgo"]  = 0
    df["Estado"]        = "Verde"

    for i in range(len(df)):
        z = df.at[i, "Z_Score"]

        # 1_3s: un punto fuera ±3SD → error aleatorio grave
        if abs(z) >= 3.0:
            df.at[i, "Regla_Violada"] = "1_3s"
            df.at[i, "Score_Riesgo"]  = 90
            df.at[i, "Estado"]        = "Rojo"
            continue

        # 2_2s: dos consecutivos fuera ±2SD en el mismo lado → error sistemático
        if i >= 1:
            zp = df.at[i-1, "Z_Score"]
            if abs(z) >= 2.0 and abs(zp) >= 2.0 and np.sign(z) == np.sign(zp):
                df.at[i, "Regla_Violada"] = "2_2s"
                df.at[i, "Score_Riesgo"]  = 75
                df.at[i, "Estado"]        = "Rojo"
                continue

        # 4_1s: cuatro consecutivos fuera ±1SD en el mismo lado → deriva
        if i >= 3:
            w = df.loc[i-3:i, "Z_Score"].values
            if all(abs(x) >= 1.0 for x in w) and len(set(np.sign(w))) == 1:
                df.at[i, "Regla_Violada"] = "4_1s"
                df.at[i, "Score_Riesgo"]  = 60
                df.at[i, "Estado"]        = "Ámbar"
                continue

        # 1_2s: advertencia preventiva
        if abs(z) >= 2.0:
            df.at[i, "Regla_Violada"] = "1_2s (warn)"
            df.at[i, "Score_Riesgo"]  = 45
            df.at[i, "Estado"]        = "Ámbar"
            continue

        df.at[i, "Score_Riesgo"] = max(0, int(abs(z) * 18))

    return df


def estado_badge(e: str) -> str:
    cls = {"Verde":"badge-green","Ámbar":"badge-amber","Rojo":"badge-red"}.get(e,"badge-green")
    ico = {"Verde":"✅","Ámbar":"⚠️","Rojo":"🔴"}.get(e,"✅")
    return f'<span class="badge {cls}">{ico} {e}</span>'


# ==============================================================
#  5. GENERADOR DE INFORME PDF
# ==============================================================
def generar_pdf(df_all: pd.DataFrame, analitos: list, fuente: str) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Encabezado
    pdf.set_fill_color(13, 17, 32)
    pdf.rect(0, 0, 210, 40, "F")
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(56, 189, 248)
    pdf.ln(6)
    pdf.cell(0, 10, "AIQC - Informe de Incidencias de Calidad", ln=True, align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(148, 163, 184)
    pdf.cell(0, 6,
             f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}  |  "
             f"Fuente: {fuente}  |  Analitos: {', '.join(analitos)}",
             ln=True, align="C")
    pdf.ln(10)

    # Evaluar todos los analitos
    frames = [evaluar_westgard(df_all[df_all["Analito"]==an].copy()) for an in analitos]
    df_ev  = pd.concat(frames)
    total_pts  = len(df_ev)
    total_rojo = int((df_ev["Estado"]=="Rojo").sum())
    total_amb  = int((df_ev["Estado"]=="Ámbar").sum())
    total_ok   = int((df_ev["Estado"]=="Verde").sum())
    f_ini = df_ev["Fecha"].min().strftime("%d/%m/%Y")
    f_fin = df_ev["Fecha"].max().strftime("%d/%m/%Y")

    def sec_title(txt):
        pdf.set_font("Helvetica","B",13)
        pdf.set_text_color(56,189,248)
        pdf.cell(0,8,txt,ln=True)
        pdf.set_draw_color(56,189,248)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)

    # 1. Resumen ejecutivo
    sec_title("1. Resumen Ejecutivo")
    pdf.set_font("Helvetica","",10)
    pdf.set_text_color(50,50,50)
    for line in [
        f"Periodo analizado  : {f_ini}  a  {f_fin}",
        f"Total mediciones   : {total_pts}",
        f"Puntos en Verde    : {total_ok}  ({100*total_ok//total_pts if total_pts else 0}%)",
        f"Alertas Ambar      : {total_amb}",
        f"Alertas Rojo (crit): {total_rojo}",
    ]:
        pdf.cell(0,7,line,ln=True)
    pdf.ln(4)

    # 2. Estado por analito
    sec_title("2. Estado por Analito (formula Z = (x - media) / SD)")
    col_w  = [55,28,24,24,30,25]
    hdrs   = ["Analito","Ultimo Valor","Z-Score","Score","Regla","Estado"]
    pdf.set_fill_color(13,17,32); pdf.set_text_color(56,189,248)
    pdf.set_font("Helvetica","B",9)
    for w,h in zip(col_w,hdrs):
        pdf.cell(w,8,h,border=1,fill=True)
    pdf.ln()
    for an in analitos:
        sub = evaluar_westgard(df_all[df_all["Analito"]==an].copy())
        u   = sub.iloc[-1]
        if u["Estado"]=="Rojo":
            pdf.set_fill_color(69,10,10);  pdf.set_text_color(248,113,113)
        elif u["Estado"]=="Ámbar":
            pdf.set_fill_color(67,20,7);   pdf.set_text_color(251,146,60)
        else:
            pdf.set_fill_color(5,46,22);   pdf.set_text_color(74,222,128)
        pdf.set_font("Helvetica","",9)
        for w,v in zip(col_w,[an[:28],str(u["Valor"]),
                               f"{u['Z_Score']:+.2f}",
                               f"{int(u['Score_Riesgo'])}/100",
                               u["Regla_Violada"],u["Estado"]]):
            pdf.cell(w,7,str(v),border=1,fill=True)
        pdf.ln()
    pdf.ln(5)

    # 3. Detalle de violaciones
    viol = df_ev[df_ev["Estado"]!="Verde"].copy()
    sec_title(f"3. Detalle de Violaciones ({len(viol)} registros)")
    if viol.empty:
        pdf.set_font("Helvetica","I",10); pdf.set_text_color(74,222,128)
        pdf.cell(0,7,"Sin violaciones en el periodo.",ln=True)
    else:
        vc  = [28,48,22,22,22,24,18]
        vhd = ["Fecha","Analito","Valor","Z-Score","Regla","Score","Estado"]
        pdf.set_fill_color(13,17,32); pdf.set_text_color(56,189,248)
        pdf.set_font("Helvetica","B",8)
        for w,h in zip(vc,vhd):
            pdf.cell(w,7,h,border=1,fill=True)
        pdf.ln()
        pdf.set_font("Helvetica","",8)
        for _,row in viol.iterrows():
            if row["Estado"]=="Rojo":
                pdf.set_fill_color(69,10,10); pdf.set_text_color(248,113,113)
            else:
                pdf.set_fill_color(67,20,7);  pdf.set_text_color(251,146,60)
            for w,v in zip(vc,[
                row["Fecha"].strftime("%d/%m/%Y"),
                str(row["Analito"])[:22],
                str(row["Valor"]),
                f"{row['Z_Score']:+.2f}",
                row["Regla_Violada"],
                f"{int(row['Score_Riesgo'])}/100",
                row["Estado"],
            ]):
                pdf.cell(w,6,str(v),border=1,fill=True)
            pdf.ln()
    pdf.ln(5)

    # 4. Recomendaciones de la IA
    sec_title("4. Recomendaciones del Asistente IA")
    pdf.set_font("Helvetica","",10); pdf.set_text_color(50,50,50)
    if total_rojo > 0:
        recs = [
            "ACCION URGENTE: alertas rojas activas. No liberar resultados de pacientes.",
            "Recalibrar el analizador con material de referencia trazable.",
            "Verificar lote, temperatura y caducidad de reactivos afectados.",
            "Repetir el control tras las acciones correctivas antes de reanudar.",
            "Documentar todas las acciones con fecha y responsable (Tab 3).",
        ]
    elif total_amb > 0:
        recs = [
            "Alertas de advertencia detectadas. Monitoreo estrecho recomendado.",
            "Verificar cadena de frio y condiciones de almacenamiento.",
            "Evaluar tendencia con EWMA si persiste en proximas corridas.",
            "Registrar observaciones en el sistema de trazabilidad.",
        ]
    else:
        recs = [
            "El laboratorio opera dentro de los criterios de Westgard.",
            "Continuar con la rutina de control de calidad diaria.",
            "Revisar periodicamente los limites con datos actualizados.",
        ]
    for i, r in enumerate(recs, 1):
        pdf.multi_cell(0, 6, f"{i}. {r}"); pdf.ln(1)

    # Pie
    pdf.ln(4)
    pdf.set_draw_color(30,39,64); pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(2)
    pdf.set_font("Helvetica","I",8); pdf.set_text_color(120,120,120)
    pdf.cell(0,5,"AIQC v3.0 · Informe automatico · Uso interno del laboratorio",
             ln=True, align="C")
    return bytes(pdf.output())


# ==============================================================
#  6. SIDEBAR
# ==============================================================
with st.sidebar:
    st.markdown('<div class="sb-logo">🔬</div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-title">AIQC · v3.0</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("**📂 Fuente de datos**")
    uploaded = st.file_uploader(
        "Sube CSV o Excel",
        type=["csv","xlsx","xls"],
        help=(
            "Columnas requeridas (nombres flexibles):\n"
            "• Fecha / Date / Dia\n"
            "• Analito / Analyte / Test\n"
            "• Valor / Value / Resultado\n"
            "• Media_Objetivo / Media / Mean / Target\n"
            "• SD_Objetivo / SD / Std / Sigma\n"
            "• Lote / Lot / Batch  (opcional)"
        ),
        key="csv_upload",
    )

    if uploaded:
        df_cargado, err = leer_archivo(uploaded)
        if df_cargado is not None:
            df_all   = df_cargado
            data_src = f"📄 {uploaded.name}"
            st.markdown(
                f'<div class="info-box">✅ <b>{uploaded.name}</b><br>'
                f'{len(df_all)} filas · {df_all["Analito"].nunique()} analito(s)</div>',
                unsafe_allow_html=True)
        else:
            st.error(err)
            df_all   = build_demo()
            data_src = "Demo (archivo inválido)"
    else:
        df_all   = build_demo()
        data_src = "🔬 Modo Demo"
        st.caption("Usando datos simulados de demostración.")

    st.markdown("---")
    analito = st.selectbox("Analito activo",
                           options=sorted(df_all["Analito"].unique()),
                           key="analito_sel")

    # Filtro de fechas
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

    st.markdown("<br>" * 3, unsafe_allow_html=True)
    if st.button("🔒 Cerrar sesión", use_container_width=True):
        st.session_state["auth"] = False
        st.rerun()
    st.markdown("---")
    st.caption(f"Fuente: {data_src}")


# ==============================================================
#  7. DATOS ACTIVOS (con filtro de fechas)
# ==============================================================
df_raw = df_all[
    (df_all["Analito"] == analito) &
    (df_all["Fecha"] >= pd.Timestamp(f_min)) &
    (df_all["Fecha"] <= pd.Timestamp(f_max))
].copy()

df_series   = evaluar_westgard(df_raw)
ultima      = df_series.iloc[-1]  if not df_series.empty else None
analitos_ls = sorted(df_all["Analito"].unique())


# ==============================================================
#  8. CABECERA
# ==============================================================
c1, c2 = st.columns([3,1])
with c1:
    st.markdown("## 🔬 AIQC – Control de Calidad")
    st.markdown(f"**Analito:** `{analito}` &nbsp;|&nbsp; "
                f"**Periodo:** {f_min.strftime('%d/%m/%Y')} → {f_max.strftime('%d/%m/%Y')} "
                f"&nbsp;|&nbsp; **Fuente:** `{data_src}`")
with c2:
    if ultima is not None:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(estado_badge(ultima["Estado"]), unsafe_allow_html=True)
st.markdown("---")


# ==============================================================
#  9. TABS
# ==============================================================
tab_dash, tab_chat, tab_log = st.tabs(
    ["📊  Dashboard", "🤖  Asistente IA", "📋  Registro de Acciones"]
)


# ── TAB 1: DASHBOARD ─────────────────────────────────────────
with tab_dash:
    if df_series.empty or ultima is None:
        st.warning("No hay datos para el rango seleccionado.")
    else:
        score  = int(ultima["Score_Riesgo"])
        zscore = round(ultima["Z_Score"], 2)
        kpi_c  = {"Verde":"#4ade80","Ámbar":"#fb923c","Rojo":"#f87171"}.get(ultima["Estado"],"#4ade80")

        cols_k = st.columns(5)
        kpi_data = [
            (f"{ultima['Valor']}",          "Valor Actual",     "#38bdf8"),
            (f"{ultima['Media_Objetivo']}", "Media Objetivo",   "#818cf8"),
            (f"±{ultima['SD_Objetivo']}",   "SD Objetivo",      "#a78bfa"),
            (f"{zscore:+.2f}σ",            "Z-Score Actual",   "#f472b6"),
            (f"{score}/100",               "Score de Riesgo",  kpi_c),
        ]
        for col, (val, lbl, color) in zip(cols_k, kpi_data):
            with col:
                st.markdown(f'<div class="kpi"><div class="kpi-val" style="color:{color}">'
                            f'{val}</div><div class="kpi-lbl">{lbl}</div></div>',
                            unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        m, sd = ultima["Media_Objetivo"], ultima["SD_Objetivo"]

        fig = go.Figure()
        # Zonas de fondo
        for y0,y1,alpha in [(m+2*sd,m+3*sd,.07),(m-3*sd,m-2*sd,.07),
                             (m+sd,m+2*sd,.04),(m-2*sd,m-sd,.04)]:
            c = "rgba(248,113,113" if abs(y0)>=m+2*sd or abs(y1)<=m-2*sd else "rgba(251,146,60"
            fig.add_hrect(y0=y0,y1=y1,fillcolor=f"{c},{alpha})",line_width=0)

        # Líneas de referencia
        for y_val,color,width,dash,name in [
            (m,      "#4ade80",2.2,"solid","Media"),
            (m+sd,   "#94a3b8",1.0,"dash", "+1 SD"),
            (m-sd,   "#94a3b8",1.0,"dash", "−1 SD"),
            (m+2*sd, "#fb923c",1.4,"dash", "+2 SD"),
            (m-2*sd, "#fb923c",1.4,"dash", "−2 SD"),
            (m+3*sd, "#f87171",1.8,"dot",  "+3 SD"),
            (m-3*sd, "#f87171",1.8,"dot",  "−3 SD"),
        ]:
            fig.add_hline(y=y_val, line_color=color, line_width=width,
                          line_dash=dash, annotation_text=name,
                          annotation_position="right",
                          annotation_font=dict(color=color,size=11))

        # Línea de tendencia
        fig.add_trace(go.Scatter(x=df_series["Fecha"], y=df_series["Valor"],
                                 mode="lines", line=dict(color="#334155",width=1.5),
                                 showlegend=False, hoverinfo="skip"))
        # Puntos por estado
        for estado, color in [("Verde","#4ade80"),("Ámbar","#fb923c"),("Rojo","#f87171")]:
            sub = df_series[df_series["Estado"]==estado]
            if sub.empty: continue
            fig.add_trace(go.Scatter(
                x=sub["Fecha"], y=sub["Valor"],
                mode="markers", name=estado,
                marker=dict(size=11,color=color,line=dict(color="#080c14",width=1.5)),
                hovertemplate=(f"<b>%{{x|%d %b %Y}}</b><br>Valor: <b>%{{y}}</b><br>"
                               f"Estado: {estado}<extra></extra>"),
            ))

        fig.update_layout(
    plot_bgcolor="white",    # Fondo del área del gráfico
    paper_bgcolor="white",   # Fondo del marco del gráfico
    font_color="#262730",    # Color de las letras y números
    xaxis=dict(gridcolor="#e5e5e5"), # Color de las líneas de rejilla
    yaxis=dict(gridcolor="#e5e5e5")
)
        st.plotly_chart(fig, use_container_width=True)

        # Últimas 7 mediciones
        st.markdown('<div class="sec-title">Últimas 7 mediciones</div>', unsafe_allow_html=True)
        tail = df_series.tail(7)[["Fecha","Valor","Z_Score","Regla_Violada","Score_Riesgo","Estado","Lote"]].copy()
        tail["Fecha"]  = tail["Fecha"].dt.strftime("%d/%m/%Y")
        tail["Estado"] = tail["Estado"].apply(estado_badge)
        st.write(tail.rename(columns={"Z_Score":"Z-Score","Regla_Violada":"Regla",
                                       "Score_Riesgo":"Score"})
                     .to_html(escape=False,index=False), unsafe_allow_html=True)


# ── TAB 2: ASISTENTE IA ───────────────────────────────────────
with tab_chat:
    st.markdown("### 🤖 Asistente AIQC")
    st.caption("Consulta en lenguaje natural. El asistente usa los datos actuales del laboratorio.")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role":"assistant","content":(
            "¡Hola! Soy el **Asistente AIQC v3.0**. Analizo los controles de calidad "
            "usando estadística avanzada (Z-Score, Westgard, EWMA).\n\n"
            "Pregúntame por ejemplo:\n"
            "- *¿Cómo está el ALT?*\n- *¿Hay alertas activas?*\n"
            "- *¿Qué significa la regla 2_2s?*\n- *Dame un resumen del laboratorio*"
        )}]

    def _stats(an: str) -> dict:
        """Calcula estadísticas live para un analito."""
        sub = evaluar_westgard(
            df_all[(df_all["Analito"]==an) &
                   (df_all["Fecha"]>=pd.Timestamp(f_min)) &
                   (df_all["Fecha"]<=pd.Timestamp(f_max))].copy()
        )
        if sub.empty:
            return {}
        u = sub.iloc[-1]
        return {
            "valor":  u["Valor"],
            "media":  u["Media_Objetivo"],
            "sd":     u["SD_Objetivo"],
            "z":      round(u["Z_Score"], 3),
            "score":  int(u["Score_Riesgo"]),
            "estado": u["Estado"],
            "regla":  u["Regla_Violada"],
            "n_rojo": int((sub["Estado"]=="Rojo").sum()),
            "n_amb":  int((sub["Estado"]=="Ámbar").sum()),
        }

    def ia_responde(preg: str) -> str:
        p = preg.lower()
        all_stats = {an: _stats(an) for an in analitos_ls}

        # — Analito mencionado explícitamente —
        mencionado = None
        for an in analitos_ls:
            tokens = [t for t in an.lower().replace("("," ").replace(")","").split() if len(t)>2]
            if any(t in p for t in tokens):
                mencionado = an; break

        if mencionado:
            d = all_stats.get(mencionado, {})
            if not d:
                return f"No hay datos de **{mencionado}** en el período seleccionado."
            z_formula = (f"Z = (x − μ) / σ = ({d['valor']} − {d['media']}) / "
                         f"{d['sd']} = **{d['z']:+.3f}**")
            if d["n_rojo"] > 0 or d["n_amb"] > 0:
                return (
                    f"📊 **Análisis de {mencionado}:**\n\n"
                    f"- Último valor: **{d['valor']}** — Regla activa: `{d['regla']}`\n"
                    f"- Cálculo Z-Score: {z_formula}\n"
                    f"- Score de riesgo: **{d['score']}/100** · Estado: {d['estado']}\n"
                    f"- Alertas en período: 🔴 {d['n_rojo']} roja(s) · 🟠 {d['n_amb']} ámbar\n\n"
                    f"🛠️ **Recomendaciones:**\n"
                    f"1. Revisar calibración del analizador.\n"
                    f"2. Verificar lote y temperatura del reactivo.\n"
                    f"3. No liberar resultados hasta restablecer el control.\n"
                    f"4. Registrar acción en el Tab 3."
                )
            return (
                f"✅ **{mencionado} en control.**\n\n"
                f"- Último valor: {d['valor']}\n"
                f"- {z_formula}\n"
                f"- Score: {d['score']}/100 · {d['estado']}"
            )

        # — Alertas globales —
        if any(w in p for w in ["alerta","alertas","error","activa","crítico","critico"]):
            tr = sum(d.get("n_rojo",0) for d in all_stats.values())
            ta = sum(d.get("n_amb",0)  for d in all_stats.values())
            if tr + ta == 0:
                return "✅ Sin alertas activas. Todos los analitos están bajo control."
            tbl = "| Analito | 🔴 Rojo | 🟠 Ámbar |\n|---|---|---|\n"
            for an,d in all_stats.items():
                tbl += f"| {an} | {d.get('n_rojo',0)} | {d.get('n_amb',0)} |\n"
            return f"🔴 **Alertas activas:**\n\n{tbl}"

        # — Reglas de Westgard —
        if any(w in p for w in ["westgard","regla","1_3s","2_2s","4_1s","violación","violacion"]):
            return (
                "📏 **Reglas de Westgard implementadas:**\n\n"
                "| Regla | Criterio | Tipo de error |\n|---|---|---|\n"
                "| **1_3s** | 1 punto fuera ±3SD | Aleatorio grave |\n"
                "| **2_2s** | 2 consecutivos fuera ±2SD (mismo lado) | Sistemático |\n"
                "| **4_1s** | 4 consecutivos fuera ±1SD (mismo lado) | Deriva |\n"
                "| **1_2s** | 1 punto fuera ±2SD | Advertencia |\n\n"
                "La **fórmula del Z-Score** usada en todas las reglas es:\n\n"
                "**Z = (x − μ) / σ**\n\n"
                "donde x = valor medido, μ = media objetivo, σ = SD objetivo."
            )

        # — Z-Score o fórmula —
        if any(w in p for w in ["z-score","zscore","formula","fórmula","calcular","z score"]):
            lines = []
            for an, d in all_stats.items():
                if d:
                    lines.append(
                        f"- **{an}**: Z = ({d['valor']} − {d['media']}) / "
                        f"{d['sd']} = **{d['z']:+.3f}σ** → {d['estado']}"
                    )
            return (
                "📐 **Z-Score actual por analito:**\n\n"
                "La fórmula es: **Z = (x − μ) / σ**\n\n" +
                "\n".join(lines)
            )

        # — CV / imprecisión —
        if any(w in p for w in ["cv","variación","variacion","imprecisión","imprecision","precisión"]):
            lines = []
            for an, d in all_stats.items():
                if d:
                    cv = round(d["sd"] / d["media"] * 100, 2)
                    lines.append(f"- **{an}**: CV = {cv}%")
            return (
                "📐 **Coeficientes de Variación (CV%):**\n\n" +
                "\n".join(lines) +
                "\n\nCV aceptable: ≤5% (CLIA). Un CV elevado indica imprecisión analítica."
            )

        # — Acción correctiva —
        if any(w in p for w in ["hacer","acción","accion","correcti","solución","solucion","recomenda"]):
            tr = sum(d.get("n_rojo",0) for d in all_stats.values())
            if tr > 0:
                return (
                    "🛠️ **Protocolo de acción correctiva (alerta roja):**\n\n"
                    "1. 🚫 Bloquear liberación de resultados del analito afectado.\n"
                    "2. 🔁 Repetir el control con vial nuevo del mismo lote.\n"
                    "3. ⚙️ Recalibrar el analizador con material trazable.\n"
                    "4. 🌡️ Verificar temperatura de almacenamiento de reactivos.\n"
                    "5. 📋 Registrar todas las acciones en el Tab 3."
                )
            return ("✅ No se requieren acciones correctivas urgentes. "
                    "Continúe con el plan de QC habitual.")

        # — Resumen global —
        if any(w in p for w in ["resumen","estado","laboratorio","informe","dashboard","global"]):
            tbl = "| Analito | Valor | Z-Score | Score | Estado |\n|---|---|---|---|---|\n"
            for an, d in all_stats.items():
                if d:
                    tbl += (f"| {an} | {d['valor']} | {d['z']:+.2f}σ | "
                            f"{d['score']}/100 | {d['estado']} |\n")
            return f"📋 **Resumen del laboratorio:**\n\n{tbl}"

        # — Ayuda —
        if any(w in p for w in ["ayuda","puedes","capacidad","opciones","que sabes"]):
            return (
                "🤖 **Capacidades del Asistente AIQC:**\n\n"
                "- 🔬 Estado de un analito: *¿Cómo está el ALT?*\n"
                "- 🚨 Alertas activas: *¿Hay alertas?*\n"
                "- 📏 Reglas Westgard: *¿Qué es la regla 2_2s?*\n"
                "- 📐 Z-Score con fórmula: *Calcula el Z del Potasio*\n"
                "- 🛠️ Acciones: *¿Qué hago si hay alerta roja?*\n"
                "- 📋 Resumen global: *Dame un informe del laboratorio*"
            )

        # Default
        return ("No encontré una respuesta específica. Escribe *ayuda* para ver mis capacidades, "
                "o pregunta directamente por un analito.")

    # Renderizar historial
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"]=="assistant" else "👤"):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Escribe tu consulta…"):
        st.session_state["messages"].append({"role":"user","content":prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        resp = ia_responde(prompt)
        st.session_state["messages"].append({"role":"assistant","content":resp})
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(resp)

    if st.button("🗑️ Nueva conversación", key="clr"):
        st.session_state["messages"] = [st.session_state["messages"][0]]
        st.rerun()


# ── TAB 3: REGISTRO DE ACCIONES + PDF ────────────────────────
with tab_log:
    col_ttl, col_pdf = st.columns([3, 1])
    with col_ttl:
        st.markdown("### 📋 Registro de Violaciones y Trazabilidad")
        st.caption("Marca cada alerta cuando se haya tomado la acción correctiva correspondiente.")
    with col_pdf:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📄 Descargar Reporte PDF", use_container_width=True, type="primary"):
            with st.spinner("Generando informe…"):
                try:
                    pdf_bytes = generar_pdf(df_all, analitos_ls, data_src)
                    fname = f"AIQC_Incidencias_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                    st.download_button("⬇️ Guardar PDF", data=pdf_bytes,
                                       file_name=fname, mime="application/pdf",
                                       use_container_width=True)
                    st.success("✅ Listo.")
                except Exception as e:
                    st.error(f"Error: {e}. Verifica que fpdf2 esté instalado: pip install fpdf2")

    # Construir tabla completa de violaciones (todos los analitos, período filtrado)
    frames3 = []
    for an in analitos_ls:
        sub = evaluar_westgard(
            df_all[(df_all["Analito"]==an) &
                   (df_all["Fecha"]>=pd.Timestamp(f_min)) &
                   (df_all["Fecha"]<=pd.Timestamp(f_max))].copy()
        )
        frames3.append(sub)
    df_full3 = pd.concat(frames3)
    df_log   = df_full3[df_full3["Estado"]!="Verde"].copy().reset_index(drop=True)

    if df_log.empty:
        st.success("✅ Sin violaciones en el período seleccionado.")
    else:
        if "acciones_log" not in st.session_state:
            st.session_state["acciones_log"] = {}

        hcols = st.columns([1.6,2.2,1.2,1.3,1.4,1.6,1.6,1.4])
        for c, lbl in zip(hcols, ["📅 Fecha","🔬 Analito","Valor","Z-Score",
                                   "Regla","Score","Estado","✅ Acción"]):
            c.markdown(f"**{lbl}**")
        st.markdown("---")

        for idx, row in df_log.iterrows():
            key  = f"{row['Fecha'].date()}_{row['Analito']}_{idx}"
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

        st.markdown("---")
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
            st.warning(f"⚠️ {pend} violación(es) sin acción registrada.")
