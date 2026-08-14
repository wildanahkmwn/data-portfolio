"""Forecast next 14 days of GMV from mart_daily_sales (simple DS demo).

Method:
1. Weekday baseline = mean GMV by day-of-week over recent history
2. Level adjustment = last-7-day average / overall recent average
3. Backtest on a held-out 14-day window (MAE + MAPE)

Easy to explain on a client call; no heavy ML framework.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.ch_utils import get_client

HORIZON = 14
HISTORY_DAYS = 60
OUT_DIR = ROOT / "science" / "output"


def load_daily(client) -> pd.DataFrame:
    df = client.query_df(
        """
        SELECT order_date, gmv, orders
        FROM ecommerce.mart_daily_sales
        ORDER BY order_date
        """
    )
    if df.empty:
        raise SystemExit("mart_daily_sales is empty. Run scripts/run_pipeline.py first.")
    df["order_date"] = pd.to_datetime(df["order_date"])
    df = df.set_index("order_date").asfreq("D", fill_value=0.0)
    df["gmv"] = df["gmv"].astype(float)
    return df


def fit_forecast(history: pd.DataFrame, horizon: int) -> pd.DataFrame:
    weekday_mean = history.groupby(history.index.dayofweek)["gmv"].mean()
    overall = float(history["gmv"].mean()) or 1.0
    recent_level = float(history["gmv"].tail(7).mean())
    level = recent_level / overall

    future_idx = pd.date_range(
        history.index.max() + pd.Timedelta(days=1), periods=horizon, freq="D"
    )
    baseline = np.array(
        [float(weekday_mean.get(d.dayofweek, overall)) for d in future_idx]
    )
    pred = np.maximum(baseline * level, 0.0)

    return pd.DataFrame(
        {
            "order_date": future_idx.date,
            "forecast_gmv": np.round(pred, 0),
            "weekday_baseline_gmv": np.round(baseline, 0),
            "level_factor": round(level, 3),
        }
    )


def backtest(df: pd.DataFrame) -> dict:
    if len(df) <= HORIZON + 14:
        return {"mae": None, "mape": None, "note": "not enough history"}
    train = df.iloc[:-HORIZON]
    actual = df.iloc[-HORIZON:]["gmv"].values.astype(float)
    pred = fit_forecast(train, HORIZON)["forecast_gmv"].values.astype(float)
    mae = float(np.mean(np.abs(actual - pred)))
    mask = actual > 0
    if mask.any():
        mape = float(np.mean(np.abs(actual[mask] - pred[mask]) / actual[mask]) * 100.0)
        mape_note = f"on {int(mask.sum())}/{len(actual)} non-zero days"
    else:
        mape = None
        mape_note = "no non-zero days in holdout"
    return {
        "mae": round(mae, 0),
        "mape": round(mape, 1) if mape is not None else None,
        "note": mape_note,
    }


def main() -> None:
    client = get_client()
    daily = load_daily(client)
    recent = daily.tail(HISTORY_DAYS)
    metrics = backtest(recent)
    forecast = fit_forecast(recent, HORIZON)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "gmv_forecast_14d.csv"
    forecast.to_csv(out_path, index=False)

    print("=== DATA SCIENCE: GMV demand forecast ===\n")
    print(f"history_days={len(recent)} horizon={HORIZON}")
    print(
        f"backtest_mae={metrics['mae']} "
        f"backtest_mape_pct={metrics['mape']} ({metrics['note']})"
    )
    print("\nNext 14 days forecast:")
    print(forecast.to_string(index=False))
    print(f"\nSaved: {out_path}")
    print(
        "\nBusiness use: share forecast with ops for stock / promo planning; "
        "retrain weekly as new marts land."
    )


if __name__ == "__main__":
    main()
