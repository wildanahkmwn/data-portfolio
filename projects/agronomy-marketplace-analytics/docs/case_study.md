# Case Study: Agronomy Marketplace Analytics Pipeline

Attach this file (or export to PDF) anywhere: Upwork proposal, email, Notion.

## Snapshot

| Field | Detail |
|---|---|
| Role | End-to-end data / analytics engineer |
| Domain | Agronomy marketplace (agricultural inputs) |
| Stack | Postgres, Python, ClickHouse, Metabase (Streamlit optional) |
| Repo | https://github.com/wildanahkmwn/data-portfolio/tree/main/projects/agronomy-marketplace-analytics |
| Visual | `docs/screenshots/dashboard-metrics.png` |

## Problem

Marketplace order data lives in Postgres. Ops still ask for GMV/AOV "hari ini"
but reports are nightly, numbers disagree, and nobody trusts freshness.

## Solution

1. Keep Postgres as system of record
2. Stream changed order lines into ClickHouse by watermark `(updated_at, id)`
3. Build marts (daily sales, customer LTV, top products)
4. Quality gate: Postgres vs ClickHouse row/GMV parity, duplicates, freshness
5. Serve Metabase for business users (Streamlit only as a demo app)

## Architecture

```text
Postgres marketplace_orders
      |
      |  stream worker
      v
ClickHouse raw + marts
      |
 +----+------------+
 |                 |
 v                 v
quality          Metabase
checks           (client BI)
```

## Sample outcome (anonymized demo)

- ~3,000 order lines from a masked extract
- Near-real-time catch-up when new Postgres rows are inserted
- All quality checks passing before the dashboard is used

## What this proves

- Can connect OLTP (Postgres) to OLAP (ClickHouse), not only load a CSV
- Can define GMV / AOV / LTV with a consistent grain
- Can gate bad or stale data before stakeholders see it
- Can put a BI tool in front that non-engineers actually open

## Attachments checklist

1. This case study
2. Dashboard screenshot
3. Repo link above
