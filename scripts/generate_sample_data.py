"""Generate a realistic sample orders.csv for demos."""

from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "sample_data" / "orders.csv"

PRODUCTS = [
    ("P001", "Fertilizer NPK 16-16-16", "Agro Input", 185000),
    ("P002", "Herbicide Glyphosate 1L", "Agro Input", 72000),
    ("P003", "Palm Sickle Pro", "Tools", 95000),
    ("P004", "Safety Boots Size 42", "PPE", 210000),
    ("P005", "Motor Grease 500g", "Maintenance", 45000),
    ("P006", "Seedling Tray 50 cell", "Nursery", 28000),
    ("P007", "Chain Saw Chain 20in", "Tools", 155000),
    ("P008", "Raincoat Heavy Duty", "PPE", 125000),
]

CUSTOMERS = [
    ("C001", "Mitra Sawit Jaya"),
    ("C002", "Koperasi Maju Bersama"),
    ("C003", "CV Hijau Lestari"),
    ("C004", "UD Tani Makmur"),
    ("C005", "PT Agro Nusantara"),
    ("C006", "Gapoktan Sejahtera"),
    ("C007", "Toko Tani Barokah"),
    ("C008", "UD Sumber Rejeki"),
]


def main(n_orders: int = 180, seed: int = 42) -> None:
    random.seed(seed)
    start = date.today() - timedelta(days=60)
    rows = []
    order_num = 1000

    for _ in range(n_orders):
        order_num += 1
        order_date = start + timedelta(days=random.randint(0, 59))
        customer_id, customer_name = random.choice(CUSTOMERS)
        # 1-3 distinct products per order (no duplicate order_id + product_id)
        n_lines = random.randint(1, 3)
        for product_id, product_name, category, unit_price in random.sample(
            PRODUCTS, n_lines
        ):
            qty = random.randint(1, 8)
            rows.append(
                {
                    "order_id": f"ORD-{order_num}",
                    "order_date": order_date.isoformat(),
                    "customer_id": customer_id,
                    "customer_name": customer_name,
                    "product_id": product_id,
                    "product_name": product_name,
                    "category": category,
                    "quantity": qty,
                    "unit_price": unit_price,
                    "currency": "IDR",
                }
            )

    df = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"Wrote {len(df)} rows to {OUT}")


if __name__ == "__main__":
    main()
