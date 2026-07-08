# ==============================================================
# AIQC – Base de datos (SQLite)
#   · usuarios, acciones (trazabilidad), auditoría
#   · login con bcrypt, control de permisos por rol
# ==============================================================
import os
import sqlite3
import bcrypt
import streamlit as st

from .config import get_section


# ==============================================================
# RUTA DE LA BASE DE DATOS
# ==============================================================
# Raíz del proyecto (carpeta que contiene el paquete aiqc/).
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_db_path():
    # Ruta explícita en secrets ([db].path) si se define; si no, ~/.aiqc/.
    # Las rutas relativas se anclan a la raíz del proyecto (no al cwd), de modo
    # que la BD queda siempre en el mismo sitio sin importar desde dónde se lance.
    custom = (get_section("db").get("path", "") or "").strip()
    if custom:
        custom = os.path.expanduser(custom)
        db_path = custom if os.path.isabs(custom) else os.path.join(_PROJECT_ROOT, custom)
    else:
        db_path = os.path.join(os.path.expanduser("~"), ".aiqc", "aiqc_acciones.db")
    db_path = os.path.abspath(db_path)
    # Garantiza que el directorio contenedor existe (multiplataforma).
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return db_path


DB_PATH = get_db_path()


# ==============================================================
# INICIALIZACIÓN
# ==============================================================
def init_db():
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute(
        """CREATE TABLE IF NOT EXISTS acciones (
        clave TEXT PRIMARY KEY, hecha INTEGER DEFAULT 0,
        ts TEXT, usuario TEXT DEFAULT 'sistema')"""
    )
    con.execute(
        """CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL,
        rol TEXT NOT NULL DEFAULT 'tecnico', nombre TEXT DEFAULT '',
        activo INTEGER DEFAULT 1, creado_en TEXT DEFAULT (datetime('now')),
        ultimo_acceso TEXT)"""
    )
    con.execute(
        """CREATE TABLE IF NOT EXISTS auditoria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT DEFAULT (datetime('now')),
        usuario TEXT NOT NULL, accion TEXT NOT NULL, detalle TEXT DEFAULT '')"""
    )
    con.commit()
    _seed_admin(con)
    return con


def _seed_admin(con):
    if con.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0:
        pwd_default = get_section("auth").get("admin_password", "admin2024")
        pwd_hash = bcrypt.hashpw(pwd_default.encode(), bcrypt.gensalt()).decode()
        con.execute(
            "INSERT INTO usuarios (username,password_hash,rol,nombre) VALUES (?,?,'admin','Administrador')",
            ("admin", pwd_hash),
        )
        con.commit()


# ==============================================================
# PASSWORD / LOGIN
# ==============================================================
def verificar_password(password, password_hash):
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except Exception:
        return False


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def login_usuario(con, username, password):
    row = con.execute(
        "SELECT id,username,password_hash,rol,nombre,activo FROM usuarios WHERE username=?",
        (username,),
    ).fetchone()
    if row is None:
        registrar_auditoria(con, username, "LOGIN_FALLIDO", "Usuario no existe")
        return None
    id_, uname, pwd_hash, rol, nombre, activo = row
    if not activo:
        registrar_auditoria(con, username, "LOGIN_DENEGADO", "Usuario desactivado")
        return None
    if not verificar_password(password, pwd_hash):
        registrar_auditoria(con, username, "LOGIN_FALLIDO", "Contraseña incorrecta")
        return None
    con.execute("UPDATE usuarios SET ultimo_acceso=datetime('now') WHERE id=?", (id_,))
    con.commit()
    registrar_auditoria(con, username, "LOGIN_OK", f"Rol: {rol}")
    return {"id": id_, "username": uname, "rol": rol, "nombre": nombre}


# ==============================================================
# AUDITORÍA / PERMISOS
# ==============================================================
def registrar_auditoria(con, usuario, accion, detalle=""):
    try:
        con.execute(
            "INSERT INTO auditoria (usuario,accion,detalle) VALUES (?,?,?)",
            (usuario, accion, detalle),
        )
        con.commit()
    except Exception:
        pass


def tiene_permiso(rol_usuario, rol_requerido):
    jerarquia = {"admin": 3, "supervisor": 2, "tecnico": 1}
    return jerarquia.get(rol_usuario, 0) >= jerarquia.get(rol_requerido, 99)


# ==============================================================
# ACCIONES (trazabilidad de incidencias)
# ==============================================================
def load_acciones(con):
    return {r[0]: bool(r[1]) for r in con.execute("SELECT clave,hecha FROM acciones").fetchall()}


def save_accion(con, clave, hecha, usuario="sistema"):
    con.execute(
        "INSERT OR REPLACE INTO acciones VALUES (?,?,datetime('now'),?)",
        (clave, int(hecha), usuario),
    )
    con.commit()
    registrar_auditoria(con, usuario, f"ACCION_{'COMPLETADA' if hecha else 'PENDIENTE'}", clave)


# ==============================================================
# LOGIN UI
# ==============================================================
def render_login(con):
    st.markdown(
        """<div class="login-card">
    <div style="font-size:3rem;text-align:center">🔬</div>
    <div style="text-align:center;font-size:1.8rem;font-weight:800;color:#1A6FC4;margin-bottom:4px">AIQC</div>
    <div style="text-align:center;font-size:.86rem;color:#64748B;margin-bottom:28px">
    Artificial Intelligence for Quality Control · v4.13</div></div>""",
        unsafe_allow_html=True,
    )
    _, mid, _ = st.columns([1, 1.8, 1])
    with mid:
        st.markdown("<br>", unsafe_allow_html=True)
        username = st.text_input("Usuario", placeholder="admin", key="_u")
        pwd = st.text_input("Contraseña", type="password", placeholder="••••••", key="_p")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Acceder al sistema →", use_container_width=True, type="primary"):
            usuario_data = login_usuario(con, username.strip(), pwd)
            if usuario_data:
                st.session_state["auth"] = True
                st.session_state["usuario"] = usuario_data
                st.rerun()
            else:
                st.error("Credenciales incorrectas o usuario desactivado.")
