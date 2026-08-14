# Data Portfolio

Monorepo of end-to-end data / analytics portfolio projects.

Each project under `projects/` is self-contained (runnable demo + case study).
Shared hire-me docs live in `docs/` so they can be attached on Upwork, email, or proposals.

## Projects

| Project | Domain | Stack | Status |
|---|---|---|---|
| [agronomy-marketplace-analytics](projects/agronomy-marketplace-analytics/) | Agronomy marketplace orders | Python, ClickHouse, Streamlit, Airflow (optional) | Ready |
| [postgres-to-clickhouse-stream](projects/postgres-to-clickhouse-stream/) | Postgres -> ClickHouse near-real-time sync | Postgres, Python, ClickHouse | Ready |

## Shared attachments

| File | Use |
|---|---|
| [docs/freelance_profile.md](docs/freelance_profile.md) | Upwork title, overview, proposal template |
| [docs/services_one_pager.md](docs/services_one_pager.md) | Service packages |
| Project `docs/case_study.md` | Per-project case study |
| Project `docs/screenshots/` | Visual proof |

## How to run a project

```bash
cd projects/<project-name>
docker compose up -d
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/run_pipeline.py
python checks/data_quality.py
streamlit run app/dashboard.py
```

## Add a new portfolio project

1. Copy `projects/_template/` (or clone structure from an existing project)
2. Put code under `projects/<short-name>/`
3. Add a case study + screenshot in that project's `docs/`
4. Register it in the table above

## License

MIT
