"""Run analyst SQL packs and print business-facing takeaways."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.ch_utils import get_client

ANALYSIS_DIR = ROOT / "analysis"


def _run_sql(client, path: Path):
    sql = path.read_text(encoding="utf-8").strip().rstrip(";")
    return client.query_df(sql)


def main() -> None:
    client = get_client()
    print("=== DATA ANALYST PACK ===\n")

    mix = _run_sql(client, ANALYSIS_DIR / "01_category_mix.sql")
    print("1) Category mix (last 60 days)")
    print(mix.to_string(index=False))
    if len(mix):
        top = mix.iloc[0]
        print(
            f"\nTakeaway: {top['category']} leads with "
            f"{top['gmv_share_pct']}% of GMV. Prioritize stock and margin there.\n"
        )

    repeat = _run_sql(client, ANALYSIS_DIR / "02_repeat_buyers.sql")
    print("2) Repeat buyers")
    print(repeat.to_string(index=False))
    if len(repeat):
        r = repeat.iloc[0]
        print(
            f"\nTakeaway: repeat rate {r['repeat_rate_pct']}%. "
            "If low, reactivation usually beats pure acquisition spend.\n"
        )

    weekday = _run_sql(client, ANALYSIS_DIR / "03_weekday_seasonality.sql")
    print("3) Weekday seasonality")
    print(weekday.to_string(index=False))
    if len(weekday):
        peak = weekday.loc[weekday["gmv"].idxmax()]
        print(
            f"\nTakeaway: peak GMV on {peak['weekday']}. "
            "Align promo and warehouse staffing to that day.\n"
        )

    cohort = _run_sql(client, ANALYSIS_DIR / "04_cohort_ltv_d30.sql")
    print("4) Cohort LTV (day-30)")
    print(cohort.to_string(index=False))
    if len(cohort) >= 2:
        first = cohort.iloc[0]
        last = cohort.iloc[-1]
        print(
            f"\nTakeaway: avg LTV D30 moved from {first['avg_ltv_d30']} "
            f"({first['cohort_month']}) to {last['avg_ltv_d30']} "
            f"({last['cohort_month']}). Review onboarding if it dropped.\n"
        )

    print("Write-up template: analysis/insights.md")


if __name__ == "__main__":
    main()
