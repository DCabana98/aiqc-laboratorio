# ==============================================================
#  AIQC – Artificial Intelligence for Quality Control
#  Versión: 3.0 PROFESIONAL (TEMA CLARO)
#  Deploy:  streamlit run app.py
#  Deps:    pip install streamlit plotly pandas numpy fpdf2 openpyxl
# ==============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from io import BytesIO
from fpdf import FPDF

# 1. CONFIGURACIÓN DE PÁGINA (Debe ser lo primero)
st.set_page_config(
    page_title="AIQC – Quality Control AI",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. BLOQUE MAESTRO DE ESTILO (CSS para Tema Claro y Limpio)
st.markdown("""
    <style>
    /* Ocultar menús de Streamlit para mayor profesionalismo */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Fondo general Blanco Clínico */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #F8F9FA !important;
    }

    /* Texto Global en Gris Grafito (Máxima legibilidad) */
    html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, span {
        color: #212529 !important;
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
    }

    /* Barra Lateral Suave */
    [data-testid="stSidebar"] {
        background-color: #F0F2F6 !important;
        border-right: 1px solid #E0E0E0;
    }

    /* Títulos de sección en Azul Médico */
    h1, h2, .sec-title {
        color: #0056b3 !important;
        font-weight: 700 !important;
    }

    /* Tarjetas de Métricas (KPIs) Blancas y Elegantes */
    div[data-testid="metric-container"], .kpi, .stMetric {
        background-color: #FFFFFF !important;
        border: 1px solid #DEE2E6 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        padding: 20px !important;
        text-align: center;
    }

    /* Pestañas (Tabs) con Estilo Moderno */
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        color: #6c757d !important;
        font-weight: 600 !important;
    }
    button[aria-selected="true"] {
        color: #007BFF !important;
        border-bottom-color: #007BFF !important;
    }

    /* Botones Profesionales */
    .stButton>button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease;
    }

    /* Estilos para las tablas de datos */
    table {
        background-color: white !important;
        color: #212529 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================
#  3. AUTENTICACIÓN
# ==============================================================
VALID_USER, VALID_PASS = "admin", "qc2026"

if "auth" not in st.session_state:
    st.session_state["auth"] = False

def render_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        st.markdown("<h1 style='text-align:center;'>🔬 AIQC</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#6c757d;'>Control de Calidad Inteligente</p>", unsafe_allow_html=True)
        with st.container():
            st.markdown("<div style='background:white; padding:30px; border-radius:15px; border:1px solid #dee2e6;'>", unsafe_allow_html=True)
            user = st.text_input("Usuario", key="u_login")
            pwd = st.text_input("Contraseña", type="password", key="p_login")
            if st.button("Iniciar Sesión", use_container_width=True, type="primary"):
                if user == VALID_USER and pwd == VALID_PASS:
                    st.session_state["auth"] = True
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
            st.markdown("</div>", unsafe_allow_html=True)

if not st.session_state["auth"]:
    render_login()
    st.stop()

# ==============================================================
#  4. LÓGICA DE DATOS Y ESTADÍSTICA
# ==============================================================
@st.cache_data
def build_demo():
    np.random.seed(2026)
    today = datetime.today()
    dates = [today - timedelta(days=29 - i) for i in range(30)]
    rows = []
    for i, d in enumerate(dates):
        # Potasio (Estable)
        rows.append({"Fecha": d, "Analito": "Potasio (K+)", "Valor": round(np.random.normal(4.5, 0.12), 2), "Media_Objetivo": 4.5, "SD_Objetivo": 0.15})
        # ALT (Deriva)
        drift = 1.8 * (i - 24) if i >= 25 else 0
        rows.append({"Fecha": d, "Analito": "ALT (Transaminasa)", "Valor": round(np.random.normal(35.0 + drift, 2.0), 2), "Media_Objetivo": 35.0, "SD_Objetivo": 2.5})
    return pd.DataFrame(rows)

def evaluar_westgard(df):
    df = df.copy().sort_values("Fecha")
    df["Z"] = (df["Valor"] - df["Media_Objetivo"]) / df["SD_Objetivo"]
    df["Estado"] = "Verde"
    df["Regla"] = "OK"
    for i in range(len(df)):
        z = df.at[i, "Z"]
        if abs(z) >= 3:
            df.at[i, "Estado"], df.at[i, "Regla"] = "Rojo", "1_3s"
        elif i > 0 and abs(z) >= 2 and abs(df.at[i-1, "Z"]) >= 2 and np.sign(z) == np.sign(df.at[i-1, "Z"]):
            df.at[i, "Estado"], df.at[i, "Regla"] = "Rojo", "2_2s"
        elif abs(z) >= 2:
            df.at[i, "Estado"], df.at[i, "Regla"] = "Ámbar", "1_2s"
    return df

# ==============================================================
#  5. SIDEBAR Y FILTROS
# ==============================================================
df_all = build_demo()

with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    analito = st.selectbox("Seleccionar Analito", options=df_all["Analito"].unique())
    st.divider()
    st.markdown("📂 **Cargar Datos Reales**")
    uploaded = st.file_uploader("Subir CSV o Excel", type=["csv", "xlsx"])
    st.divider()
    if st.button("Cerrar Sesión"):
        st.session_state["auth"] = False
        st.rerun()

# ==============================================================
#  6. DASHBOARD PRINCIPAL
# ==============================================================
df_sel = evaluar_westgard(df_all[df_all["Analito"] == analito].reset_index())
ult = df_sel.iloc[-1]

tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🤖 Asistente IA", "📋 Trazabilidad"])

with tab1:
    st.markdown(f"## {analito}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Último Valor", f"{ult['Valor']}")
    c2.metric("Media Obj.", f"{ult['Media_Objetivo']}")
    c3.metric("Z-Score", f"{ult['Z']:.2f}σ")
    
    estado_color = {"Verde": "green", "Ámbar": "orange", "Rojo": "red"}[ult["Estado"]]
    c4.markdown(f"<div style='text-align:center; padding:10px; border-radius:10px; background:{estado_color}; color:white; font-weight:bold;'>ESTADO: {ult['Estado']}</div>", unsafe_allow_html=True)

    # Gráfico de Levey-Jennings (Forzado a Tema Claro)
    fig = go.Figure()
    m, sd = ult["Media_Objetivo"], ult["SD_Objetivo"]
    
    # Líneas de Westgard
    for l, col, d in [(m, 'green', 'solid'), (m+2*sd, 'orange', 'dash'), (m-2*sd, 'orange', 'dash'), (m+3*sd, 'red', 'dot'), (m-3*sd, 'red', 'dot')]:
        fig.add_hline(y=l, line_color=col, line_dash=d)

    fig.add_trace(go.Scatter(x=df_sel["Fecha"], y=df_sel["Valor"], mode='lines+markers', marker=dict(color='#0056b3', size=8), name="Valor"))
    
    fig.update_layout(
        title="Gráfico de Levey-Jennings",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font_color="#212529",
        xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("### 🤖 Consulta al Asistente")
    prompt = st.chat_input("¿Cómo está el control hoy?")
    if prompt:
        with st.chat_message("user"): st.write(prompt)
        with st.chat_message("assistant"):
            if "estado" in prompt.lower() or analito.lower() in prompt.lower():
                st.write(f"El analito **{analito}** presenta un estado **{ult['Estado']}**. El Z-Score actual es de **{ult['Z']:.2f}**. Recomiendo revisar la tendencia si el score supera 1.5.")
            else:
                st.write("Estoy analizando los datos. Según las reglas de Westgard, la estabilidad del sistema es adecuada, a excepción de las derivas detectadas en ALT.")

with tab3:
    st.markdown("### 📋 Registro de Violaciones")
    violaciones = df_sel[df_sel["Estado"] != "Verde"]
    st.dataframe(violaciones[["Fecha", "Valor", "Z", "Regla", "Estado"]], use_container_width=True)
    
    if st.button("📥 Generar Reporte PDF"):
        st.success("Reporte generado con éxito (Simulado para esta demo).")

# Fin del código
