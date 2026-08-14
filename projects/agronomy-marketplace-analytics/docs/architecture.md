# Architecture

## Goal

Show a complete, demable path from agronomy marketplace transactions to trusted metrics.

## Components

| Component | Role |
|---|---|
| `sample_data/orders.csv` | Anonymized marketplace order lines (IDs hashed, no PII) |
| `scripts/run_pipeline.py` | Local orchestrator |
| `dags/ecommerce_ingest_dag.py` | Airflow orchestration (optional) |
| ClickHouse `raw_orders` | Immutable-ish landing table |
| ClickHouse marts | Business-ready aggregates |
| `checks/data_quality.py` | Gate before serving |
| `app/dashboard.py` | Consumption layer |

## Data model

### raw_orders
Grain: one row per order line item.

### mart_daily_sales
Grain: one row per order_date.
Metrics: orders, gmv, aov, units.

### mart_customer_ltv
Grain: one row per customer_id.
Metrics: orders, gmv, aov, first/last order date.

### mart_top_products
Grain: one row per product_id.
Metrics: orders, units, gmv.

## Quality gates

1. raw table not empty
2. no blank order_id
3. no duplicate (order_id, product_id)
4. marts populated
5. raw GMV equals mart daily GMV
6. latest order within freshness SLA

## How to extend toward production

- Swap CSV for Shopify/Odoo/API extract
- Add incremental watermark (`loaded_at` / `updated_at`)
- Add dbt tests instead of (or in addition to) Python checks
- Add Slack/Lark alert on quality failure
- Separate bronze/silver/gold databases
