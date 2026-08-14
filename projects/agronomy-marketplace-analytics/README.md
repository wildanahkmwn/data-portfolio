# Agronomy Marketplace Analytics

End-to-end portfolio project for an agronomy marketplace:
masked order lines -> ClickHouse marts -> data quality checks -> Streamlit dashboard.

Part of the [data portfolio monorepo](../../README.md).

## Domain

Sample data is an **anonymized extract** of marketplace order lines for agricultural inputs
(seeds, fertilizer, herbicides, tools, and related SKUs). Buyer identities are pseudonymized;
no phones, emails, or addresses are included.

## Architecture

```text
masked orders CSV
        |
        v
  Python ingest (Airflow DAG or CLI)
        |
        v
   ClickHouse (raw + marts)
        |
   +----+----+
   |         |
   v         v
 quality   Streamlit
 checks    dashboard
```

## Quick start

```bash
docker compose up -d
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/run_pipeline.py
python checks/data_quality.py
streamlit run app/dashboard.py
```

Dashboard: http://localhost:8501

### Dashboard preview

![Agronomy Marketplace Sales Dashboard](docs/screenshots/dashboard-metrics.png)

## What you get

- Incremental-style load into ClickHouse (`raw_orders`)
- SQL marts: daily sales, customer LTV, top products
- Data quality checks: nulls, duplicates, freshness
- Streamlit dashboard: GMV, AOV, orders, top products, freshness

## Airflow (optional)

Copy `dags/ecommerce_ingest_dag.py` into your Airflow `dags/` folder.
Env vars: `CLICKHOUSE_HOST`, `CLICKHOUSE_PORT`, `CLICKHOUSE_USER`,
`CLICKHOUSE_PASSWORD`, `CLICKHOUSE_DATABASE` (defaults target local demo).

## Layout

```text
agronomy-marketplace-analytics/
  docker-compose.yml
  requirements.txt
  app/dashboard.py
  checks/data_quality.py
  dags/ecommerce_ingest_dag.py
  scripts/
  sql/
  sample_data/orders.csv
  docs/
    architecture.md
    case_study.md
    screenshots/
```

## Metrics

| Metric | Definition |
|---|---|
| GMV | Sum of `quantity * unit_price` |
| Orders | Distinct `order_id` |
| AOV | GMV / Orders |
| Top products | Revenue by `product_name` |
| Freshness | Hours since latest load |

## Case study / attachments

- [Case study](docs/case_study.md)
- Screenshot: `docs/screenshots/dashboard-metrics.png`
- Shared freelance pack (repo root): `../../docs/freelance_profile.md`
