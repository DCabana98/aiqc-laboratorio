# ==============================================================
# AIQC – Base de conocimiento
#   · BIORAD_KB     : fichas Bio-Rad por analito
#   · GRUPOS_ANALITICOS
#   · NIVELES       : N / PB / PA
#   · COBAS_8000_KB : manual resumido del analizador
#   · TEA_CLIA      : error total admisible (Sigma Metrics)
# ==============================================================

# ==============================================================
# CONSTANTES DE NIVEL
# ==============================================================
NIVELES = {
    "N": {"label": "Normal", "pill": "nivel-N", "icon": "🔵"},
    "PB": {"label": "Patológico Bajo", "pill": "nivel-PB", "icon": "🟡"},
    "PA": {"label": "Patológico Alto", "pill": "nivel-PA", "icon": "🔴"},
}


def nivel_badge(codigo):
    cfg = NIVELES.get(codigo, NIVELES["N"])
    return f'<span class="nivel-pill {cfg["pill"]}">{cfg["icon"]} {cfg["label"]}</span>'


# ==============================================================
# BIO-RAD KB
# ==============================================================
BIORAD_KB = {
    "Glucosa": {
        "producto": "Liquichek Chemistry Control / Lyphochek Chemistry",
        "grupo": "Bioquímica básica",
        "causas_comunes": [
            "Evaporación del vial",
            "Degradación glucolítica in vitro",
            "Interferencia por hemólisis severa",
            "Calibración desactualizada",
        ],
        "acciones_1_3s": [
            "No liberar resultados de pacientes",
            "Repetir con NUEVO vial del mismo lote",
            "Si persiste: vial de LOTE DIFERENTE",
            "Verificar temperatura (2-8 oC)",
            "Recalibrar con estándar trazable IDMS",
        ],
        "acciones_warn": [
            "Monitoreo estrecho",
            "Revisar tendencia en Levey-Jennings",
            "Verificar temperatura del baño",
        ],
        "causas_deriva": [
            "Deterioro del reactivo",
            "Deriva del calibrador",
            "Fluctuación de temperatura",
        ],
        "estabilidad_biorad": "Reconstituido: 5 días a 2-8 oC / 30 días a -20 oC",
        "interferencias": "Hemólisis (+), lipemia severa (- GOD-PAP), ácido ascórbico >30 mg/dL (-)",
        "referencia": "Liquichek Chemistry Control Insert · Bio-Rad cat. 66796 / CLSI EP7-A2",
    },
    "Potasio (K+)": {
        "producto": "Liquichek Chemistry Control / Liquichek Electrolyte Plus",
        "grupo": "Bioquímica básica",
        "causas_comunes": [
            "Evaporación del vial",
            "Contaminación por EDTA",
            "Hemólisis in vitro del control",
            "Temperatura incorrecta del módulo ISE",
        ],
        "acciones_1_3s": [
            "Verificar que el vial no lleva abierto más de 8 horas",
            "Repetir con vial nuevo",
            "Revisar el electrodo ISE",
            "Recalibrar el módulo ISE",
        ],
        "acciones_warn": [
            "Verificar tiempo de apertura del vial",
            "Comprobar limpieza del electrodo ISE",
        ],
        "causas_deriva": [
            "Desgaste de la membrana del electrodo ISE",
            "Acumulación de proteínas en el electrodo",
        ],
        "estabilidad_biorad": "Reconstituido: 8 h a temperatura ambiente / 5 días a 2-8 oC",
        "interferencias": "Hemólisis (++), EDTA (+), heparina litio (mínimo)",
        "referencia": "Liquichek Electrolyte Plus Insert · Bio-Rad · CLSI EP9-A3",
    },
    "Sodio": {
        "producto": "Liquichek Chemistry Control / Liquichek Electrolyte Plus",
        "grupo": "Bioquímica básica",
        "causas_comunes": [
            "Pseudohiponatremia por lipemia severa",
            "Dilución incorrecta del control",
            "Electrodo ISE de sodio deteriorado",
        ],
        "acciones_1_3s": [
            "Repetir control con vial nuevo",
            "Verificar volumen de reconstitución",
            "Revisar y limpiar el electrodo ISE de sodio",
        ],
        "acciones_warn": ["Revisar mezcla por inversión suave", "Verificar temperatura ISE"],
        "causas_deriva": ["Envejecimiento de la membrana ISE", "Cambio de lote sin recalibración"],
        "estabilidad_biorad": "Reconstituido: 8 h a temperatura ambiente / 5 días a 2-8 oC",
        "interferencias": "Lipemia (- métodos fotométricos), hemólisis (mínimo en ISE)",
        "referencia": "Liquichek Electrolyte Plus Insert · Bio-Rad · CLSI EP7-A2",
    },
    "Creatinina": {
        "producto": "Liquichek Chemistry Control",
        "grupo": "Bioquímica básica",
        "causas_comunes": [
            "Interferencia por cromógenos de Jaffé",
            "Diferencia de método: Jaffé vs enzimático",
            "Calibración no trazable a IDMS",
        ],
        "acciones_1_3s": [
            "Confirmar valores del insert para TU método",
            "Cambiar a método enzimático si hay interferencia",
            "Recalibrar con calibrador trazable IDMS (NIST SRM 967)",
        ],
        "acciones_warn": [
            "Verificar método (Jaffé vs enzimático)",
            "Revisar caducidad del reactivo Jaffé",
        ],
        "causas_deriva": ["Degradación del ácido pícrico en método Jaffé", "Deriva del calibrador"],
        "estabilidad_biorad": "Reconstituido: 5 días a 2-8 oC",
        "interferencias": "Bilirrubina >10 mg/dL (+ Jaffé), cefalosporinas (+), acetona (+)",
        "referencia": "Liquichek Chemistry Control Insert · Bio-Rad · CLSI EP6-A",
    },
    "ALT (Transaminasa)": {
        "producto": "Liquichek Chemistry Control / Lyphochek Chemistry",
        "grupo": "Enzimas hepáticas",
        "causas_comunes": [
            "Temperatura de incubación incorrecta",
            "Degradación enzimática por ciclos de congelación",
            "Longitud de onda del fotómetro fuera de tolerancia (340 nm)",
            "Reactivo de piridoxal fosfato (P-5-P) faltante",
        ],
        "acciones_1_3s": [
            "Verificar temperatura del baño (37,0 oC +/- 0,1 oC)",
            "Repetir con vial nuevo",
            "Comprobar que el reactivo contiene P-5-P activado",
            "Verificar longitud de onda del espectrofotómetro",
        ],
        "acciones_warn": [
            "Comprobar temperatura del módulo fotométrico",
            "Verificar mezcla del vial",
        ],
        "causas_deriva": [
            "Deterioro del NADH (sensible a luz UV)",
            "Fluctuación de temperatura",
            "Cambio de lote sin ajuste de valores objetivo",
        ],
        "estabilidad_biorad": "Reconstituido: 5 días a 2-8 oC",
        "interferencias": "Hemólisis severa (+), lipemia >500 mg/dL (variable), bilirrubina >20 mg/dL (+ leve)",
        "referencia": "Liquichek Chemistry Control Insert · Bio-Rad · IFCC EP9 / CLSI EP15-A3",
    },
    "AST": {
        "producto": "Liquichek Chemistry Control / Lyphochek Chemistry",
        "grupo": "Enzimas hepáticas",
        "causas_comunes": [
            "Hemólisis in vitro (AST eritrocitaria es 15x mayor)",
            "Temperatura incorrecta",
            "P-5-P ausente o degradado",
        ],
        "acciones_1_3s": [
            "Inspeccionar el vial (hemólisis visible = color rosado)",
            "Repetir con vial nuevo sin hemólisis",
            "Verificar temperatura (37,0 oC +/- 0,1 oC)",
        ],
        "acciones_warn": ["Mezclar por inversión suave", "Verificar absorbancia del blanco"],
        "causas_deriva": [
            "Degradación del NADH por luz",
            "Acumulación de oxalacetato en R2 abierto",
        ],
        "estabilidad_biorad": "Reconstituido: 5 días a 2-8 oC",
        "interferencias": "Hemólisis (+++ critico), lipemia moderada (+ leve)",
        "referencia": "Liquichek Chemistry Control Insert · Bio-Rad · IFCC / CLSI EP7-A2",
    },
    "GGT": {
        "producto": "Liquichek Chemistry Control",
        "grupo": "Enzimas hepáticas",
        "causas_comunes": [
            "Temperatura incorrecta (+/- 0,5 oC)",
            "pH fuera de rango (óptimo 7,9-8,2)",
            "Evaporación del substrato por mal sellado",
        ],
        "acciones_1_3s": [
            "Verificar temperatura del módulo fotométrico",
            "Comprobar pH del tampón",
            "Repetir con vial nuevo y reactivo fresco",
        ],
        "acciones_warn": [
            "Revisar fecha de preparación del reactivo",
            "Verificar ausencia de precipitados",
        ],
        "causas_deriva": [
            "Hidrólisis espontánea del substrato",
            "Fluctuación de pH por CO2 ambiental",
        ],
        "estabilidad_biorad": "Reconstituido: 5 días a 2-8 oC",
        "interferencias": "Hemólisis leve (mínimo), lipemia >1000 mg/dL (+)",
        "referencia": "Liquichek Chemistry Control Insert · Bio-Rad · ECCLS / DGKC",
    },
    "LDH": {
        "producto": "Liquichek Chemistry Control / Lyphochek Chemistry",
        "grupo": "Enzimas hepáticas",
        "causas_comunes": [
            "Hemólisis (LDH eritrocitaria es 160x mayor)",
            "Temperatura critica: cada oC modifica la actividad ~8-10%",
            "Inhibición por exceso de piruvato",
        ],
        "acciones_1_3s": [
            "Inspeccionar el vial (hemólisis = causa más frecuente)",
            "Repetir con vial nuevo sin hemólisis",
            "Verificar temperatura (37,0 oC)",
        ],
        "acciones_warn": [
            "Verificar que el reactivo no tiene precipitados",
            "Atemperar el reactivo antes de su uso",
        ],
        "causas_deriva": [
            "Degradación del NADH por congelación repetida",
            "Cambio de isoenzimas por lote diferente",
        ],
        "estabilidad_biorad": "Reconstituido: 24 h a 2-8 oC (muy lábil - usar el mismo día)",
        "interferencias": "Hemólisis (+++ critico), oxalato (-), urea elevada (- leve)",
        "referencia": "Liquichek Chemistry Control Insert · Bio-Rad · IFCC/DGKC",
    },
    "Colesterol": {
        "producto": "Liquichek Lipid Control / Lyphochek Lipid",
        "grupo": "Lípidos",
        "causas_comunes": [
            "Diferencia de método: CHOD-PAP vs Abell-Kendall",
            "Interferencia por bilirrubina >5 mg/dL",
            "Calibrador no trazable a NIST SRM 1951c",
        ],
        "acciones_1_3s": [
            "Verificar que los valores del insert corresponden a TU método",
            "Repetir con vial nuevo",
            "Recalibrar con calibrador trazable a NIST SRM 1951c",
        ],
        "acciones_warn": ["Verificar mezcla del vial (colesterol puede precipitar)"],
        "causas_deriva": [
            "Degradación de la colesterol oxidasa (CHOD)",
            "Cambio de lote de reactivo",
        ],
        "estabilidad_biorad": "Reconstituido: 7 días a 2-8 oC",
        "interferencias": "Bilirrubina >5 mg/dL (- CHOD-PAP), hemólisis (+ leve), ácido ascórbico (-)",
        "referencia": "Liquichek Lipid Control Insert · Bio-Rad · CDC/NHLBI",
    },
    "Triglicéridos": {
        "producto": "Liquichek Lipid Control / Lyphochek Lipid",
        "grupo": "Lípidos",
        "causas_comunes": [
            "Glicerol endógeno libre en el control",
            "Interferencia por hemólisis (inhibe la peroxidasa)",
        ],
        "acciones_1_3s": [
            "Verificar si el insert especifica valores con/sin corrección por glicerol",
            "Repetir control con vial nuevo",
        ],
        "acciones_warn": ["Verificar que el control se ha atemperado correctamente"],
        "causas_deriva": ["Degradación de la lipasa pancreática", "Acumulación de glicerol libre"],
        "estabilidad_biorad": "Reconstituido: 7 días a 2-8 oC",
        "interferencias": "Hemólisis (- peroxidasa), glicerol libre (+), bilirrubina >5 mg/dL (-)",
        "referencia": "Liquichek Lipid Control Insert · Bio-Rad",
    },
    "HDL-Colesterol": {
        "producto": "Liquichek Lipid Control",
        "grupo": "Lípidos",
        "causas_comunes": [
            "Efecto matriz en métodos de precipitación directa",
            "Interferencia de VLDL elevadas",
        ],
        "acciones_1_3s": [
            "Verificar valores del insert para TU método específico de HDL",
            "Repetir con vial nuevo",
            "Recalibrar",
        ],
        "acciones_warn": ["Confirmar que el tipo de método coincide con los valores del insert"],
        "causas_deriva": ["Cambio de lote de reactivo sin recalibración"],
        "estabilidad_biorad": "Reconstituido: 7 días a 2-8 oC",
        "interferencias": "Triglicéridos >400 mg/dL (+ falso en directo), bilirrubina >10 mg/dL (+)",
        "referencia": "Liquichek Lipid Control Insert · Bio-Rad · CDC Lipid Standardization",
    },
    "TSH": {
        "producto": "Lyphochek Immunoassay Plus Control",
        "grupo": "Inmunoensayo hormonal",
        "causas_comunes": [
            "Anticuerpos heterófilos (HAMA) en ensayos sandwich",
            "Degradación por ciclos de congelación/descongelación",
        ],
        "acciones_1_3s": [
            "Verificar que el control está asignado a TU plataforma",
            "Repetir con vial nuevo",
            "Revisar número de ciclos de congelación (max. 3)",
        ],
        "acciones_warn": ["Revisar número de lote del reactivo vs calibración activa"],
        "causas_deriva": ["Cambio de lote (recalibrar obligatoriamente)"],
        "estabilidad_biorad": "Reconstituido: 30 días a 2-8 oC (Lyphochek)",
        "interferencias": "HAMA (++), biotina >20 ng/mL (-), hemólisis severa (variable)",
        "referencia": "Lyphochek Immunoassay Plus Control Insert · Bio-Rad · CLSI EP15-A3",
    },
    "T4 Libre (FT4)": {
        "producto": "Lyphochek Immunoassay Plus Control",
        "grupo": "Inmunoensayo hormonal",
        "causas_comunes": [
            "Interferencia por proteínas de unión (TBG, albúmina)",
            "Dilución incorrecta del control liofilizado",
        ],
        "acciones_1_3s": [
            "Confirmar que los valores objetivo son específicos para TU analizador",
            "Repetir con vial nuevo reconstituido correctamente",
        ],
        "acciones_warn": ["Comprobar el volumen de reconstitución exacto"],
        "causas_deriva": ["Cambio de lote de reactivo", "Degradación por temperatura inadecuada"],
        "estabilidad_biorad": "Reconstituido: 30 días a 2-8 oC (Lyphochek)",
        "interferencias": "Biotina >20 ng/mL (-), HAMA (variable), heparina IV (+ artefactual)",
        "referencia": "Lyphochek Immunoassay Plus Control Insert · Bio-Rad",
    },
    "Hemoglobina": {
        "producto": "Lyphochek Hematology / Liquichek Hematology",
        "grupo": "Hematología",
        "causas_comunes": [
            "Envejecimiento del control (eritrocitos se fragmentan)",
            "Temperatura de almacenamiento incorrecta",
        ],
        "acciones_1_3s": [
            "Verificar fecha de caducidad del vial abierto (5-7 días)",
            "Repetir con vial nuevo",
        ],
        "acciones_warn": [
            "Verificar temperatura (2-8 oC, NO congelar)",
            "Invertir suavemente 8-10 veces antes de analizar",
        ],
        "causas_deriva": ["Fragmentación progresiva de eritrocitos"],
        "estabilidad_biorad": "Abierto: 5-7 días a 2-8 oC / No congelar",
        "interferencias": "Lipemia severa (+ HGB fotométrico), ictericia severa (+ HGB)",
        "referencia": "Lyphochek Hematology Control Insert · Bio-Rad · CLSI H26-A2",
    },
    "Calcio": {
        "producto": "Liquichek Chemistry Control",
        "grupo": "Bioquímica básica",
        "causas_comunes": [
            "Interferencia por EDTA (quelante del calcio)",
            "pH del control fuera de rango",
            "Evaporación del vial",
        ],
        "acciones_1_3s": [
            "Descartar contaminación con EDTA",
            "Repetir con vial nuevo",
            "Verificar pH del reactivo",
            "Recalibrar con calibrador trazable NIST SRM 956c",
        ],
        "acciones_warn": ["Verificar tiempo de apertura del vial", "Comprobar temperatura (37 oC)"],
        "causas_deriva": [
            "Degradación del indicador o-cresolftaleína",
            "Cambio de lote de reactivo",
        ],
        "estabilidad_biorad": "Reconstituido: 5 días a 2-8 oC",
        "interferencias": "EDTA (--- critico), magnesio elevado (+ leve), hemólisis (+ leve)",
        "referencia": "Liquichek Chemistry Control Insert · Bio-Rad · CLSI EP7-A2",
    },
    "Amilasa": {
        "producto": "Liquichek Chemistry Control",
        "grupo": "Bioquímica básica",
        "causas_comunes": [
            "Temperatura de incubación incorrecta (método cinético muy sensible a T)",
            "Degradación del substrato por luz o calor",
            "Calibración desactualizada o calibrador no trazable",
            "Inhibición por EDTA si la muestra es plasma",
            "Contaminación cruzada con saliva",
        ],
        "acciones_1_3s": [
            "No liberar resultados de pacientes hasta resolver la alarma",
            "Repetir con NUEVO vial del mismo lote",
            "Si persiste: repetir con vial de LOTE DIFERENTE",
            "Verificar temperatura del módulo fotométrico (37,0 oC +/- 0,1 oC)",
            "Recalibrar con estándar trazable",
            "Documentar acción y responsable",
        ],
        "acciones_warn": [
            "Monitoreo estrecho durante 3 días",
            "Revisar tendencia en Levey-Jennings",
            "Verificar temperatura del baño",
            "Comprobar absorbancia del blanco (<1.5 AU)",
        ],
        "causas_deriva": [
            "Deterioro del substrato (sensible a temperatura y luz)",
            "Deriva del calibrador",
            "Cambio de lote sin ajuste de valores objetivo",
        ],
        "estabilidad_biorad": "Reconstituido: 5 días a 2-8 oC",
        "interferencias": "EDTA (-), hemólisis leve (mínimo), lipemia >500 mg/dL (variable), bilirrubina >20 mg/dL (leve)",
        "referencia": "Liquichek Chemistry Control Insert · Bio-Rad / IFCC método cinético colorimétrico",
    },
}

