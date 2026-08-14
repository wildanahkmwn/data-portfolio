# Architecture

## Goal

Show a demable path from operational Postgres orders to trusted ClickHouse metrics
and a stakeholder dashboard.

## Components

| Component | Role |
|---|---|
| Postgres `marketplace_orders` | System of record (OLTP) |
| `sample_data/orders.csv` | Anonymized seed extract |
| `scripts/stream_worker.py` | Watermark poll + batched ClickHouse inserts |
| ClickHouse `raw_orders` | ReplacingMergeTree sink |
| ClickHouse marts | Daily sales, LTV, top products |
| `checks/data_quality.py` | PG vs CH parity plus nulls/dups/freshness |
| Metabase | Client-facing BI |
| Streamlit `app/dashboard.py` | Optional demo app |

## Ingestion

Batched inserts from a stream worker. Official ClickHouse guidance prefers
healthy batch sizes over many tiny writes:
https://clickhouse.com/docs/best-practices/selecting-an-insert-strategy

`wal_level=logical` is on so this can later move to Debezium/Kafka or
MaterializedPostgreSQL without redesigning the source.

## Data model

### marketplace_orders (Postgres)
Grain: one row per order line. Unique `(order_id, product_id)`.

### raw_orders (ClickHouse)
Same grain. `ReplacingMergeTree(synced_at)` keyed by business keys + `source_id`.

### mart_daily_sales / mart_customer_ltv / mart_top_products
Aggregates rebuilt after each non-empty sync.

## Quality gates

1. raw table not empty
2. no blank order_id
3. no duplicate (order_id, product_id)
4. marts populated
5. raw GMV equals mart daily GMV
6. Postgres row count and GMV match ClickHouse
7. latest order within freshness SLA
