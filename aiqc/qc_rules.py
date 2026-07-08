# ==============================================================
# AIQC – Reglas y estadística de control de calidad
#   · evaluar_westgard()  : 1_3s, 2_2s, 4_1s, 10_x, 1_2s(warn)
#   · evaluar_r4s()       : R-4s multi-nivel (error aleatorio)
#   · calcular_ewma()     : media móvil ponderada (deriva)
#   · calcular_cusum()    : suma acumulada (tendencia)
#   · calcular_sigma()    : Sigma Metrics (CLIA)
# ==============================================================
import numpy as np
import pandas as pd

from .knowledge_base import NIVELES

REGLAS_DESC = (
    "1_3s: +/-3SD -> Rojo | 2_2s: 2 consec +/-2SD -> Rojo | "
    "4_1s: 4 consec +/-1SD -> Ambar | 10_x: 10 consec mismo lado -> Ambar | "
    "R-4s: 2 niveles opuestos >2SD -> Rojo (multi-nivel)"
)


# ==============================================================
# WESTGARD
# ==============================================================
def evaluar_westgard(serie):
    df = serie.copy().sort_values("Fecha").reset_index(drop=True)
    df["Z_Score"] = (df["Valor"] - df["Media_Objetivo"]) / df["SD_Objetivo"]
    df["Regla_Violada"] = "—"
    df["Score_Riesgo"] = 0
    df["Estado"] = "Verde"
    for i in range(len(df)):
        z = df.at[i, "Z_Score"]
        if abs(z) >= 3.0:
            df.at[i, "Regla_Violada"] = "1_3s"
            df.at[i, "Score_Riesgo"] = 90
            df.at[i, "Estado"] = "Rojo"
            continue
        if i >= 1:
            zp = df.at[i - 1, "Z_Score"]
            if abs(z) >= 2.0 and abs(zp) >= 2.0 and np.sign(z) == np.sign(zp):
                df.at[i, "Regla_Violada"] = "2_2s"
                df.at[i, "Score_Riesgo"] = 75
                df.at[i, "Estado"] = "Rojo"
                continue
        if i >= 3:
            w4 = df.loc[i - 3 : i, "Z_Score"].values
            if all(abs(x) >= 1.0 for x in w4) and len(set(np.sign(w4))) == 1:
                df.at[i, "Regla_Violada"] = "4_1s"
                df.at[i, "Score_Riesgo"] = 60
                df.at[i, "Estado"] = "Ámbar"
                continue
        if i >= 9:
            w10 = df.loc[i - 9 : i, "Z_Score"].values
            signos = set(np.sign(w10))
            if len(signos) == 1 and 0.0 not in signos:
                df.at[i, "Regla_Violada"] = "10_x"
                df.at[i, "Score_Riesgo"] = 55
                df.at[i, "Estado"] = "Ámbar"
                continue
        if abs(z) >= 2.0:
            df.at[i, "Regla_Violada"] = "1_2s (warn)"
            df.at[i, "Score_Riesgo"] = 45
            df.at[i, "Estado"] = "Ámbar"
            continue
        df.at[i, "Score_Riesgo"] = max(0, int(abs(z) * 18))
    return df


# ==============================================================
# R-4s (multi-nivel)
# ==============================================================
def evaluar_r4s(df_all, analito, f_min, f_max):
    niveles = sorted(df_all[df_all["Analito"] == analito]["Nivel"].unique())
    if len(niveles) < 2:
        return None
    zscores = {}
    for niv in niveles:
        sub = df_all[
            (df_all["Analito"] == analito)
            & (df_all["Nivel"] == niv)
            & (df_all["Fecha"] >= pd.Timestamp(f_min))
            & (df_all["Fecha"] <= pd.Timestamp(f_max))
        ].copy()
        if sub.empty:
            continue
        u = sub.sort_values("Fecha").iloc[-1]
        z = (u["Valor"] - u["Media_Objetivo"]) / u["SD_Objetivo"]
        zscores[niv] = {
            "z": round(z, 3),
            "valor": u["Valor"],
            "media": u["Media_Objetivo"],
            "sd": u["SD_Objetivo"],
        }
    if len(zscores) < 2:
        return None
    pares = list(zscores.items())
    for i in range(len(pares)):
        for j in range(i + 1, len(pares)):
            niv_a, info_a = pares[i]
            niv_b, info_b = pares[j]
            diff = abs(info_a["z"] - info_b["z"])
            if diff >= 4.0 and np.sign(info_a["z"]) != np.sign(info_b["z"]):
                return {
                    "dispara": True,
                    "analito": analito,
                    "niv_a": niv_a,
                    "niv_b": niv_b,
                    "label_a": NIVELES.get(niv_a, NIVELES["N"])["label"],
                    "label_b": NIVELES.get(niv_b, NIVELES["N"])["label"],
                    "z_a": info_a["z"],
                    "z_b": info_b["z"],
                    "diferencia": round(diff, 3),
                    "valor_a": info_a["valor"],
                    "valor_b": info_b["valor"],
                    "media_a": info_a["media"],
                    "media_b": info_b["media"],
                    "sd_a": info_a["sd"],
                    "sd_b": info_b["sd"],
                }
    return None


