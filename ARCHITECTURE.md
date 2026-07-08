# Arquitectura y evolución de AIQC

Este documento recoge el análisis de la arquitectura actual de AIQC y el camino
para convertirlo en un **producto en condiciones** para entorno de laboratorio
clínico. Es un documento vivo: refleja decisiones y opciones, no un compromiso
cerrado.

> **TL;DR** — Lo más valioso ya está hecho: la lógica de control de calidad está
> separada de la interfaz (paquete `aiqc/` vs `app.py`). El siguiente paso de
> bajo riesgo y alto valor es **envolver `aiqc/` en una API (FastAPI)**
> manteniendo Streamlit como frontend interno, y **sustituir la fuente de datos
> CSV/GitHub por una entrada realista** (API push del LIS → HL7/ASTM/FHIR).

---

## 1. ¿Tiene sentido Streamlit para este caso?

**Para el estado actual (demo / prototipo / herramienta interna de 1-5 personas):
sí.** Streamlit permitió construir algo funcional muy rápido y no debe
descartarse a la ligera.

**Para un producto real: se queda corto**, por razones concretas (no estéticas):

| Limitación de Streamlit | Por qué importa en este caso |
|---|---|
| Re-ejecuta todo el script en cada interacción | No escala a muchos usuarios concurrentes; la lógica de QC se recalcula constantemente |
| No separa frontend/backend | No puede exponer una API para que el LIS/middleware, OpenLab o un móvil consuman datos |
| Estado en memoria de sesión | Se pierde al recargar; no sirve para multiusuario real |
| Autenticación/autorización débil | bcrypt + roles es un buen empiece, pero no es grado clínico (sin MFA, SSO, gestión de sesiones robusta) |
| Difícil de testear | El acoplamiento UI-lógica complica las pruebas automatizadas, obligatorias en software clínico |
| Auditoría/trazabilidad | ISO 15189 / CLIA exigen un audit trail inmutable, no una tabla SQLite editable |

**Punto clave:** ya se hizo lo más importante al separar la lógica (`aiqc/`) de
la UI (`app.py`). Esa lógica (Westgard, EWMA, CUSUM, Sigma) es reutilizable tal
cual con cualquier frontend o backend.

---

## 2. Opciones de arquitectura (de menos a más esfuerzo)

### Opción A — Endurecer Streamlit

Mantener `aiqc/` como está y profesionalizar solo el entorno: Postgres en vez de
SQLite, autenticación vía proveedor (Auth0/Cognito), despliegue en contenedor.

- **Cuándo:** herramienta interna, pocos usuarios, sin necesidad de API ni móvil.
- **Coste:** bajo · **Techo:** bajo.

### Opción B — Separar backend (API) + frontend  ⭐ recomendada como siguiente paso

Transición natural. Se introduce una API que usa `aiqc/` como motor de cálculo;
el frontend (Streamlit y/o web) consume esa API.

```
                    ┌─────────────────────────┐
   LIS / OpenLab ──▶│   API  (FastAPI)        │◀── Frontend web (React/Next)
   middleware       │   ┌───────────────────┐ │◀── Streamlit (panel interno)
   HL7/ASTM         │   │  aiqc/ (la lógica)│ │◀── App móvil (futuro)
                    │   └───────────────────┘ │
                    │   Postgres + audit log  │
                    └─────────────────────────┘
```

- **`aiqc/` no cambia** — se convierte en el motor que la API llama. Aquí se nota
  el valor de haber separado la lógica.
- **FastAPI** expone endpoints (`POST /qc/evaluate`,
  `GET /analytes/{id}/levey-jennings`, etc.): estándar Python, rápido, tipado,
  documentación automática (OpenAPI/Swagger), testeable.
- **Frontend:** React/Next.js para UI rica, o se deja **Streamlit como panel
  interno** consumiendo la API. Pueden coexistir ambos.

- **Cuándo:** cualquier cosa más allá de uso interno trivial.
- **Coste:** medio · **Techo:** alto.

### Opción C — Plataforma SaaS multi-tenant completa

Todo lo de B + aislamiento de datos por laboratorio, facturación, escalado
horizontal, observabilidad y cumplimiento formal. Es un producto de empresa.

- **Cuándo:** vender a varios laboratorios como SaaS.
- **Coste:** alto · **Techo:** muy alto.

---

## 3. Fuentes de datos — el cambio más importante

La fuente actual (**CSV vía GitHub**) es un buen *stub* para la demo, pero **no es
como llegan los datos en un laboratorio real**. El flujo real:

```
Analizador          Middleware / LIS        Sistema QC
(cobas 8000)  ──▶   (OpenLab, etc.)   ──▶   AIQC
   HL7 / ASTM        normaliza, enruta
```

### Evolución por orden de realismo

| Hoy (demo) | Intermedio | Producción real |
|---|---|---|
| CSV en GitHub | El laboratorio programa export CSV a un endpoint | **Integración directa con el middleware/LIS** |
| Polling cada 60 min | API REST que el LIS llama (`POST /qc/results`) | **HL7 v2 / ASTM E1394** (protocolos de instrumentos clínicos) o **HL7 FHIR** (moderno) |
| — | Webhook desde OpenLab | Conector que escucha el stream del analizador en tiempo real |

