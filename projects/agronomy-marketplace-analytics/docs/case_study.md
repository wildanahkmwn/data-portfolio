# Case Study: Agronomy Marketplace Analytics Pipeline

Attach this file (or export to PDF) anywhere: Upwork proposal, LinkedIn Featured,
email, Notion, company intake form.

## Snapshot

| Field | Detail |
|---|---|
| Role | End-to-end data / analytics engineer |
| Domain | Agronomy marketplace (agricultural inputs) |
| Stack | Python, SQL, ClickHouse, Streamlit, Airflow (optional) |
| Repo | https://github.com/wildanahkmwn/data-portfolio/tree/main/projects/agronomy-marketplace-analytics |
| Visual | `docs/screenshots/dashboard-metrics.png` |

## Problem

Marketplace teams often have order data but still struggle with:

- GMV / AOV numbers that disagree across reports
- No clear freshness check (is this data from today or last week?)
- Duplicate or incomplete order lines slipping into dashboards
- Business users cannot self-serve a trusted view

## Solution

Built a compact production-style path:

1. Load anonymized order lines into ClickHouse (`raw_orders`)
2. Transform into business marts (daily sales, customer LTV, top products)
3. Run quality gates before serving (nulls, duplicates, GMV consistency, freshness)
4. Serve a Streamlit dashboard for non-technical consumption

## Architecture

```text
masked order CSV
      |
      v
Python ingest (CLI or Airflow)
      |
      v
ClickHouse raw + marts
      |
 +----+----+
 |         |
 v         v
quality   Streamlit
checks    dashboard
```

## Sample outcome (from anonymized demo data)

- ~3,000 order lines / ~2,800 orders
- Marts for GMV, AOV, top products, customer LTV
- All quality checks passing before dashboard serve

## What this proves

- Can design a clear data flow, not only ad-hoc SQL
- Can define business metrics with consistent grain
- Can gate bad data before it reaches stakeholders
- Can deliver an interface a non-engineer can use

## Attachments checklist

When sending to a client / Upwork / recruiter, attach:

1. This case study (PDF or Markdown)
2. Dashboard screenshot (`docs/screenshots/dashboard-metrics.png`)
3. Repo link above

Optional: 45-60s screen recording of pipeline run + dashboard.
