"""ClickHouse helpers: schema, Postgres sync, and marts."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import clickhouse_connect

ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = ROOT / "sql"
STREAM_NAME = os.getenv("STREAM_NAME", "marketplace_orders")
STREAM_BATCH_SIZE = int(os.getenv("STREAM_BATCH_SIZE", "2000"))


def get_client():
    return clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        port=int(os.getenv("CLICKHOUSE_PORT", "8123")),
        username=os.getenv("CLICKHOUSE_USER", "default"),
        password=os.getenv("CLICKHOUSE_PASSWORD", "analytics"),
        database=os.getenv("CLICKHOUSE_DATABASE", "default"),
    )


def run_sql_file(client, path: Path) -> None:
    sql = path.read_text(encoding="utf-8")
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    for statement in statements:
        client.command(statement)


def create_schema(client) -> None:
    run_sql_file(client, SQL_DIR / "01_raw_orders.sql")


def reset_sink(client) -> None:
    client.command("TRUNCATE TABLE IF EXISTS ecommerce.raw_orders")
    client.command("TRUNCATE TABLE IF EXISTS ecommerce.stream_watermarks")


def read_watermark(client) -> tuple[datetime, int]:
    rows = client.query(
        """
        SELECT last_updated_at, last_source_id
        FROM ecommerce.stream_watermarks FINAL
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


def write_watermark(
    client, updated_at: datetime, source_id: int, rows_synced: int
) -> None:
    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)
    client.insert(
        "ecommerce.stream_watermarks",
        [[STREAM_NAME, updated_at, source_id, rows_synced]],
        column_names=[
            "stream_name",
            "last_updated_at",
            "last_source_id",
            "rows_synced",
        ],
    )


def insert_raw_orders(client, rows: list[dict]) -> None:
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
    client.insert(
        "ecommerce.raw_orders",
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


def sync_once(pg_conn, client) -> int:
    from scripts.pg_utils import fetch_changed_since

    wm_ts, wm_id = read_watermark(client)
    rows = fetch_changed_since(pg_conn, wm_ts, wm_id, STREAM_BATCH_SIZE)
    if not rows:
        return 0
    insert_raw_orders(client, rows)
    last = rows[-1]
    write_watermark(client, last["updated_at"], int(last["id"]), len(rows))
    return len(rows)


def sync_all(pg_conn, client) -> int:
    total = 0
    while True:
        n = sync_once(pg_conn, client)
        if n == 0:
            return total
        total += n


def build_marts(client) -> None:
    for name in (
        "02_mart_daily_sales.sql",
        "03_mart_customer_ltv.sql",
        "04_mart_top_products.sql",
    ):
        run_sql_file(client, SQL_DIR / name)
