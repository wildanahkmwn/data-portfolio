"""Near-real-time Postgres -> ClickHouse stream worker.

Pattern: watermark polling + batched inserts into ReplacingMergeTree.
This keeps the demo local and reliable. Production upgrades:
Debezium/Kafka, PeerDB, or ClickHouse MaterializedPostgreSQL (logical replication).
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from pathlib import Path

import clickhouse_connect
import psycopg
from psycopg.rows import dict_row

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
    STREAM_BATCH_SIZE,
    STREAM_NAME,
    STREAM_POLL_SECONDS,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_SQL = ROOT / "sql" / "01_clickhouse_schema.sql"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("pg2ch.stream")


def get_pg():
    return psycopg.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        dbname=PG_DATABASE,
        row_factory=dict_row,
    )


def get_ch():
    return clickhouse_connect.get_client(
        host=CH_HOST,
        port=CH_PORT,
        username=CH_USER,
        password=CH_PASSWORD,
    )


def ensure_clickhouse_schema(ch) -> None:
    sql = SCHEMA_SQL.read_text(encoding="utf-8")
    for statement in [s.strip() for s in sql.split(";") if s.strip()]:
        ch.command(statement)


def read_watermark(ch) -> tuple[datetime, int]:
    rows = ch.query(
        """
        SELECT last_updated_at, last_source_id
        FROM pg2ch.stream_watermarks FINAL
        WHERE stream_name = {name:String}
        LIMIT 1
        """,
        parameters={"name": STREAM_NAME},
    ).result_rows
    if not rows:
        return datetime(1970, 1, 1, tzinfo=timezone.utc), 0
    ts, source_id = rows[0]
    if getattr(ts, "tzinfo", None) is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts, int(source_id)


def write_watermark(ch, updated_at: datetime, source_id: int, rows_synced: int) -> None:
    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)
    ch.insert(
        "pg2ch.stream_watermarks",
        [[STREAM_NAME, updated_at, source_id, rows_synced]],
        column_names=[
            "stream_name",
            "last_updated_at",
            "last_source_id",
            "rows_synced",
        ],
    )


def fetch_batch(pg, updated_at: datetime, source_id: int) -> list[dict]:
    # Truncate to milliseconds so the watermark matches ClickHouse DateTime64(3).
    with pg.cursor() as cur:
        cur.execute(
            """
            SELECT
                id,
                order_id,
                order_date,
                customer_id,
                customer_name,
                product_id,
                product_name,
                category,
                quantity,
                unit_price,
                currency,
                date_trunc('milliseconds', updated_at) AS updated_at
            FROM marketplace_orders
            WHERE (date_trunc('milliseconds', updated_at), id) > (%s, %s)
            ORDER BY date_trunc('milliseconds', updated_at), id
            LIMIT %s
            """,
            (updated_at, source_id, STREAM_BATCH_SIZE),
        )
        return list(cur.fetchall())


def insert_clickhouse(ch, rows: list[dict]) -> None:
    payload = []
    for r in rows:
        updated_at = r["updated_at"]
        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)
        payload.append(
            [
                int(r["id"]),
                r["order_id"],
                r["order_date"],
                r["customer_id"],
                r["customer_name"],
                r["product_id"],
                r["product_name"],
                r["category"],
                int(r["quantity"]),
                float(r["unit_price"]),
                r["currency"],
                updated_at,
            ]
        )
    ch.insert(
        "pg2ch.raw_orders",
        payload,
        column_names=[
            "source_id",
            "order_id",
            "order_date",
            "customer_id",
            "customer_name",
            "product_id",
            "product_name",
            "category",
            "quantity",
            "unit_price",
            "currency",
            "source_updated_at",
        ],
    )


def sync_once(pg, ch) -> int:
    wm_ts, wm_id = read_watermark(ch)
    rows = fetch_batch(pg, wm_ts, wm_id)
    if not rows:
        return 0
    insert_clickhouse(ch, rows)
    last = rows[-1]
    write_watermark(ch, last["updated_at"], int(last["id"]), len(rows))
    log.info(
        "synced=%s watermark=(%s, %s)",
        len(rows),
        last["updated_at"].isoformat(),
        last["id"],
    )
    return len(rows)


def rebuild_mart(ch) -> None:
    mart_sql = (ROOT / "sql" / "02_mart_daily_sales.sql").read_text(encoding="utf-8")
    for statement in [s.strip() for s in mart_sql.split(";") if s.strip()]:
        ch.command(statement)


def run_forever() -> None:
    log.info(
        "starting stream pg=%s:%s/%s -> ch=%s:%s",
        PG_HOST,
        PG_PORT,
        PG_DATABASE,
        CH_HOST,
        CH_PORT,
    )
    ch = get_ch()
    ensure_clickhouse_schema(ch)
    while True:
        try:
            with get_pg() as pg:
                synced = sync_once(pg, ch)
                if synced:
                    rebuild_mart(ch)
        except Exception:
            log.exception("sync loop error; retrying")
        time.sleep(STREAM_POLL_SECONDS)


if __name__ == "__main__":
    run_forever()