GRUPOS_ANALITICOS = {
    "Bioquímica básica": ["Glucosa", "Potasio (K+)", "Sodio", "Creatinina", "Calcio", "Amilasa"],
    "Enzimas hepáticas": ["ALT (Transaminasa)", "AST", "GGT", "LDH"],
    "Lípidos": ["Colesterol", "Triglicéridos", "HDL-Colesterol"],
    "Inmunoensayo hormonal": ["TSH", "T4 Libre (FT4)"],
    "Hematología": ["Hemoglobina"],
}


def buscar_kb(analito, estado):
    if analito in BIORAD_KB:
        return BIORAD_KB[analito]
    an_norm = analito.lower()
    for key in BIORAD_KB:
        if an_norm in key.lower() or key.lower() in an_norm:
            return BIORAD_KB[key]
    return None


# ==============================================================
# COBAS 8000 KB
# ==============================================================
COBAS_8000_KB = """
=== ANALIZADOR MODULAR COBAS® 8000 ===
- Módulos: cobas ISE (Na+,K+,Cl-,Ca++), c701/c702/c502 (fotométrico), e602 (ECL).
- Calibración ISE: cada 24 horas obligatorio.
- Bandeja verde: procesar antes de la calibración diaria ISE (~20 min).
- Limpieza pipeta diaria: Standby → abrir cubierta → gasa con alcohol de arriba abajo.
- Limpiar puertos vaciado ISE: gasa + agua desionizada al finalizar el día.
- Temperatura baño fotométrico: 37,0 °C ± 0,1 °C (crítico para ALT/AST/LDH).
- Longitud de onda NADH: 340 nm (ALT, AST, LDH).
- Interlock: cubierta abierta = equipo se detiene, muestras inválidas.
TROUBLESHOOTING:
- Error QC ISE: limpiar puerto vaciado, revisar electrodo, bandeja verde + calibrar.
- Error QC enzimas: verificar temperatura 37,0°C, verificar fotómetro 340nm.
- Alarma Interlock: cerrar cubierta, reinicializar módulo.
- Calibración ISE no válida: procesar bandeja verde → calibrar ISE.
"""


