# Case Study: Agronomy Marketplace (DE + DA + DS)

Attach this file (or export to PDF) on Upwork, email, or Notion.

## Snapshot

| Field | Detail |
|---|---|
| Role | Data engineer + analyst + applied scientist |
| Domain | Agronomy marketplace (agricultural inputs) |
| Stack | Postgres, Python, ClickHouse, Metabase |
| Repo | https://github.com/wildanahkmwn/data-portfolio/tree/main/projects/agronomy-marketplace-analytics |
| Visual | `docs/screenshots/dashboard-metrics.png` |

## Problem

1. Order data sits in Postgres; reports are late or disagree.
2. Ops still need clear answers: what sells, who comes back, which day peaks.
3. Leadership wants a forward view: next-week GMV and who to reactivate.

## Solution (three layers)

### Data Engineer
- Stream Postgres `marketplace_orders` into ClickHouse by watermark
- Build marts (daily sales, LTV, top products)
- Quality gates including Postgres vs ClickHouse parity

### Data Analyst
- Category GMV mix
- Repeat-buyer rate
- Weekday seasonality
- Cohort LTV at day-30
- Written takeaways in `analysis/insights.md` / `scripts/run_analysis.py`

### Data Scientist
- 14-day GMV forecast with MAE/MAPE backtest
- Buyer reactivation priority list (RFM-style ranking)

## Architecture

```text
Postgres
   -> stream -> ClickHouse marts
                    |
         +----------+-----------+
         |          |           |
      Metabase   Analyst     Forecast /
                 insights    reactivation
```

## What to say in a pitch

- "I do not stop at the pipeline. I turn trusted marts into decisions and a simple forecast ops can use."
- "DE makes the numbers trustworthy. DA explains the business. DS ranks the next action."

## Attachments

1. This case study
2. Dashboard screenshot
3. Optional: terminal output of `run_analysis.py` and `forecast_daily_gmv.py`
4. Repo link above
