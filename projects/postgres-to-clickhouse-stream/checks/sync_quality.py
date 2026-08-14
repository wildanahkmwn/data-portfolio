"""Sync quality checks for Postgres -> ClickHouse stream."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import clickhouse_connect
import psycopg

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from stream import (
    CH_HOST,
    CH_PASSWORD,
    CH_PORT,
    CH_USER,
    PG_DATABASE,
    PG_HOST,
    PG_PASSWORD,
    PG_PORT,
    PG_USER,
)


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str


def main() -> int:
    with psycopg.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        dbname=PG_DATABASE,
    ) as pg:
        with pg.cursor() as cur:
            cur.execute("SELECT count(*) FROM marketplace_orders")
            pg_count = int(cur.fetchone()[0])
            cur.execute("SELECT coalesce(sum(quantity * unit_price), 0) FROM marketplace_orders")
            pg_gmv = float(cur.fetchone()[0])

    ch = clickhouse_connect.get_client(
        host=CH_HOST,
        port=CH_PORT,
        username=CH_USER,
        password=CH_PASSWORD,
    )
    ch_count = int(ch.command("SELECT count() FROM pg2ch.raw_orders FINAL"))
    ch_gmv = float(
        ch.command("SELECT coalesce(sum(quantity * unit_price), 0) FROM pg2ch.raw_orders FINAL")
    )
    mart_days = int(ch.command("SELECT count() FROM pg2ch.mart_daily_sales"))
    wm_rows = int(
        ch.command("SELECT count() FROM pg2ch.stream_watermarks FINAL")
    )

    checks = [
        CheckResult("postgres_not_empty", pg_count > 0, f"pg_rows={pg_count}"),
        CheckResult("clickhouse_caught_up", ch_count == pg_count, f"pg={pg_count}, ch={ch_count}"),
        CheckResult(
            "gmv_matches",
            abs(pg_gmv - ch_gmv) < 0.01,
            f"pg_gmv={pg_gmv}, ch_gmv={ch_gmv}",
        ),
        CheckResult("watermark_present", wm_rows > 0, f"watermarks={wm_rows}"),
        CheckResult("mart_populated", mart_days > 0, f"mart_days={mart_days}"),
    ]

    failed = 0
    for c in checks:
        status = "PASS" if c.ok else "FAIL"
        print(f"[{status}] {c.name}: {c.detail}")
        if not c.ok:
            failed += 1

    if failed:
        print(f"\n{failed} check(s) failed")
        return 1
    print("\nAll checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