# ==============================================================
# EWMA
# ==============================================================
def calcular_ewma(z_scores, lam=0.20):
    n = len(z_scores)
    if n == 0:
        return {
            "ewma": [],
            "estados": [],
            "ultimo_ewma": 0,
            "sigma_ewma": 0,
            "inicio_deriva": None,
            "lim_warn": 0,
            "lim_act": 0,
        }
    sigma_ewma = (lam / (2 - lam)) ** 0.5
    lim_warn = 2.0 * sigma_ewma
    lim_act = 3.0 * sigma_ewma
    ewma = [0.0] * n
    estados = ["Verde"] * n
    ewma[0] = lam * z_scores[0]
    for i in range(1, n):
        ewma[i] = lam * z_scores[i] + (1 - lam) * ewma[i - 1]
    inicio_deriva = None
    for i, e in enumerate(ewma):
        if abs(e) >= lim_act:
            estados[i] = "Rojo"
            if inicio_deriva is None:
                inicio_deriva = i
        elif abs(e) >= lim_warn:
            estados[i] = "Ámbar"
            if inicio_deriva is None:
                inicio_deriva = i
    return {
        "ewma": ewma,
        "estados": estados,
        "ultimo_ewma": round(ewma[-1], 4),
        "sigma_ewma": round(sigma_ewma, 4),
        "lim_warn": round(lim_warn, 4),
        "lim_act": round(lim_act, 4),
        "inicio_deriva": inicio_deriva,
    }


# ==============================================================
# CUSUM
# ==============================================================
def calcular_cusum(z_scores, k=0.5, h=5.0):
    n = len(z_scores)
    if n == 0:
        return {
            "cusum_pos": [],
            "cusum_neg": [],
            "alarma_any": [],
            "primera_alarma": None,
            "max_cp": 0,
            "max_cm": 0,
            "tipo_deriva": None,
        }
    cp = [0.0] * n
    cm = [0.0] * n
    alarma = [False] * n
    cp[0] = max(0, z_scores[0] - k)
    cm[0] = max(0, -z_scores[0] - k)
    if cp[0] > h or cm[0] > h:
        alarma[0] = True
    for i in range(1, n):
        cp[i] = max(0, cp[i - 1] + z_scores[i] - k)
        cm[i] = max(0, cm[i - 1] - z_scores[i] - k)
        if cp[i] > h or cm[i] > h:
            alarma[i] = True
    primera = next((i for i, a in enumerate(alarma) if a), None)
    tipo = None
    if primera is not None:
        tipo = "ascendente" if cp[primera] > h else "descendente"
    return {
        "cusum_pos": cp,
        "cusum_neg": cm,
        "alarma_any": alarma,
        "primera_alarma": primera,
        "max_cp": round(max(cp), 3),
        "max_cm": round(max(cm), 3),
        "tipo_deriva": tipo,
    }


# ==============================================================
# SIGMA METRICS
# ==============================================================
def calcular_sigma(df_analito, tea_pct):
    if df_analito.empty:
        return {}
    media = df_analito["Media_Objetivo"].iloc[0]
    sd = df_analito["SD_Objetivo"].iloc[0]
    vals = df_analito["Valor"]
    cv_pct = (sd / media) * 100 if media != 0 else 0
    sesgo_pct = abs((vals.mean() - media) / media) * 100 if media != 0 else 0
    sigma = (tea_pct - sesgo_pct) / cv_pct if cv_pct > 0 else 0
    if sigma >= 6:
        cat = "Clase Mundial"
        color = "#0D9E6E"
    elif sigma >= 4:
        cat = "Buena calidad"
        color = "#1A6FC4"
    elif sigma >= 3:
        cat = "Aceptable"
        color = "#F59E0B"
    else:
        cat = "Revisar metodo"
        color = "#E53E3E"
    return {
        "sigma": round(sigma, 2),
        "cv_pct": round(cv_pct, 2),
        "sesgo_pct": round(sesgo_pct, 2),
        "tea_pct": tea_pct,
        "categoria": cat,
        "color": color,
        "media": round(media, 3),
        "sd": round(sd, 4),
        "n": len(vals),
    }
