# ==============================================================
#  sync_openlab.py  v2.1
#  Lee los TXT exportados por OpenLab y los sube a GitHub
#  para que AIQC los lea en tiempo real.
#
#  Formato OpenLab confirmado:
#    27/04 16:50  [TAB]  50.000  [TAB]  Valido  [TAB]  [TAB]
#
#  Instalar dependencias:
#    pip install requests schedule pandas
#
#  Ejecutar:
#    python sync_openlab.py
# ==============================================================

import os
import base64
import hashlib
import schedule
import time
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path

# ==============================================================
#  CONFIGURACIÓN
# ==============================================================

# Carpeta donde guardas los TXT exportados desde OpenLab
CARPETA_QC = r"C:\QC_Export"

# ──────────────────────────────────────────────────────────────
#  ANALITOS
#  Formato: "archivo.txt" : (Analito, Nivel, Media, SD)
#
#  IMPORTANTE: Los valores de Media y SD son los que introduces
#  tú en la app (panel Configuración). Aquí pon 0.0 como
#  placeholder — la app los sobreescribe con los valores reales
#  que configures en el panel.
#
#  Los tres archivos deben llamarse EXACTAMENTE igual a como
#  los guardas al exportar desde OpenLab. Si todos se llaman
#  QCDatos.txt, expórtalos uno a uno y renómbralos:
#    → QCDatos_N.txt   (nivel Normal)
#    → QCDatos_PB.txt  (Patológico Bajo)
#    → QCDatos_PA.txt  (Patológico Alto)
# ──────────────────────────────────────────────────────────────
ANALITOS = {
    "QCDatos_N.txt"  : ("Amilasa", "N",  0.0, 0.0),
    "QCDatos_PB.txt" : ("Amilasa", "PB", 0.0, 0.0),
    "QCDatos_PA.txt" : ("Amilasa", "PA", 0.0, 0.0),
}

# Lote por defecto — cámbialo desde la pestaña ⚙️ Configuración de la app
LOTE_DEFAULT = "LOT-2025"

# GitHub
GITHUB_USUARIO = "aiqc"
GITHUB_REPO    = "aiqc"
GITHUB_RAMA    = "main"
GITHUB_ARCHIVO = "data/controles_qc.csv"
GITHUB_TOKEN   = "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"    # ← pon aquí tu token

# Intervalo de sincronización automática en minutos
INTERVALO_MINUTOS = 60

# Log
LOG_PATH = r"C:\QC_Export\sync_log.txt"


