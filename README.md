# Data Portfolio

Monorepo of end-to-end data / analytics portfolio projects.

Each project under `projects/` is self-contained (runnable demo + case study).
Shared hire-me docs live in `docs/` so they can be attached on Upwork, email, or proposals.

## Projects

| Project | Domain | Stack | Status |
|---|---|---|---|
| [agronomy-marketplace-analytics](projects/agronomy-marketplace-analytics/) | Agronomy marketplace: Postgres to ClickHouse to Metabase | Postgres, Python, ClickHouse, Metabase | Ready |

## Shared attachments

| File | Use |
|---|---|
| [docs/freelance_profile.md](docs/freelance_profile.md) | Upwork title, overview, proposal template |
| [docs/services_one_pager.md](docs/services_one_pager.md) | Service packages |
| Project `docs/case_study.md` | Per-project case study |
| Project `docs/screenshots/` | Visual proof |

## How to run

```bash
cd projects/agronomy-marketplace-analytics
docker compose up -d --build
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/run_pipeline.py
python checks/data_quality.py
```

Metabase: http://localhost:3000

## Add a new portfolio project

1. Copy `projects/_template/`
2. Put code under `projects/<short-name>/`
3. Add a case study + screenshot
4. Register it in the table above

## License

MIT
