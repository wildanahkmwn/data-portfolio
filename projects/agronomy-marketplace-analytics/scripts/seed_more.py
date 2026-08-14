"""Insert new Postgres orders so the stream worker (or next pipeline run) picks them up."""

from __future__ import annotations

import random
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.pg_utils import get_connection

PRODUCTS = [
    ("P-FERT-01", "NPK 16-16-16 50kg", "Pupuk", 185000),
    ("P-HERB-01", "Glyphosate 1L", "Racun", 72000),
    ("P-SEED-01", "Benih Topaz 100 butir", "Benih", 950000),
    ("P-TOOL-01", "Palm Sickle Pro", "Tools", 95000),
]
CUSTOMERS = [
    ("C-LIVE-01", "Mitra Tani 2101"),
    ("C-LIVE-02", "Koperasi Hijau 2102"),
    ("C-LIVE-03", "UD Agro 2103"),
]


def main(n: int = 5) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            for i in range(n):
                stamp = date.today().strftime("%Y%m%d")
                order_id = f"ORD-LIVE-{stamp}-{random.randint(1000, 9999)}-{i}"
                customer_id, customer_name = random.choice(CUSTOMERS)
                product_id, product_name, category, unit_price = random.choice(
                    PRODUCTS
                )
                cur.execute(
                    """
                    INSERT INTO marketplace_orders (
                        order_id, order_date, customer_id, customer_name,
                        product_id, product_name, category, quantity, unit_price, currency
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'IDR')
                    """,
                    (
                        order_id,
                        date.today(),
                        customer_id,
                        customer_name,
                        product_id,
                        product_name,
                        category,
                        random.randint(1, 12),
                        unit_price,
                    ),
                )
        conn.commit()
    print(f"Inserted {n} new Postgres rows.")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 5)
