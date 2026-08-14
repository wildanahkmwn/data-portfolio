# Analyst insights (from ClickHouse marts)

Run:

```bash
python scripts/run_analysis.py
```

These questions are what you answer as a **data analyst** after the pipeline is trusted.

## Business questions

1. Which product categories drive GMV in the last 60 days?
2. What share of buyers are one-time vs repeat?
3. Is GMV weekday-skewed (ops / promo timing)?
4. How does 30-day LTV differ by acquisition cohort?

## How to present this

In Metabase or a proposal, lead with decisions, not tables:

- "Category X is Y% of GMV: protect stock and margin there first."
- "Repeat rate is Z%: reactivation campaigns beat pure acquisition if Z is low."
- "Weekday pattern: put promo budget on peak days, staff warehouse accordingly."
- "Newer cohorts spend less/more by day-30: review onboarding or first-order discount."

Exact numbers change with the sample extract; re-run `run_analysis.py` after each reload.
