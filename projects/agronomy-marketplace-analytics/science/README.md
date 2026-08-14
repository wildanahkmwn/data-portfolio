# Data science notes

Two lightweight models sit on top of trusted ClickHouse marts:

| Script | Question | Output |
|---|---|---|
| `forecast_daily_gmv.py` | How much GMV next 14 days? | `output/gmv_forecast_14d.csv` + MAE/MAPE |
| `reactivation_priority.py` | Which buyers to call first? | `output/reactivation_priority.csv` |

## Why this counts as DS (not just charts)

- Clear prediction / ranking target
- Backtest metric for the forecast
- Actionable output for ops (stock plan, outreach list)
- Built on curated marts, not a dirty CSV notebook

## Upgrade path (if a client wants more)

- Prophet / gradient boosting for forecast
- Proper churn classifier with train/test split
- Experiment design for promo uplift