Protocolos reales del dominio: **HL7 v2** y **ASTM E1394 / LIS2-A** (lo que
hablan analizadores y middleware como OpenLab de Agilent), y **HL7 FHIR** para
interoperabilidad moderna.

### Cambios concretos

1. **Corto plazo:** sustituir `leer_csv_github()` por un endpoint al que el LIS
   empuje resultados (`POST /qc/results`). Cambia *cómo entran* los datos sin
   tocar la lógica de QC.
2. **Medio plazo:** un módulo `connectors/` con un parser HL7/ASTM que traduzca
   los mensajes del analizador al DataFrame estándar
   (`Fecha, Analito, Nivel, Valor, Media_Objetivo, SD_Objetivo, Lote`).
3. **Largo plazo:** conector bidireccional certificado con el middleware.

> **Nota de diseño:** `normalizar_df()` ya es la pieza correcta — es la "frontera"
> donde cualquier fuente se traduce al formato interno. En producción habría
> varios *adapters* (CSV, HL7, FHIR, API) alimentando esa misma frontera.

```
   CSV adapter ─┐
   API adapter ─┤
   HL7 adapter ─┼──▶ normalizar_df()  ──▶  DataFrame estándar  ──▶  aiqc/qc_rules
   FHIR adapter ┘
```

---

## 4. Qué más necesita un "producto en condiciones" (laboratorio clínico)

Esto distingue el software clínico de una app normal. Conviene tenerlo en el
radar aunque no se aborde de inmediato:

- **Base de datos de verdad:** PostgreSQL con migraciones (Alembic), no SQLite.
- **Audit trail inmutable:** requisito de ISO 15189 / CLIA / CAP. Quién vio o
  cambió qué y cuándo, sin posibilidad de borrado.
- **Tests automatizados:** prácticamente obligatorios para lógica clínica. La
  buena noticia: `qc_rules.py` es Python puro, trivial de testear con `pytest`.
- **Autenticación robusta:** SSO/MFA, gestión de sesiones; no bcrypt casero.
- **Validación y trazabilidad de cálculos:** documentar que las reglas de
  Westgard/Sigma están validadas frente a una referencia.
- **Privacidad:** los datos de QC no son datos de paciente (ventaja), pero si el
  sistema se conecta a infraestructura con PHI aplican RGPD/HIPAA.
- **Asistente Gemini:** en producción clínica, enviar datos a una API externa
  (Google) requiere revisión de privacidad y probablemente un acuerdo de
  tratamiento de datos (DPA). Considerar opción de desactivarlo o usar un modelo
  autoalojado para clientes sensibles.

---

## 5. Plan por fases (camino recomendado)

Ninguna fase obliga a reescribir la lógica de QC.

### Fase 0 — Donde estamos
- App Streamlit funcional, lógica separada en `aiqc/`, CI con formato e import.
- Fuente de datos: CSV/GitHub + carga manual + demo. SQLite local.

### Fase 1 — Endurecer (Opción A)
- [ ] Migrar SQLite → PostgreSQL (con Alembic).
- [ ] Externalizar autenticación (proveedor con MFA).
- [ ] Contenerizar (Docker) y desplegar en infraestructura controlada.
- [ ] Suite `pytest` para `qc_rules.py` (Westgard, R-4s, EWMA, CUSUM, Sigma).
- [ ] Audit trail en tabla append-only.

### Fase 2 — API (Opción B)
- [ ] Envolver `aiqc/` en **FastAPI**; endpoints de evaluación y consulta.
- [ ] Endpoint `POST /qc/results` para que el LIS empuje datos.
- [ ] Streamlit pasa a consumir la API (deja de calcular en proceso).
- [ ] (Opcional) Frontend web React/Next consumiendo la misma API.

### Fase 3 — Integración real de datos
- [ ] Módulo `connectors/` con *adapters* (CSV, API, HL7 v2, ASTM, FHIR).
- [ ] Parser HL7/ASTM → `normalizar_df()`.
- [ ] Conector con middleware/OpenLab (push o stream en tiempo real).

### Fase 4 — Producto / SaaS (Opción C, si aplica)
- [ ] Multi-tenancy con aislamiento de datos por laboratorio.
- [ ] Observabilidad (logs, métricas, alertas), escalado horizontal.
- [ ] Cumplimiento formal (ISO 15189 / CLIA), validación documentada.
- [ ] Revisión de privacidad del asistente IA (DPA / modelo autoalojado).

---

## 6. Principio rector

> Mantener la **lógica de dominio (`aiqc/`) independiente de la UI, del
> almacenamiento y de la fuente de datos**. Toda fuente entra por la frontera
> `normalizar_df()` y toda salida (UI, API, informes) consume el mismo
> `DataFrame` estándar. Mientras se respete esto, cada capa (frontend, backend,
> conectores, base de datos) puede evolucionar de forma independiente sin
> reescribir el núcleo de control de calidad.
