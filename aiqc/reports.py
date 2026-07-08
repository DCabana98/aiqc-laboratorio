# ==============================================================
# AIQC – Exportación de informes
#   · generar_csv()  : CSV (UTF-8 BOM, separador ';') para Excel
#   · generar_pdf()  : informe PDF completo (fpdf2)
# ==============================================================
from datetime import datetime

import pandas as pd
from fpdf import FPDF

from .knowledge_base import NIVELES, TEA_CLIA, TEA_DEFAULT, buscar_kb
from .qc_rules import evaluar_westgard, evaluar_r4s, calcular_sigma
from .charts import build_lj_figure, fig_to_png_bytes


# ==============================================================
# CSV EXPORT
# ==============================================================
def generar_csv(df_log, acciones_db, claves_log):
    if df_log.empty:
        return b""
    export = df_log.copy()
    export["Fecha"] = export["Fecha"].dt.strftime("%d/%m/%Y")
    export["Nivel_Label"] = export.get(
        "_nivel_label", export["Nivel"].map(lambda n: NIVELES.get(n, NIVELES["N"])["label"])
    )
    export["Accion_Completada"] = ["Si" if acciones_db.get(k, False) else "No" for k in claves_log]
    columnas = {
        "Fecha": "Fecha",
        "Analito": "Analito",
        "Nivel_Label": "Nivel",
        "Lote": "Lote",
        "Valor": "Valor_Medido",
        "Media_Objetivo": "Media_Objetivo",
        "SD_Objetivo": "SD_Objetivo",
        "Z_Score": "Z_Score",
        "Regla_Violada": "Regla_Westgard",
        "Score_Riesgo": "Score_Riesgo_100",
        "Estado": "Estado",
        "Accion_Completada": "Accion_Completada",
    }
    cols_ok = {k: v for k, v in columnas.items() if k in export.columns}
    export = export[list(cols_ok.keys())].rename(columns=cols_ok)
    if "Z_Score" in export.columns:
        export["Z_Score"] = export["Z_Score"].round(3)
    return export.to_csv(index=False, sep=";").encode("utf-8-sig")


# ==============================================================
# PDF – sustitución de caracteres no latin-1
# ==============================================================
PDF_REP = {
    "—": "-",
    "–": "-",
    "−": "-",
    "±": "+/-",
    "×": "x",
    "÷": "/",
    "σ": "sigma",
    "μ": "u",
    "→": "->",
    "↑": "(+)",
    "↓": "(-)",
    "≥": ">=",
    "≤": "<=",
    "≠": "!=",
    "≈": "~",
    "°": "o",
    "’": "'",
    "“": '"',
    "”": '"',
    "🔴": "[ROJO]",
    "🟡": "[AMBAR]",
    "🟢": "[VERDE]",
    "⚡": "[R-4s]",
    "✅": "[OK]",
    "⚠": "[WARN]",
    "❌": "[ERROR]",
    "🏆": "[*]",
    "📋": "",
    "📄": "",
    "📈": "",
    "🔬": "",
    "•": "-",
    "·": "-",
}


def pdf_txt(s):
    for orig, repl in PDF_REP.items():
        s = s.replace(orig, repl)
    return s.encode("latin-1", errors="replace").decode("latin-1")


