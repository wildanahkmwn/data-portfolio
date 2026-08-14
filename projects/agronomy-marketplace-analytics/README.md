# Agronomy Marketplace Analytics

One project, three hats:

| Hat | What you show |
|---|---|
| **Data Engineer** | Postgres -> ClickHouse stream, marts, quality gates |
| **Data Analyst** | Business questions: category mix, repeat rate, weekday, cohort LTV |
| **Data Scientist** | GMV 14-day forecast + buyer reactivation ranking |

Part of the [data portfolio monorepo](../../README.md).

## Domain

Anonymized marketplace order lines for agricultural inputs
(seeds, fertilizer, herbicides, tools). Buyer identities are hashed;
no phones, emails, or addresses.

## Architecture

```text
Postgres marketplace_orders
        |
        |  watermark stream
        v
ClickHouse raw + marts + quality
        |
   +----+------+------------------+
   |           |                  |
   v           v                  v
Metabase    Analyst SQL        Forecast /
(client BI) insights           reactivation
```

## Quick start

```bash
cd projects/agronomy-marketplace-analytics
docker compose up -d --build
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/run_pipeline.py
python checks/data_quality.py
```

### Data Engineer checks

```bash
python scripts/seed_more.py 5
python checks/data_quality.py
```

### Data Analyst pack

```bash
python scripts/run_analysis.py
```

See `analysis/insights.md` for how to phrase takeaways.

### Data Scientist pack

```bash
python science/forecast_daily_gmv.py
python science/reactivation_priority.py
```

### Dashboards

- Metabase (client BI): http://localhost:3000
  - ClickHouse host `clickhouse`, port `8123`, user `default`, password `analytics`, SSL off
- Streamlit demo: `streamlit run app/dashboard.py` -> http://localhost:8501

### Dashboard preview

![Agronomy Marketplace Sales Dashboard](docs/screenshots/dashboard-metrics.png)

## Dashboard tool choice

| Tool | Sell as |
|---|---|
| **Metabase** | Default BI for SME/startup clients |
| Streamlit | Demo / internal prototype only |
| Power BI / Tableau | Only if the client already licenses it |

## Ports

| Service | Port | Login |
|---|---|---|
| Postgres | 5434 | agro / agro |
| ClickHouse | 8123 | default / analytics |
| Metabase | 3000 | first-run wizard |
| Streamlit | 8501 | local |

## Layout

```text
agronomy-marketplace-analytics/
  analysis/          # DA SQL + insights
  science/           # DS forecast + reactivation
  app/dashboard.py   # Streamlit demo
  checks/
  postgres/
  scripts/
  sql/
  docs/case_study.md
```

## Case study / attachments

- [Case study](docs/case_study.md) — DE + DA + DS in one page
- Screenshot: `docs/screenshots/dashboard-metrics.png`
- Shared pack: `../../docs/freelance_profile.md`
