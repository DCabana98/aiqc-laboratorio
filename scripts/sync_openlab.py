#!/usr/bin/env python3
# ==============================================================
#  sync_openlab.py  v2.2
#  Agente de subida que corre EN EL LABORATORIO.
#
#  Lee los TXT que OpenLab (Agilent) exporta a una carpeta local
#  y sube el CSV combinado a GitHub, para que la app AIQC lo lea
#  vía leer_csv_github() (aiqc/data_io.py).
#
#  Flujo:   OpenLab --export TXT--> carpeta local
#                   --este script--> GitHub (CSV)
#                   --la app AIQC lee--> navegador
#
#  Formato OpenLab confirmado (separado por tabuladores):
#    27/04 16:50  [TAB]  50.000  [TAB]  Valido  [TAB]  [TAB]
#
#  ── SECRETOS ──────────────────────────────────────────────────
#  El token NUNCA va en el código. Se lee, por orden de prioridad:
#    1. variable de entorno  GITHUB_TOKEN
#    2. sección [github].token de un secrets.toml (ver --secrets)
#  El resto de config (usuario/repo/rama/archivo) sale de la misma
#  sección [github] de secrets.toml — el MISMO contrato que usa la
#  app (.streamlit/secrets.toml.example). Cualquier valor puede
#  sobreescribirse con variables de entorno GITHUB_USUARIO, etc.
#
#  ── USO ───────────────────────────────────────────────────────
#    pip install -r scripts/requirements-sync.txt
#    export GITHUB_TOKEN=ghp_xxx          # (Windows: set GITHUB_TOKEN=...)
#    python scripts/sync_openlab.py       # sincroniza en bucle
#    python scripts/sync_openlab.py --once   # una sola vez y sale
# ==============================================================

import argparse
import base64
import hashlib
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
import requests

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover - fallback 3.9/3.10
    try:
        import tomli as tomllib  # type: ignore
    except ModuleNotFoundError:
        tomllib = None

# ==============================================================
#  CONFIGURACIÓN (con defaults; todo overridable por entorno)
# ==============================================================

# Raíz del proyecto = carpeta padre de scripts/. Las rutas relativas
# (p. ej. secrets.toml) se anclan aquí, no al cwd.
RAIZ = Path(__file__).resolve().parent.parent

# Carpeta donde OpenLab exporta los TXT. En el PC del lab suele ser
# algo como  C:\QC_Export  — configúralo con la variable de entorno
# AIQC_CARPETA_QC o editando este default.
CARPETA_QC = os.environ.get("AIQC_CARPETA_QC", r"C:\QC_Export")

# Mapa de archivos exportados → (Analito, Nivel, Media, SD).
# Media y SD se dejan a 0.0: la app los sobreescribe con los valores
# reales que configures en su panel ⚙️ Configuración.
ANALITOS = {
    "QCDatos_N.txt": ("Amilasa", "N", 0.0, 0.0),
    "QCDatos_PB.txt": ("Amilasa", "PB", 0.0, 0.0),
    "QCDatos_PA.txt": ("Amilasa", "PA", 0.0, 0.0),
}

# Lote por defecto — cámbialo desde la pestaña ⚙️ Configuración de la app.
LOTE_DEFAULT = os.environ.get("AIQC_LOTE", "LOT-2025")

# Intervalo de sincronización automática en minutos.
INTERVALO_MINUTOS = int(os.environ.get("AIQC_INTERVALO_MIN", "60"))

# Log junto a la carpeta de export.
LOG_PATH = os.environ.get("AIQC_LOG", str(Path(CARPETA_QC) / "sync_log.txt"))


def cargar_config_github(ruta_secrets: Optional[str]) -> dict:
    """Lee la sección [github] de secrets.toml y aplica overrides de
    entorno. El token sale SOLO de entorno o de secrets, nunca del código."""
    cfg = {
        "usuario": "",
        "repo": "",
        "rama": "main",
        "archivo": "data/controles_qc.csv",
        "token": "",
    }

    ruta = Path(ruta_secrets) if ruta_secrets else RAIZ / ".streamlit" / "secrets.toml"
    if not ruta.is_absolute():
        ruta = RAIZ / ruta
    if ruta.exists() and tomllib is not None:
        try:
            with open(ruta, "rb") as f:
                data = tomllib.load(f)
            cfg.update({k: v for k, v in data.get("github", {}).items() if v})
        except Exception as e:  # noqa: BLE001
            log(f"⚠️  No se pudo leer {ruta}: {e}")

    # Overrides de entorno (tienen prioridad).
    for clave, env in [
        ("usuario", "GITHUB_USUARIO"),
        ("repo", "GITHUB_REPO"),
        ("rama", "GITHUB_RAMA"),
        ("archivo", "GITHUB_ARCHIVO"),
        ("token", "GITHUB_TOKEN"),
    ]:
        if os.environ.get(env):
            cfg[clave] = os.environ[env]
    return cfg


