"""Print Postgres vs ClickHouse sync status."""

from __future__ import annotations

import sys
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
    STREAM_NAME,
)


def main() -> None:
    with psycopg.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        dbname=PG_DATABASE,
    ) as pg:
        with pg.cursor() as cur:
            cur.execute("SELECT count(*), max(updated_at) FROM marketplace_orders")
            pg_count, pg_max = cur.fetchone()

    ch = clickhouse_connect.get_client(
        host=CH_HOST,
        port=CH_PORT,
        username=CH_USER,
        password=CH_PASSWORD,
    )
    ch_count = ch.command("SELECT count() FROM pg2ch.raw_orders FINAL")
    wm = ch.query(
        f"""
        SELECT last_updated_at, last_source_id, rows_synced
        FROM pg2ch.stream_watermarks FINAL
        WHERE stream_name = '{STREAM_NAME}'
        LIMIT 1
        """
    ).result_rows
    mart = ch.command("SELECT count() FROM pg2ch.mart_daily_sales")

    print(f"postgres_rows={pg_count} postgres_max_updated_at={pg_max}")
    print(f"clickhouse_rows={ch_count} mart_days={mart}")
    if wm:
        print(f"watermark_updated_at={wm[0][0]} watermark_id={wm[0][1]} last_batch={wm[0][2]}")
    else:
        print("watermark=none")
    lag = int(pg_count) - int(ch_count)
    print(f"row_lag={lag}")


if __name__ == "__main__":
    main()
