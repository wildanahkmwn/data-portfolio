# Case Study: Postgres to ClickHouse Stream

Attach with the agronomy analytics case study when pitching pipeline work.

## Snapshot

| Field | Detail |
|---|---|
| Role | Data / analytics engineer |
| Domain | Agronomy marketplace order sync |
| Stack | Postgres, Python, ClickHouse |
| Repo path | `projects/postgres-to-clickhouse-stream/` |
| Pattern | Watermark stream + batched inserts |

## Problem

Order data often lives in Postgres (app DB), while analytics needs ClickHouse.
A nightly dump is too slow when ops ask "apa angka hari ini?".

## Solution

1. Keep Postgres as system of record
2. Run a stream worker that polls new/changed rows by `(updated_at, id)`
3. Batch-insert into ClickHouse `ReplacingMergeTree`
4. Rebuild a daily sales mart and verify parity (rows + GMV)

## Outcome

- Near-real-time sync (seconds, not hours)
- Idempotent sink via ReplacingMergeTree + source id
- Explicit watermark table for operability
- Clear upgrade path to logical CDC when volume grows

## Architecture choice

| Choice | Why |
|---|---|
| Batched direct inserts | Healthy for moderate throughput; avoids tiny insert storms |
| Watermark poll (not full dump) | Incremental, restart-safe |
| ReplacingMergeTree | Handles late updates from source without heavy mutations |
| Logical WAL enabled | Ready for Debezium/Kafka later |

## Attachments

1. This case study
2. Repo folder link
3. Optional: terminal output of `scripts/status.py` before/after `seed_more.py`
