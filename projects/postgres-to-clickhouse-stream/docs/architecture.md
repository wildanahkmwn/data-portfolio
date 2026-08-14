# Architecture notes

## Workload

- Shape: operational Postgres orders mirrored for analytics
- Latency target: seconds (near-real-time), not sub-second
- Query pattern: daily GMV / order counts in ClickHouse

## Ingestion decision

For this demo volume, use **direct batched inserts** from a stream worker.

Provenance: official ClickHouse guidance prefers appropriately sized batches
over many tiny inserts. See:
https://clickhouse.com/docs/best-practices/selecting-an-insert-strategy

When producers multiply or replay is required, move the stream behind Kafka
(derived pattern) or adopt logical CDC.

## Tables

### Postgres `marketplace_orders`
System of record. Indexed on `(updated_at, id)` for watermark scans.

### ClickHouse `pg2ch.raw_orders`
`ReplacingMergeTree(synced_at)` ordered by business keys + `source_id`.

### ClickHouse `pg2ch.stream_watermarks`
Operability state: last synced timestamp/id and batch size.

### ClickHouse `pg2ch.mart_daily_sales`
Simple aggregate rebuilt after each non-empty sync batch.
