"""Score buyers for reactivation priority (simple RFM-style ranking).

Outputs a ranked table: days since last order, order count, GMV, priority band.
This is the DS "action list" ops can use after the DE pipeline is trusted.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.ch_utils import get_client

OUT_DIR = ROOT / "science" / "output"


def score_band(days_since: int, orders: int) -> str:
    if days_since <= 14:
        return "active"
    if days_since <= 45 and orders >= 2:
        return "warm_reactivate"
    if days_since <= 90:
        return "cool_reactivate"
    return "lapse_risk"


def main() -> None:
    client = get_client()
    df = client.query_df(
        """
        SELECT
            customer_id,
            any(customer_name) AS customer_name,
            min(order_date) AS first_order_date,
            max(order_date) AS last_order_date,
            uniqExact(order_id) AS orders,
            sum(quantity * unit_price) AS gmv,
            dateDiff('day', max(order_date), today()) AS days_since_last_order
        FROM ecommerce.raw_orders FINAL
        GROUP BY customer_id
        ORDER BY gmv DESC
        """
    )
    if df.empty:
        raise SystemExit("No customers found. Run scripts/run_pipeline.py first.")

    df["priority"] = [
        score_band(int(d), int(o))
        for d, o in zip(df["days_since_last_order"], df["orders"])
    ]
    # Higher GMV + longer silence = higher outreach value among non-active
    df["outreach_score"] = (
        df["gmv"].astype(float)
        * (df["days_since_last_order"].clip(lower=1).astype(float) / 30.0)
        * df["orders"].astype(float)
    )
    ranked = df.sort_values("outreach_score", ascending=False)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "reactivation_priority.csv"
    ranked.to_csv(out_path, index=False)

    summary = (
        ranked.groupby("priority")
        .agg(buyers=("customer_id", "count"), gmv=("gmv", "sum"))
        .reset_index()
        .sort_values("gmv", ascending=False)
    )

    print("=== DATA SCIENCE: reactivation priority ===\n")
    print(summary.to_string(index=False))
    print("\nTop 10 outreach candidates:")
    cols = [
        "customer_name",
        "orders",
        "gmv",
        "days_since_last_order",
        "priority",
    ]
    print(ranked[cols].head(10).to_string(index=False))
    print(f"\nSaved: {out_path}")
    print(
        "\nBusiness use: give warm/cool lists to sales or CRM; "
        "do not blast active buyers."
    )


if __name__ == "__main__":
    main()
