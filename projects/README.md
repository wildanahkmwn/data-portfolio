# Projects

Self-contained portfolio demos. Each folder should include:

- `README.md` with quick start
- runnable code / SQL
- `docs/case_study.md`
- at least one screenshot under `docs/screenshots/`

## Current

- `agronomy-marketplace-analytics/` — marketplace orders to ClickHouse marts to Streamlit
- `postgres-to-clickhouse-stream/` — near-real-time Postgres to ClickHouse sync

## Template

```text
projects/<short-name>/
  README.md
  requirements.txt          # if Python
  docker-compose.yml        # if needed
  docs/
    case_study.md
    screenshots/
  app/ or src/
  sql/                      # optional
```