# ==============================================================
#  LOGGING
# ==============================================================
def log(msg: str):
    ts  = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
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
def parsear_fecha_openlab(fecha_str: str) -> datetime | None:
    """
    Parsea fechas OpenLab:
      "27/04 16:50"      → formato confirmado (sin año)
      "27/04/2025 16:50" → con año (por si acaso)
    Si no tiene año usa el actual. Si la fecha está >15 días
    en el futuro, asume año anterior.
    """
    año_actual = datetime.now().year
    fecha_str  = fecha_str.strip()

    formatos = [
        ("%d/%m %H:%M",   False),  # ← formato confirmado
        ("%d/%m/%Y %H:%M", True),
        ("%d/%m/%y %H:%M", True),
        ("%d/%m/%Y",       True),
        ("%d/%m/%y",       True),
        ("%d/%m",          False),
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
def leer_archivo_openlab(ruta: Path, analito: str, nivel: str,
                          media: float, sd: float) -> pd.DataFrame | None:
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

            filas.append({
                "Fecha":          fecha,
                "Analito":        analito,
                "Nivel":          nivel,
                "Valor":          round(valor, 4),
                # Media y SD se ponen a 0 aquí; la app los
                # sobreescribe con los valores del panel de configuración
                "Media_Objetivo": media,
                "SD_Objetivo":    sd,
                "Lote":           LOTE_DEFAULT,
            })

    if not filas:
        log(f"   ⚠️  Sin datos válidos en {ruta.name}"
            f"{f' ({cancelados} cancelados)' if cancelados else ''}")
        return None

    df = pd.DataFrame(filas).sort_values("Fecha").reset_index(drop=True)
    log(f"   ✅ {ruta.name}: {len(df)} válidos"
        f"{f', {cancelados} cancelados omitidos' if cancelados else ''}"
        f" · {df['Fecha'].min().strftime('%d/%m')} → {df['Fecha'].max().strftime('%d/%m')}")
    return df


def combinar_todos() -> pd.DataFrame | None:
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
        log("   Nombres esperados: QCDatos_N.txt, QCDatos_PB.txt, QCDatos_PA.txt")
        return None

    df_total = (pd.concat(frames, ignore_index=True)
                  .sort_values(["Analito", "Nivel", "Fecha"])
                  .reset_index(drop=True))
    log(f"📊 Total: {len(df_total)} registros · "
        f"{df_total['Analito'].nunique()} analito(s) · "
        f"{len(frames)}/{len(ANALITOS)} archivos leídos")
    return df_total


# ==============================================================
#  SUBIDA A GITHUB
# ==============================================================
_ultimo_hash = ""

def hash_df(df: pd.DataFrame) -> str:
    return hashlib.md5(df.to_csv(index=False).encode()).hexdigest()


def subir_a_github(df: pd.DataFrame) -> bool:
    url     = (f"https://api.github.com/repos/{GITHUB_USUARIO}/"
               f"{GITHUB_REPO}/contents/{GITHUB_ARCHIVO}")
    headers = {
        "Authorization":        f"Bearer {GITHUB_TOKEN}",
        "Accept":               "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    csv_str = df.to_csv(index=False, sep=";", encoding="utf-8-sig")
    csv_b64 = base64.b64encode(csv_str.encode("utf-8-sig")).decode()

    sha = None
    r   = requests.get(url, headers=headers, timeout=15)
    if r.status_code == 200:
        sha = r.json().get("sha")
    elif r.status_code == 401:
        log("❌ Token GitHub inválido. Verifica GITHUB_TOKEN.")
        return False

    payload = {
        "message": f"QC sync {datetime.now().strftime('%d/%m/%Y %H:%M')} · {len(df)} registros",
        "content": csv_b64,
        "branch":  GITHUB_RAMA,
    }
    if sha:
        payload["sha"] = sha

    r2 = requests.put(url, headers=headers, json=payload, timeout=30)
    if r2.status_code in [200, 201]:
        log(f"✅ GitHub {'actualizado' if sha else 'creado'}: {GITHUB_ARCHIVO} ({len(df)} filas)")
        return True
    else:
        log(f"❌ Error GitHub {r2.status_code}: {r2.text[:300]}")
        return False


# ==============================================================
#  CICLO PRINCIPAL
# ==============================================================
def sincronizar():
    global _ultimo_hash
    log("─" * 55)
    log("🔄 Sincronizando...")

    df = combinar_todos()
    if df is None:
        return

    nuevo_hash = hash_df(df)
    if nuevo_hash == _ultimo_hash:
        log("⏭️  Sin cambios desde la última sincronización.")
        return

    if subir_a_github(df):
        _ultimo_hash = nuevo_hash


if __name__ == "__main__":
    log("=" * 55)
    log("🚀 AIQC Sync OpenLab v2.1")
    log(f"   Carpeta  : {CARPETA_QC}")
    log(f"   Analitos : {len(ANALITOS)}")
    log(f"   Destino  : {GITHUB_USUARIO}/{GITHUB_REPO}/{GITHUB_ARCHIVO}")
    log(f"   Intervalo: cada {INTERVALO_MINUTOS} min")
    log("=" * 55)

    sincronizar()

    schedule.every(INTERVALO_MINUTOS).minutes.do(sincronizar)
    while True:
        schedule.run_pending()
        time.sleep(30)