def generar_pdf(df_all, analitos, fuente, f_min=None, f_max=None, lab_nombre="LAB. CENTRAL"):
    class PDF(FPDF):
        def footer(self):
            self.set_y(-13)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(100, 116, 139)
            self.cell(
                0, 10, f"Pagina {self.page_no()}/{{nb}} | AIQC v4.13 | Uso interno", align="C"
            )

    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_fill_color(26, 111, 196)
    pdf.rect(0, 0, 210, 42, "F")
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(255, 255, 255)
    pdf.ln(8)
    pdf.cell(0, 10, "AIQC - Informe de Incidencias de Calidad", ln=True, align="C")
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, pdf_txt(lab_nombre), ln=True, align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(220, 235, 255)
    periodo = (
        f" | Periodo: {f_min.strftime('%d/%m/%Y')} - {f_max.strftime('%d/%m/%Y')}"
        if f_min and f_max
        else ""
    )
    pdf.cell(
        0,
        6,
        pdf_txt(
            f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}{periodo} | Fuente: {fuente}"
        ),
        ln=True,
        align="C",
    )
    pdf.ln(12)

    niveles_disponibles = sorted(df_all["Nivel"].unique()) if "Nivel" in df_all.columns else ["N"]

    def sec(txt):
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(26, 111, 196)
        pdf.cell(0, 8, pdf_txt(txt), ln=True)
        pdf.set_draw_color(13, 158, 110)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)

    # 1. Resumen ejecutivo
    sec("1. Resumen Ejecutivo")
    for niv in niveles_disponibles:
        frames = [
            evaluar_westgard(df_all[(df_all["Analito"] == an) & (df_all["Nivel"] == niv)].copy())
            for an in analitos
        ]
        df_ev = pd.concat([f for f in frames if not f.empty], ignore_index=True)
        if df_ev.empty:
            continue
        total = len(df_ev)
        rojos = int((df_ev["Estado"] == "Rojo").sum())
        ambar = int((df_ev["Estado"] == "Ámbar").sum())
        ok = int((df_ev["Estado"] == "Verde").sum())
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(28, 43, 58)
        pdf.cell(0, 7, pdf_txt(f"Nivel: {NIVELES.get(niv, NIVELES['N'])['label']}"), ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(
            0,
            6,
            pdf_txt(
                f"  Total: {total} | Verde: {ok} ({100 * ok // total if total else 0}%) | "
                f"Ambar: {ambar} | Rojo: {rojos}"
            ),
            ln=True,
        )
        pdf.ln(2)

    # 2. Semáforo de estado
    sec("2. Semaforo de Estado")
    sw = [52, 30, 22, 22, 22, 22, 18]
    sh = ["Analito", "Nivel", "Ultimo Valor", "Media", "SD", "Z-Score", "Estado"]
    pdf.set_fill_color(240, 242, 245)
    pdf.set_text_color(71, 85, 105)
    pdf.set_font("Helvetica", "B", 8)
    for w, h in zip(sw, sh):
        pdf.cell(w, 8, h, border=1, fill=True)
    pdf.ln()
    for an in analitos:
        for niv in niveles_disponibles:
            sub = evaluar_westgard(
                df_all[(df_all["Analito"] == an) & (df_all["Nivel"] == niv)].copy()
            )
            if sub.empty:
                continue
            u = sub.iloc[-1]
            niv_label = NIVELES.get(niv, NIVELES["N"])["label"]
            if u["Estado"] == "Rojo":
                pdf.set_fill_color(254, 226, 226)
                pdf.set_text_color(153, 27, 27)
            elif u["Estado"] == "Ámbar":
                pdf.set_fill_color(254, 243, 199)
                pdf.set_text_color(146, 64, 14)
            else:
                pdf.set_fill_color(209, 250, 229)
                pdf.set_text_color(6, 95, 70)
            pdf.set_font("Helvetica", "", 8)
            ico = {"Rojo": "[R]", "Ámbar": "[A]", "Verde": "[V]"}.get(u["Estado"], "")
            for w, v in zip(
                sw,
                [
                    an[:24],
                    niv_label[:14],
                    str(u["Valor"]),
                    str(u["Media_Objetivo"]),
                    str(u["SD_Objetivo"]),
                    pdf_txt(f"{u['Z_Score']:+.2f}"),
                    f"{ico} {u['Estado']}",
                ],
            ):
                pdf.cell(w, 7, pdf_txt(str(v)), border=1, fill=True)
            pdf.ln()
    pdf.ln(6)

    # 3. Sigma Metrics
    sec("3. Sigma Metrics (CLIA)")
    sm_w = [46, 28, 18, 18, 18, 18, 42]
    sm_h = ["Analito", "Nivel", "TEa%", "CV%", "Sesgo%", "Sigma", "Categoria"]
    pdf.set_fill_color(240, 242, 245)
    pdf.set_text_color(71, 85, 105)
    pdf.set_font("Helvetica", "B", 8)
    for w, h in zip(sm_w, sm_h):
        pdf.cell(w, 8, h, border=1, fill=True)
    pdf.ln()
    for an in analitos:
        for niv in niveles_disponibles:
            sub = df_all[(df_all["Analito"] == an) & (df_all["Nivel"] == niv)].copy()
            if sub.empty:
                continue
            tea = TEA_CLIA.get(an, (TEA_DEFAULT, "", ""))[0]
            sig = calcular_sigma(sub, tea)
            if not sig:
                continue
            s = sig["sigma"]
            if s >= 6:
                pdf.set_fill_color(209, 250, 229)
                pdf.set_text_color(6, 95, 70)
            elif s >= 4:
                pdf.set_fill_color(219, 234, 254)
                pdf.set_text_color(26, 111, 196)
            elif s >= 3:
                pdf.set_fill_color(254, 243, 199)
                pdf.set_text_color(146, 64, 14)
            else:
                pdf.set_fill_color(254, 226, 226)
                pdf.set_text_color(153, 27, 27)
            pdf.set_font("Helvetica", "", 8)
            niv_label = NIVELES.get(niv, NIVELES["N"])["label"]
            for w, v in zip(
                sm_w,
                [
                    an[:24],
                    niv_label[:14],
                    f"{sig['tea_pct']}%",
                    f"{sig['cv_pct']}%",
                    f"{sig['sesgo_pct']}%",
                    str(sig["sigma"]),
                    pdf_txt(sig["categoria"]),
                ],
            ):
                pdf.cell(w, 7, pdf_txt(str(v)), border=1, fill=True)
            pdf.ln()
    pdf.ln(6)

    # 4. Gráficos Levey-Jennings
    sec("4. Graficos Levey-Jennings")
    for an in analitos:
        for niv in niveles_disponibles:
            sub_ev = evaluar_westgard(
                df_all[(df_all["Analito"] == an) & (df_all["Nivel"] == niv)].copy()
            )
            if sub_ev.empty:
                continue
            fig = build_lj_figure(sub_ev, an, niv)
            png = fig_to_png_bytes(fig)
            niv_label = NIVELES.get(niv, NIVELES["N"])["label"]
            if png:
                tmp = f"/tmp/lj_{an.replace(' ', '_').replace('(', '').replace(')', '_')}_{niv}.png"
                open(tmp, "wb").write(png)
                pdf.set_font("Helvetica", "B", 10)
                pdf.set_text_color(28, 43, 58)
                pdf.cell(0, 7, pdf_txt(f"{an} - {niv_label}"), ln=True)
                pdf.image(tmp, x=10, w=190)
                pdf.ln(4)
            else:
                pdf.set_font("Helvetica", "I", 9)
                pdf.set_text_color(100, 116, 139)
                pdf.cell(0, 7, pdf_txt("[Grafico no disponible - instala kaleido]"), ln=True)

    # 5. R-4s
    sec("5. R-4s")
    hay_r4s = False
    for an in analitos:
        r4s = evaluar_r4s(
            df_all, an, f_min or df_all["Fecha"].min(), f_max or df_all["Fecha"].max()
        )
        if r4s:
            hay_r4s = True
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(153, 27, 27)
            pdf.cell(
                0,
                7,
                pdf_txt(
                    f"[R-4s] {an}: {r4s['label_a']} Z={r4s['z_a']:+.2f} vs {r4s['label_b']} "
                    f"Z={r4s['z_b']:+.2f} | Diff={r4s['diferencia']:.2f}sigma"
                ),
                ln=True,
            )
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(28, 43, 58)
            pdf.multi_cell(
                0, 5, pdf_txt("Accion: Repetir ambos niveles con viales nuevos. NO recalibrar.")
            )
            pdf.ln(2)
    if not hay_r4s:
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(6, 95, 70)
        pdf.cell(0, 7, pdf_txt("Sin alarmas R-4s."), ln=True)
    pdf.ln(4)

    # 6. Guía Bio-Rad
    sec("6. Guia Bio-Rad")
    alarmas = set()
    for an in analitos:
        for niv in niveles_disponibles:
            sub = evaluar_westgard(
                df_all[(df_all["Analito"] == an) & (df_all["Nivel"] == niv)].copy()
            )
            if sub.empty:
                continue
            u = sub.iloc[-1]
            if u["Estado"] != "Verde" and an not in alarmas:
                alarmas.add(an)
                kb = buscar_kb(an, u["Estado"])
                if not kb:
                    continue
                niv_label = NIVELES.get(niv, NIVELES["N"])["label"]
                pdf.set_font("Helvetica", "B", 10)
                if u["Estado"] == "Rojo":
                    pdf.set_text_color(153, 27, 27)
                else:
                    pdf.set_text_color(146, 64, 14)
                pdf.cell(
                    0,
                    7,
                    pdf_txt(
                        f"{'ROJO' if u['Estado'] == 'Rojo' else 'AMBAR'} - {an} "
                        f"[{niv_label}] - {u['Regla_Violada']}"
                    ),
                    ln=True,
                )
                pdf.set_font("Helvetica", "", 8)
                pdf.set_text_color(28, 43, 58)
                pdf.cell(0, 5, pdf_txt(f"Producto: {kb['producto']}"), ln=True)
                pdf.set_font("Helvetica", "B", 8)
                pdf.cell(0, 5, "Causas:", ln=True)
                pdf.set_font("Helvetica", "", 8)
                for c in kb["causas_comunes"][:3]:
                    pdf.multi_cell(0, 5, pdf_txt(f"- {c}"))
                pdf.set_font("Helvetica", "B", 8)
                pdf.cell(0, 5, "Acciones:", ln=True)
                pdf.set_font("Helvetica", "", 8)
                for a in (kb["acciones_1_3s"] if u["Estado"] == "Rojo" else kb["acciones_warn"])[
                    :4
                ]:
                    pdf.multi_cell(0, 5, pdf_txt(f"- {a}"))
                pdf.cell(0, 5, pdf_txt(f"Ref: {kb['referencia']}"), ln=True)
                pdf.ln(3)
    if not alarmas:
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(6, 95, 70)
        pdf.cell(0, 7, "Sin alarmas.", ln=True)

    # 7. Firma
    pdf.add_page()
    sec("7. Registro de Validacion y Firma")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(28, 43, 58)
    pdf.cell(0, 6, pdf_txt(f"Informe AIQC v4.13 | Fuente: {fuente}"), ln=True)
    pdf.ln(8)
    fw = [65, 65, 60]
    fh = ["Elaborado por", "Revisado por", "Responsable de Calidad"]
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(240, 242, 245)
    pdf.set_text_color(71, 85, 105)
    for w, h in zip(fw, fh):
        pdf.cell(w, 8, h, border=1, fill=True)
    pdf.ln()
    for w in fw:
        pdf.cell(w, 22, "", border=1)
    pdf.ln()
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(100, 116, 139)
    for w in fw:
        pdf.cell(w, 6, "Nombre y firma", border="LRB", align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(28, 43, 58)
    pdf.cell(65, 8, pdf_txt(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}"), border=1)
    if f_min and f_max:
        pdf.cell(
            125,
            8,
            pdf_txt(f"Periodo: {f_min.strftime('%d/%m/%Y')} - {f_max.strftime('%d/%m/%Y')}"),
            border=1,
        )
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 116, 139)
    pdf.multi_cell(0, 5, pdf_txt("Confidencial · Uso interno · ISO 15189:2022"))
    return bytes(pdf.output())
