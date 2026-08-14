"""Shared ClickHouse helpers for local pipeline and Airflow DAG."""

from __future__ import annotations

import os
from pathlib import Path

import clickhouse_connect
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = ROOT / "sql"
SAMPLE_CSV = ROOT / "sample_data" / "orders.csv"


def get_client():
    return clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        port=int(os.getenv("CLICKHOUSE_PORT", "8123")),
        username=os.getenv("CLICKHOUSE_USER", "default"),
        password=os.getenv("CLICKHOUSE_PASSWORD", ""),
        database=os.getenv("CLICKHOUSE_DATABASE", "default"),
    )


def run_sql_file(client, path: Path) -> None:
    sql = path.read_text(encoding="utf-8")
    # Allow multiple statements separated by semicolons.
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    for statement in statements:
        client.command(statement)


def create_schema(client) -> None:
    run_sql_file(client, SQL_DIR / "01_raw_orders.sql")


def load_orders_from_csv(client, csv_path: Path = SAMPLE_CSV) -> int:
    df = pd.read_csv(csv_path, parse_dates=["order_date"])
    df["order_date"] = pd.to_datetime(df["order_date"]).dt.date
    required = [
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
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"CSV missing columns: {missing}")

    # Idempotent reload for demo: wipe raw then insert.
    client.command("TRUNCATE TABLE IF EXISTS ecommerce.raw_orders")
    client.insert_df("ecommerce.raw_orders", df[required])
    return len(df)


def build_marts(client) -> None:
    for name in (
        "02_mart_daily_sales.sql",
        "03_mart_customer_ltv.sql",
        "04_mart_top_products.sql",
    ):
        run_sql_file(client, SQL_DIR / name)
