"""Seed Postgres, sync to ClickHouse, then rebuild marts."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.ch_utils import (
    build_marts,
    create_schema,
    get_client,
    reset_sink,
    sync_all,
)
from scripts.pg_utils import (
    count_orders,
    create_source_schema,
    get_connection,
    load_orders_from_csv,
)


def main() -> None:
    print("Preparing Postgres source...")
    with get_connection() as pg:
        create_source_schema(pg)
        n = load_orders_from_csv(pg)
        print(f"Loaded {n} rows into marketplace_orders ({count_orders(pg)} total)")

        print("Creating ClickHouse schema...")
        ch = get_client()
        create_schema(ch)
        reset_sink(ch)

        print("Streaming Postgres -> ClickHouse...")
        synced = sync_all(pg, ch)
        print(f"Synced {synced} rows into ecommerce.raw_orders")

    print("Building marts...")
    build_marts(ch)
    print(
        "Done. Next: python checks/data_quality.py && "
        "open Metabase at http://localhost:3000 (or streamlit run app/dashboard.py)"
    )


if __name__ == "__main__":
    main()