# ==============================================================
# SIGMA METRICS – TEa CLIA
# ==============================================================
TEA_CLIA = {
    "Potasio (K+)": (8.0, "mmol/L", "CLIA"),
    "ALT (Transaminasa)": (20.0, "U/L", "CLIA"),
    "Glucosa": (10.0, "mg/dL", "CLIA"),
    "Sodio": (4.0, "mmol/L", "CLIA"),
    "Creatinina": (15.0, "mg/dL", "CLIA"),
    "Colesterol": (10.0, "mg/dL", "CLIA"),
    "Hemoglobina": (7.0, "g/dL", "CLIA"),
    "Calcio": (8.0, "mg/dL", "CLIA"),
    "Triglicéridos": (25.0, "mg/dL", "CLIA"),
    "HDL-Colesterol": (30.0, "mg/dL", "CLIA"),
    "TSH": (25.0, "mIU/L", "CLIA"),
    "T4 Libre (FT4)": (20.0, "ng/dL", "CLIA"),
    "AST": (20.0, "U/L", "CLIA"),
    "GGT": (20.0, "U/L", "CLIA"),
    "LDH": (20.0, "U/L", "CLIA"),
    "Amilasa": (30.0, "U/L", "CLIA"),
}
TEA_DEFAULT = 15.0
