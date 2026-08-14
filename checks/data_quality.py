"""Data quality checks for ecommerce ClickHouse marts.

Exit code 0 = all checks passed.
Exit code 1 = one or more checks failed.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.ch_utils import get_client


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str


def _scalar(client, sql: str):
    rows = client.query(sql).result_rows
    return rows[0][0] if rows else None


def check_raw_not_empty(client) -> CheckResult:
    n = _scalar(client, "SELECT count() FROM ecommerce.raw_orders")
    return CheckResult("raw_orders_not_empty", bool(n and n > 0), f"rows={n}")


def check_no_null_order_id(client) -> CheckResult:
    n = _scalar(
        client,
        "SELECT count() FROM ecommerce.raw_orders WHERE order_id IS NULL OR order_id = ''",
    )
    return CheckResult("no_null_or_blank_order_id", n == 0, f"bad_rows={n}")


def check_no_duplicate_line_keys(client) -> CheckResult:
    # Same order_id + product_id should not appear twice in demo load.
    n = _scalar(
        client,
        """
        SELECT count()
        FROM (
            SELECT order_id, product_id, count() AS c
            FROM ecommerce.raw_orders
            GROUP BY order_id, product_id
            HAVING c > 1
        )
        """,
    )
    return CheckResult("no_duplicate_order_product", n == 0, f"dup_groups={n}")


def check_mart_row_counts(client) -> CheckResult:
    daily = _scalar(client, "SELECT count() FROM ecommerce.mart_daily_sales")
    cust = _scalar(client, "SELECT count() FROM ecommerce.mart_customer_ltv")
    prod = _scalar(client, "SELECT count() FROM ecommerce.mart_top_products")
    ok = bool(daily and cust and prod)
    return CheckResult(
        "marts_populated",
        ok,
        f"daily={daily}, customers={cust}, products={prod}",
    )


def check_gmv_consistency(client) -> CheckResult:
    raw_gmv = _scalar(
        client, "SELECT sum(quantity * unit_price) FROM ecommerce.raw_orders"
    )
    mart_gmv = _scalar(client, "SELECT sum(gmv) FROM ecommerce.mart_daily_sales")
    ok = (
        raw_gmv is not None
        and mart_gmv is not None
        and abs(float(raw_gmv) - float(mart_gmv)) < 0.01
    )
    return CheckResult(
        "gmv_raw_equals_mart_daily",
        ok,
        f"raw_gmv={raw_gmv}, mart_gmv={mart_gmv}",
    )


def check_freshness(client, max_age_days: int = 7) -> CheckResult:
    age = _scalar(
        client,
        """
        SELECT dateDiff('day', max(order_date), today())
        FROM ecommerce.raw_orders
        """,
    )
    ok = age is not None and age <= max_age_days
    return CheckResult(
        "order_date_freshness",
        ok,
        f"days_since_latest_order={age}, max_allowed={max_age_days}",
    )


def main() -> int:
    client = get_client()
    checks = [
        check_raw_not_empty,
        check_no_null_order_id,
        check_no_duplicate_line_keys,
        check_mart_row_counts,
        check_gmv_consistency,
        check_freshness,
    ]

    results = [fn(client) for fn in checks]
    failed = 0
    for r in results:
        status = "PASS" if r.ok else "FAIL"
        print(f"[{status}] {r.name}: {r.detail}")
        if not r.ok:
            failed += 1

    if failed:
        print(f"\n{failed} check(s) failed")
        return 1

    print("\nAll checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
