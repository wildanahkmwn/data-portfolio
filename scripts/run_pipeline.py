"""Run full local pipeline: schema -> load -> marts."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.ch_utils import build_marts, create_schema, get_client, load_orders_from_csv


def main() -> None:
    client = get_client()
    print("Creating schema...")
    create_schema(client)

    print("Loading sample orders...")
    n = load_orders_from_csv(client)
    print(f"Loaded {n} rows into ecommerce.raw_orders")

    print("Building marts...")
    build_marts(client)
    print("Done. Next: python checks/data_quality.py && streamlit run app/dashboard.py")


if __name__ == "__main__":
    main()
