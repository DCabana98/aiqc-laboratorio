# 🔬 AIQC — Artificial Intelligence for Quality Control

Aplicación **Streamlit** para el control de calidad (QC) de un laboratorio
clínico. Evalúa controles **Bio-Rad** (Liquichek / Lyphochek) procesados en un
analizador **Roche cobas® 8000**, con datos servidos desde **OpenLab** (Agilent)
vía GitHub. Incluye reglas de Westgard, gráficos Levey-Jennings, detección
temprana de tendencias (EWMA / CUSUM), Sigma Metrics (CLIA), generación de
informes PDF/CSV y un asistente conversacional con **Google Gemini**.

**Versión:** 4.13

---

## ✨ Funcionalidades

- **Reglas de Westgard** multinivel: `1_3s`, `2_2s`, `4_1s`, `10_x`, `1_2s` (warning) y **R-4s** (error aleatorio entre niveles).
- **Levey-Jennings** interactivo (Plotly) con zonas ±1/2/3 SD coloreadas.
- **EWMA** (deriva sostenida) y **CUSUM** (tendencias) con parámetros ajustables (λ, k, h).
- **Sigma Metrics** según error total admisible (TEa) de **CLIA**, editable por analito.
- **Base de conocimiento Bio-Rad**: causas probables, acciones correctivas, interferencias y estabilidad por analito.
- **Manual cobas® 8000** integrado para el asistente IA.
- **Informes**: PDF firmado (fpdf2) y CSV compatible con Excel (UTF-8 BOM, `;`).
- **Asistente IA (Gemini)** con inyección de los datos reales de QC.
- **Gestión de usuarios** con roles (`admin`, `supervisor`, `tecnico`), bcrypt y registro de **auditoría**.
- **Fuentes de datos** con prioridad: GitHub/OpenLab → archivo subido → modo demo.

---

## 🗂 Estructura del proyecto

```
.
├── app.py                       # Punto de entrada Streamlit (UI + pestañas)
├── aiqc/                        # Paquete con toda la lógica
│   ├── __init__.py
│   ├── styles.py                # CSS de la interfaz
│   ├── knowledge_base.py        # Bio-Rad KB, niveles, cobas 8000, TEa CLIA
│   ├── database.py              # SQLite: usuarios, acciones, auditoría, login
│   ├── data_io.py               # Demo, lectura CSV/Excel, sync GitHub/OpenLab
│   ├── qc_rules.py              # Westgard, R-4s, EWMA, CUSUM, Sigma
│   ├── charts.py                # Figuras Plotly y paneles de UI
│   ├── reports.py               # Exportación PDF y CSV
│   └── ai_assistant.py          # Asistente Google Gemini
├── data/
│   └── controles_qc.example.csv # CSV de ejemplo (formato OpenLab)
├── .streamlit/
│   └── secrets.toml.example     # Plantilla de secretos
├── .github/workflows/ci.yml     # CI: formato (black), sintaxis e import
├── pyproject.toml               # Configuración de black
├── requirements.txt             # Dependencias de ejecución
├── requirements-dev.txt         # + black (desarrollo)
├── README.md
├── ARCHITECTURE.md              # Análisis de arquitectura y hoja de ruta
└── CLAUDE.md                    # Guía para agentes / contribuidores
```

> 📐 Para el análisis de la arquitectura actual y el camino hacia un producto en
> condiciones (API, integración real de datos vía HL7/ASTM/FHIR, requisitos
> clínicos), consulta **[ARCHITECTURE.md](ARCHITECTURE.md)**.

---

## 🚀 Puesta en marcha local

Requiere **Python 3.11+**.

```bash
# 1. Clonar
git clone https://github.com/<usuario>/<repo>.git
cd <repo>

# 2. Entorno virtual (recomendado)
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Dependencias
pip install -r requirements.txt

# 4. Secretos (opcional para el modo demo; obligatorio para Gemini/GitHub)
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
#   edita .streamlit/secrets.toml con tus valores

# 5. Ejecutar
streamlit run app.py
```

La app abre en `http://localhost:8501`. Sin configurar fuentes externas arranca
en **modo demo** con datos simulados de Amilasa y ALT.

**Login inicial:** usuario `admin`, contraseña la definida en
`[auth].admin_password` (por defecto `admin2024`). Se crea automáticamente la
primera vez que se inicializa la base de datos.

---

## ☁️ Despliegue en Streamlit Community Cloud

1. Sube este repositorio a GitHub.
2. En [share.streamlit.io](https://share.streamlit.io) crea una app apuntando a `app.py`.
3. En **Settings → Secrets**, pega el contenido de tu `secrets.toml`
   (mismo formato que `.streamlit/secrets.toml.example`).

> El `requirements.txt` se instala automáticamente. `kaleido` permite exportar
> los gráficos Levey-Jennings al PDF; si no está disponible, el PDF se genera
> igualmente sin las imágenes.

---

## ⚙️ Configuración (`secrets.toml`)

| Sección    | Clave            | Descripción                                                        |
|------------|------------------|--------------------------------------------------------------------|
| `[auth]`   | `admin_password` | Contraseña del `admin` inicial (solo al crear la BD vacía).        |
| `[db]`     | `path`           | Ruta del SQLite. Vacío = `~/.aiqc/aiqc_acciones.db`.               |
| `[gemini]` | `api_key`        | Clave de Google Gemini ([aistudio.google.com/apikey](https://aistudio.google.com/apikey)). |
| `[github]` | `usuario`/`repo`/`rama`/`archivo`/`token` | CSV de OpenLab servido en GitHub.       |
| `[lab]`    | `nombre`         | Nombre del laboratorio en los informes PDF.                        |

La variable de entorno `GEMINI_API_KEY` también es válida como alternativa a `[gemini].api_key`.

---

## 📄 Formato de datos QC

CSV o Excel con estas columnas (los nombres admiten sinónimos y se normalizan
automáticamente):

| Columna          | Obligatoria | Ejemplo            |
|------------------|:-----------:|--------------------|
| `Fecha`          | ✅          | `01/06/2025`       |
| `Analito`        | ✅          | `Glucosa`          |
| `Valor`          | ✅          | `100.4`            |
| `Media_Objetivo` | ✅          | `100.0`            |
| `SD_Objetivo`    | ✅          | `2.0`              |
| `Nivel`          | —           | `N` / `PB` / `PA`  |
| `Lote`           | —           | `LOT-2025-A`       |

Niveles: `N` (Normal), `PB` (Patológico Bajo), `PA` (Patológico Alto).
Ver [`data/controles_qc.example.csv`](data/controles_qc.example.csv).

---

## 🛠 Desarrollo

El formato del código lo impone **[Black](https://black.readthedocs.io/)**
(configurado en `pyproject.toml`, `line-length = 100`). El CI verifica el
formato, la sintaxis y que el paquete importe.

```bash
pip install -r requirements-dev.txt
black app.py aiqc/            # formatear
black --check --diff app.py aiqc/   # lo que valida el CI
```

---

## 🔒 Seguridad

- Contraseñas con **bcrypt**; nunca se almacenan en claro.
- `secrets.toml` y `*.db` están en `.gitignore` — **no** se suben al repositorio.
- Registro de **auditoría** de logins, exportaciones y cambios.

---

## 📜 Licencia

Uso interno de laboratorio. Define aquí la licencia que corresponda antes de
publicar el repositorio.
