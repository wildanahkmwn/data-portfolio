"""Insert fresh Postgres rows so the stream worker catches up live."""

from __future__ import annotations

import random
import sys
from datetime import date
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from stream import PG_DATABASE, PG_HOST, PG_PASSWORD, PG_PORT, PG_USER

PRODUCTS = [
    ("P-FERT-01", "NPK 16-16-16 50kg", "Pupuk", 185000),
    ("P-HERB-01", "Glyphosate 1L", "Racun", 72000),
    ("P-SEED-01", "Benih Sawit Topaz 100 butir", "Benih", 950000),
    ("P-TOOL-01", "Palm Sickle Pro", "Tools", 95000),
]
CUSTOMERS = [
    ("C-2001", "Mitra Tani 2001"),
    ("C-2002", "Koperasi Hijau 2002"),
    ("C-2003", "UD Agro 2003"),
]


def main(n: int = 5) -> None:
    with psycopg.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        dbname=PG_DATABASE,
    ) as conn:
        with conn.cursor() as cur:
            for i in range(n):
                order_id = f"ORD-LIVE-{date.today().strftime('%Y%m%d')}-{random.randint(1000, 9999)}-{i}"
                customer_id, customer_name = random.choice(CUSTOMERS)
                product_id, product_name, category, unit_price = random.choice(PRODUCTS)
                qty = random.randint(1, 12)
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
                        qty,
                        unit_price,
                    ),
                )
        conn.commit()
    print(f"Inserted {n} new Postgres rows. Stream worker should sync within a few seconds.")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 5)