# ==============================================================
#  LOGGING
# ==============================================================
def log(msg: str) -> None:
    ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    txt = f"[{ts}] {msg}"
    print(txt)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(txt + "\n")
    except Exception:
        pass


# ==============================================================
#  PARSEO DE FECHA OPENLAB (sin año)
# ==============================================================
def parsear_fecha_openlab(fecha_str: str) -> Optional[datetime]:
    """Parsea fechas OpenLab:
      "27/04 16:50"      → formato confirmado (sin año)
      "27/04/2025 16:50" → con año (por si acaso)
    Si no tiene año usa el actual; si la fecha cae >15 días en el
    futuro, asume el año anterior."""
    año_actual = datetime.now().year
    fecha_str = fecha_str.strip()

    formatos = [
        ("%d/%m %H:%M", False),  # ← formato confirmado
        ("%d/%m/%Y %H:%M", True),
        ("%d/%m/%y %H:%M", True),
        ("%d/%m/%Y", True),
        ("%d/%m/%y", True),
        ("%d/%m", False),
    ]

    for fmt, tiene_año in formatos:
        try:
            fecha = datetime.strptime(fecha_str, fmt)
            if not tiene_año:
                fecha = fecha.replace(year=año_actual)
                if (fecha - datetime.now()).days > 15:
                    fecha = fecha.replace(year=año_actual - 1)
            return fecha
        except ValueError:
            continue
    return None


# ==============================================================
#  LECTURA DE ARCHIVOS
# ==============================================================
def leer_archivo_openlab(
    ruta: Path, analito: str, nivel: str, media: float, sd: float
) -> Optional[pd.DataFrame]:
    if not ruta.exists():
        log(f"⚠️  No encontrado: {ruta.name}")
        return None

    filas = []
    cancelados = 0

    with open(ruta, encoding="latin-1", errors="replace") as f:
        for num_linea, linea in enumerate(f, 1):
            linea = linea.strip()
            if not linea:
                continue

            partes = [p.strip() for p in linea.split("\t")]
            if len(partes) < 2:
                continue

            fecha = parsear_fecha_openlab(partes[0])
            if fecha is None:
                log(f"   ⚠️  Línea {num_linea}: fecha no reconocida '{partes[0]}'")
                continue

            valor_str = partes[1].replace(",", ".").strip()
            try:
                valor = float(valor_str)
            except ValueError:
                continue

            estado = partes[2].strip() if len(partes) > 2 else "Valido"
            if estado.lower() not in {"valido", "válido", "valid", "ok", ""}:
                cancelados += 1
                continue

            filas.append(
                {
                    "Fecha": fecha,
                    "Analito": analito,
                    "Nivel": nivel,
                    "Valor": round(valor, 4),
                    # Media y SD a 0; la app los sobreescribe con
                    # los valores del panel de configuración.
                    "Media_Objetivo": media,
                    "SD_Objetivo": sd,
                    "Lote": LOTE_DEFAULT,
                }
            )

    if not filas:
        log(
            f"   ⚠️  Sin datos válidos en {ruta.name}"
            f"{f' ({cancelados} cancelados)' if cancelados else ''}"
        )
        return None

    df = pd.DataFrame(filas).sort_values("Fecha").reset_index(drop=True)
    log(
        f"   ✅ {ruta.name}: {len(df)} válidos"
        f"{f', {cancelados} cancelados omitidos' if cancelados else ''}"
        f" · {df['Fecha'].min().strftime('%d/%m')} → {df['Fecha'].max().strftime('%d/%m')}"
    )
    return df


