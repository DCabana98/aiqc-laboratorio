# ==============================================================
# AIQC – Acceso seguro a la configuración (st.secrets)
#
# st.secrets lanza StreamlitSecretNotFoundError si no existe ningún
# secrets.toml. Esto envuelve el acceso para que la app pueda arrancar
# en modo demo sin ninguna configuración.
# ==============================================================
import streamlit as st


def get_section(nombre, default=None):
    """Devuelve la sección ``[nombre]`` de secrets como dict, o ``default`` ({} por
    defecto) si no hay secrets.toml o la sección no existe."""
    if default is None:
        default = {}
    try:
        return st.secrets.get(nombre, default)
    except Exception:
        return default


def get_value(nombre, default=""):
    """Devuelve una clave de nivel superior de secrets, o ``default`` si no
    hay secrets.toml o la clave no existe."""
    try:
        return st.secrets.get(nombre, default)
    except Exception:
        return default
