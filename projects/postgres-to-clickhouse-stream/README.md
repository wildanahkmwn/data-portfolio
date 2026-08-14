# Postgres -> ClickHouse Stream

Near-real-time sync demo: **Postgres marketplace orders -> ClickHouse raw + mart**.

Part of the [data portfolio monorepo](../../README.md).

## What this shows

- Source system: Postgres (`marketplace_orders`)
- Stream worker: watermark polling `(updated_at, id)` + batched inserts
- Sink: ClickHouse `ReplacingMergeTree` + daily sales mart
- Quality checks: row count parity, GMV parity, watermark present

This is the practical local pattern for low/medium volume streaming. Production
upgrades (documented below): logical CDC via Debezium/Kafka, PeerDB, or
ClickHouse `MaterializedPostgreSQL`.

## Architecture

```text
Postgres (marketplace_orders)
        |
        |  poll every 2s by watermark
        v
  Python stream worker
        |
        |  batched inserts
        v
ClickHouse pg2ch.raw_orders
        |
        v
  mart_daily_sales + quality checks
```

## Quick start

```bash
cd projects/postgres-to-clickhouse-stream
docker compose up -d --build
```

Services:

| Service | Port | Purpose |
|---|---|---|
| Postgres | `localhost:5433` | Source |
| ClickHouse | `localhost:8124` | Sink (user `default` / pass `stream`) |
| stream | (internal) | Continuous sync worker |

Wait ~10s, then:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# from host, talking to published ports
python scripts/status.py
python checks/sync_quality.py
```

### Prove it is streaming

```bash
python scripts/seed_more.py 5
sleep 5
python scripts/status.py
python checks/sync_quality.py
```

You should see Postgres and ClickHouse row counts match again within a few seconds.

## Local worker without the stream container

```bash
docker compose up -d postgres clickhouse
export PG_PORT=5433 CH_PORT=8124
python -m stream.worker
```

## Production upgrade path

| Stage | Pattern | When |
|---|---|---|
| This demo | Watermark poll + batched CH inserts | MVP / low-medium volume |
| Next | Debezium -> Kafka -> ClickHouse Kafka engine | Multi-service CDC, replay |
| Alt | PeerDB / MaterializedPostgreSQL | Managed or CH-native logical replication |

`wal_level=logical` is already enabled in Postgres so CDC can be added later
without redesigning the source.

## Layout

```text
postgres-to-clickhouse-stream/
  docker-compose.yml
  Dockerfile
  requirements.txt
  postgres/init/
  sql/
  stream/worker.py
  scripts/status.py
  scripts/seed_more.py
  checks/sync_quality.py
  docs/case_study.md
```

## Case study

See [docs/case_study.md](docs/case_study.md).
