# SIG de la Informalidad Laboral en Villarrica (UNVES 2026)

Proyecto interdisciplinario del 8.° semestre de la Licenciatura en Administración de Empresas, Facultad de Ciencias Económicas, Universidad Nacional de Villarrica del Espíritu Santo (UNVES). Cátedras: Sistema de Información Gerencial, Análisis de la Realidad Social del Paraguay y Marketing Social.

- **Dashboard gerencial:** https://gilgapy.github.io/sig-informalidad-villarrica/
- **Informe final (APA 7):** [`docs/informe_final_unves_2026.docx`](docs/informe_final_unves_2026.docx)

## Contenido del repositorio

| Carpeta | Qué contiene |
| :--- | :--- |
| `kobo/` | Formulario XLSForm de KoboToolbox y su especificación |
| `data/raw/` | Exportación cruda de la encuesta (formato KoboToolbox / ODK) |
| `data/processed/` | Trabajadores, unidades productivas, métricas de campaña y derivaciones |
| `data/DATA_DICTIONARY.md` | Diccionario de datos de todos los conjuntos |
| `scripts/` | Pipeline de datos en Python (`run_pipeline.py`) y verificaciones |
| `db/` | Esquema PostgreSQL en 3FN (`schema.sql`), carga ETL y pruebas de integridad |
| `r-analysis/` | Análisis estadístico en R, datos analíticos y gráficos APA |
| `docs/` | Dashboard, diagrama ER, informe, presentación, flyer y capturas |
| `mcp-server/` | Servidor MCP (Node.js / TypeScript) con la guía docente |

## Cómo replicar el estudio

Requisitos: Python 3.9 o superior, PostgreSQL 16 y R 4.2 o superior.

```bash
git clone https://github.com/gilgapy/sig-informalidad-villarrica.git
cd sig-informalidad-villarrica
pip install pandas numpy scipy matplotlib psycopg2-binary
```

**1. Conjuntos de datos.** `run_pipeline.py` escribe `data/raw/` y `data/processed/` y verifica su consistencia. Las unidades productivas, la exportación de la encuesta y las métricas de campaña se generan con los scripts `generate_*.py` (semilla fija `20261016`, por lo que el resultado es siempre el mismo); los indicadores sociales de los trabajadores se calculan a partir de esa exportación. Para procesar una exportación propia de KoboToolbox se usa `scripts/import_field_data.py`.

```bash
python3 scripts/run_pipeline.py
```

**2. Base de datos.** La conexión se configura con las variables `PGDATABASE`, `PGUSER`, `PGHOST`, `PGPORT` y `PGPASSWORD` (o `DATABASE_URL`).

```bash
createdb unves_sig_2026
psql -d unves_sig_2026 -f db/schema.sql
python3 db/load_data.py
python3 db/test_db_integrity.py
python3 scripts/export_analytical_datasets.py   # vistas → r-analysis/data/ y dashboard
```

**3. Análisis estadístico.** Desde la raíz del repositorio:

```bash
Rscript -e 'install.packages(c("ggplot2","dplyr","readr","tidyr","scales","jsonlite"))'
Rscript r-analysis/scripts/analisis_econometrico.R
```

Los gráficos y el reporte APA quedan en `r-analysis/output/`.

**4. Dashboard.** Abrir `docs/dashboard.html` en el navegador; lee `docs/dashboard_data.js`.