def combinar_todos() -> Optional[pd.DataFrame]:
    carpeta = Path(CARPETA_QC)
    if not carpeta.exists():
        log(f"❌ Carpeta no encontrada: {CARPETA_QC}")
        return None

    frames = []
    for archivo, (analito, nivel, media, sd) in ANALITOS.items():
        df = leer_archivo_openlab(carpeta / archivo, analito, nivel, media, sd)
        if df is not None:
            frames.append(df)

    if not frames:
        log("❌ Ningún archivo pudo leerse.")
        log(f"   Exporta los TXT desde OpenLab a: {CARPETA_QC}")
        log(f"   Nombres esperados: {', '.join(ANALITOS)}")
        return None

    df_total = (
        pd.concat(frames, ignore_index=True)
        .sort_values(["Analito", "Nivel", "Fecha"])
        .reset_index(drop=True)
    )
    log(
        f"📊 Total: {len(df_total)} registros · "
        f"{df_total['Analito'].nunique()} analito(s) · "
        f"{len(frames)}/{len(ANALITOS)} archivos leídos"
    )
    return df_total


# ==============================================================
#  SUBIDA A GITHUB
# ==============================================================
def hash_df(df: pd.DataFrame) -> str:
    return hashlib.md5(df.to_csv(index=False).encode()).hexdigest()


def subir_a_github(df: pd.DataFrame, cfg: dict) -> bool:
    if not all([cfg.get("usuario"), cfg.get("repo"), cfg.get("archivo")]):
        log(
            "❌ Falta config GitHub (usuario/repo/archivo). Revisa secrets.toml o variables de entorno."
        )
        return False
    if not cfg.get("token"):
        log("❌ Falta el token. Define GITHUB_TOKEN o [github].token en secrets.toml.")
        return False

    url = f"https://api.github.com/repos/{cfg['usuario']}/{cfg['repo']}/contents/{cfg['archivo']}"
    headers = {
        "Authorization": f"Bearer {cfg['token']}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    csv_str = df.to_csv(index=False, sep=";", encoding="utf-8-sig")
    csv_b64 = base64.b64encode(csv_str.encode("utf-8-sig")).decode()

    sha = None
    r = requests.get(url, headers=headers, params={"ref": cfg["rama"]}, timeout=15)
    if r.status_code == 200:
        sha = r.json().get("sha")
    elif r.status_code == 401:
        log("❌ Token GitHub inválido. Verifica GITHUB_TOKEN.")
        return False

    payload = {
        "message": f"QC sync {datetime.now().strftime('%d/%m/%Y %H:%M')} · {len(df)} registros",
        "content": csv_b64,
        "branch": cfg["rama"],
    }
    if sha:
        payload["sha"] = sha

    r2 = requests.put(url, headers=headers, json=payload, timeout=30)
    if r2.status_code in (200, 201):
        log(f"✅ GitHub {'actualizado' if sha else 'creado'}: {cfg['archivo']} ({len(df)} filas)")
        return True
    log(f"❌ Error GitHub {r2.status_code}: {r2.text[:300]}")
    return False


# ==============================================================
#  CICLO PRINCIPAL
# ==============================================================
def sincronizar(cfg: dict, estado: dict) -> None:
    log("─" * 55)
    log("🔄 Sincronizando...")

    df = combinar_todos()
    if df is None:
        return

    nuevo_hash = hash_df(df)
    if nuevo_hash == estado.get("ultimo_hash"):
        log("⏭️  Sin cambios desde la última sincronización.")
        return

    if subir_a_github(df, cfg):
        estado["ultimo_hash"] = nuevo_hash


def main() -> int:
    parser = argparse.ArgumentParser(description="Sincroniza QC de OpenLab → GitHub.")
    parser.add_argument("--once", action="store_true", help="Sincroniza una vez y termina.")
    parser.add_argument(
        "--secrets", help="Ruta a secrets.toml (por defecto .streamlit/secrets.toml)."
    )
    args = parser.parse_args()

    cfg = cargar_config_github(args.secrets)

    log("=" * 55)
    log("🚀 AIQC Sync OpenLab v2.2")
    log(f"   Carpeta  : {CARPETA_QC}")
    log(f"   Analitos : {len(ANALITOS)}")
    log(f"   Destino  : {cfg.get('usuario')}/{cfg.get('repo')}/{cfg.get('archivo')}")
    log(f"   Token    : {'definido' if cfg.get('token') else 'NO definido'}")
    log(f"   Intervalo: cada {INTERVALO_MINUTOS} min")
    log("=" * 55)

    estado: dict = {}
    sincronizar(cfg, estado)

    if args.once:
        return 0

    try:
        while True:
            time.sleep(INTERVALO_MINUTOS * 60)
            sincronizar(cfg, estado)
    except KeyboardInterrupt:
        log("👋 Detenido por el usuario.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
