# Agronomy Marketplace Analytics Pipeline

End-to-end portfolio project for an agronomy marketplace:
masked order lines -> ClickHouse marts -> data quality checks -> Streamlit dashboard.

Built to demonstrate the same pattern used in production stacks:
ingest -> warehouse -> transform -> data quality -> serve.

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

## What you get

- Incremental-style load into ClickHouse (`raw_orders`)
- SQL marts: daily sales, customer LTV, top products
- Data quality checks: nulls, duplicates, freshness
- Streamlit dashboard: GMV, AOV, orders, top products, freshness

## Quick start (no Airflow required)

### 1. Start ClickHouse

```bash
docker compose up -d
```

### 2. Install Python deps

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Create tables + load sample data + build marts

```bash
python scripts/run_pipeline.py
```

### 4. Run quality checks

```bash
python checks/data_quality.py
```

### 5. Open dashboard

```bash
streamlit run app/dashboard.py
```

Dashboard: http://localhost:8501

### Dashboard preview

![Agronomy Marketplace Sales Dashboard](docs/screenshots/dashboard-metrics.png)

## Airflow (optional)

Copy `dags/ecommerce_ingest_dag.py` into your Airflow `dags/` folder.
Set connection/env:

- `CLICKHOUSE_HOST` (default `localhost`)
- `CLICKHOUSE_PORT` (default `8123`)
- `CLICKHOUSE_USER` (default `default`)
- `CLICKHOUSE_PASSWORD` (default empty)
- `CLICKHOUSE_DATABASE` (default `ecommerce`)

The DAG runs daily: create schema -> load -> transform -> quality checks.

## Project layout

```text
ecommerce-clickhouse-pipeline/
  docker-compose.yml
  requirements.txt
  dags/
    ecommerce_ingest_dag.py
  sql/
    01_raw_orders.sql
    02_mart_daily_sales.sql
    03_mart_customer_ltv.sql
    04_mart_top_products.sql
  checks/
    data_quality.py
  app/
    dashboard.py
  scripts/
    run_pipeline.py
    export_masked_sample.py
    generate_sample_data.py
  sample_data/
    orders.csv
  docs/
    architecture.md
    linkedin_case_study.md
    services_one_pager.md
    screenshots/
```

## Metrics on the dashboard

| Metric | Definition |
|---|---|
| GMV | Sum of `quantity * unit_price` |
| Orders | Distinct `order_id` |
| AOV | GMV / Orders |
| Top products | Revenue by `product_name` |
| Freshness | Hours since latest `order_date` / load time |

## Why this portfolio matters

Recruiters and clients care less about notebooks and more about:

1. Can you design a clear data flow?
2. Can you model marts that answer business questions?
3. Do you check data quality before serving?
4. Can a non-engineer use the output?

This repo is a compact answer to all four.

## License

MIT
