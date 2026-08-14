"""Postgres helpers: source schema, seeding, and watermark reads."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_CSV = ROOT / "sample_data" / "orders.csv"
PG_SCHEMA_SQL = ROOT / "postgres" / "init" / "01_schema.sql"

SOURCE_COLUMNS = [
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
]


def get_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5434")),
        user=os.getenv("POSTGRES_USER", "agro"),
        password=os.getenv("POSTGRES_PASSWORD", "agro"),
        dbname=os.getenv("POSTGRES_DATABASE", "marketplace"),
        row_factory=dict_row,
    )


def create_source_schema(conn) -> None:
    sql = PG_SCHEMA_SQL.read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()


def count_orders(conn) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM marketplace_orders")
        return int(cur.fetchone()["n"])


def load_orders_from_csv(conn, csv_path: Path = SAMPLE_CSV) -> int:
    """Seed the source database from the anonymized sample extract."""
    df = pd.read_csv(csv_path)
    missing = [c for c in SOURCE_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"CSV missing columns: {missing}")
    df["order_date"] = pd.to_datetime(df["order_date"]).dt.date

    rows = [tuple(r) for r in df[SOURCE_COLUMNS].itertuples(index=False, name=None)]
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE marketplace_orders RESTART IDENTITY")
        with cur.copy(
            "COPY marketplace_orders (" + ", ".join(SOURCE_COLUMNS) + ") FROM STDIN"
        ) as copy:
            for row in rows:
                copy.write_row(row)
    conn.commit()
    return len(rows)


def fetch_changed_since(
    conn,
    updated_at: datetime,
    source_id: int,
    batch_size: int = 2000,
) -> list[dict]:
    """Read the next batch of new or updated source rows.

    Timestamps are truncated to milliseconds so the watermark round-trips
    through ClickHouse DateTime64(3) without re-reading the same row.
    """
    with conn.cursor() as cur:
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
            (updated_at, source_id, batch_size),
        )
        return list(cur.fetchall())


def source_totals(conn) -> tuple[int, float]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                count(*) AS rows,
                coalesce(sum(quantity * unit_price), 0) AS gmv
            FROM marketplace_orders
            """
        )
        row = cur.fetchone()
        return int(row["rows"]), float(row["gmv"])
