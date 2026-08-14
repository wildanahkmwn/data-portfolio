"""Build anonymized sample_data/orders.csv for the public portfolio.

Reads from SOURCE_CLICKHOUSE_* (never committed). Output contains no PII:
no real names, phones, emails, addresses, or source system identifiers.

Required env:
  SOURCE_CLICKHOUSE_HOST
  SOURCE_CLICKHOUSE_PORT (default 8123)
  SOURCE_CLICKHOUSE_USER
  SOURCE_CLICKHOUSE_PASSWORD
  SOURCE_ORDERS_SQL  -- SELECT that returns columns listed in fetch_raw()
"""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

import clickhouse_connect
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "sample_data" / "orders.csv"

BUYER_PREFIXES = (
    "Mitra Tani",
    "Koperasi Hijau",
    "UD Agro",
    "CV Kebun",
    "Toko Pupuk",
    "Gapoktan",
    "Distributor Bibit",
    "Usaha Kebun",
)

# Optional extra scrub tokens via env, comma-separated (never hardcode employer names).
BRAND_SCRUB = re.compile(
    r"(?i)\b("
    + "|".join(
        re.escape(t.strip())
        for t in os.environ.get("SOURCE_SCRUB_TOKENS", "").split(",")
        if t.strip()
    )
    + r")\b"
) if os.environ.get("SOURCE_SCRUB_TOKENS", "").strip() else None


def _stable_hash(value: str, n: int = 8) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:n].upper()


def _buyer_label(customer_key: str) -> str:
    digest = int(hashlib.sha256(customer_key.encode("utf-8")).hexdigest()[:8], 16)
    prefix = BUYER_PREFIXES[digest % len(BUYER_PREFIXES)]
    return f"{prefix} {digest % 9000 + 1000}"


def _scrub_product_name(name: str) -> str:
    cleaned = name or ""
    if BRAND_SCRUB is not None:
        cleaned = BRAND_SCRUB.sub("", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    return cleaned or "Agro Product"


def _category(row) -> str:
    for col in ("product_category", "product_type"):
        val = row.get(col)
        if val is not None and str(val).strip():
            return str(val).strip()
    return "General"


def get_source_client():
    host = os.environ.get("SOURCE_CLICKHOUSE_HOST")
    if not host:
        raise SystemExit(
            "Set SOURCE_CLICKHOUSE_HOST / USER / PASSWORD and SOURCE_ORDERS_SQL."
        )
    return clickhouse_connect.get_client(
        host=host,
        port=int(os.environ.get("SOURCE_CLICKHOUSE_PORT", "8123")),
        username=os.environ.get("SOURCE_CLICKHOUSE_USER", "default"),
        password=os.environ.get("SOURCE_CLICKHOUSE_PASSWORD", ""),
        database=os.environ.get("SOURCE_CLICKHOUSE_DATABASE", "default"),
    )


def fetch_raw(client) -> pd.DataFrame:
    sql = os.environ.get("SOURCE_ORDERS_SQL", "").strip()
    if not sql:
        raise SystemExit(
            "SOURCE_ORDERS_SQL is required. It must return: "
            "order_no, order_date, customer_key, product_name_raw, "
            "product_category, product_type, quantity, unit_price"
        )
    return client.query_df(sql)


def mask_and_sample(df: pd.DataFrame, target_rows: int = 3000) -> pd.DataFrame:
    df = df.copy()
    required = {
        "order_no",
        "order_date",
        "customer_key",
        "product_name_raw",
        "quantity",
        "unit_price",
    }
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"SOURCE_ORDERS_SQL missing columns: {sorted(missing)}")

    df["product_name_raw"] = df["product_name_raw"].fillna("Agro Product").astype(str)
    df["customer_key"] = df["customer_key"].fillna("unknown").astype(str)
    if "product_category" not in df.columns:
        df["product_category"] = ""
    if "product_type" not in df.columns:
        df["product_type"] = ""

    recent_cut = df["order_date"].max() - pd.Timedelta(days=21)
    recent = df[df["order_date"] >= recent_cut]
    older = df[df["order_date"] < recent_cut]

    if len(recent) >= target_rows:
        sampled = recent.sample(n=target_rows, random_state=42)
    else:
        need = target_rows - len(recent)
        take = min(need, len(older))
        sampled = pd.concat(
            [recent, older.sample(n=take, random_state=42)],
            ignore_index=True,
        )

    rows = []
    for _, r in sampled.iterrows():
        order_id = f"ORD-{_stable_hash('order:' + str(r['order_no']), 8)}"
        customer_id = f"C-{_stable_hash('cust:' + str(r['customer_key']), 8)}"
        product_name = _scrub_product_name(str(r["product_name_raw"]))
        product_id = f"P-{_stable_hash('prod:' + product_name.lower(), 6)}"
        rows.append(
            {
                "order_id": order_id,
                "order_date": pd.Timestamp(r["order_date"]).date().isoformat(),
                "customer_id": customer_id,
                "customer_name": _buyer_label(str(r["customer_key"])),
                "product_id": product_id,
                "product_name": product_name,
                "category": _category(r),
                "quantity": int(r["quantity"]),
                "unit_price": float(r["unit_price"]),
                "currency": "IDR",
            }
        )

    out = pd.DataFrame(rows)
    out = (
        out.groupby(
            [
                "order_id",
                "order_date",
                "customer_id",
                "customer_name",
                "product_id",
                "product_name",
                "category",
                "currency",
            ],
            as_index=False,
        )
        .agg(quantity=("quantity", "sum"), unit_price=("unit_price", "mean"))
        .sort_values(["order_date", "order_id", "product_id"])
        .reset_index(drop=True)
    )
    return out[
        [
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
    ]


def main() -> None:
    client = get_source_client()
    raw = fetch_raw(client)
    masked = mask_and_sample(raw, target_rows=3000)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    masked.to_csv(OUT, index=False)
    print(
        f"Wrote {len(masked)} masked rows "
        f"({masked['order_id'].nunique()} orders, "
        f"{masked['customer_id'].nunique()} buyers, "
        f"{masked['product_id'].nunique()} products) -> {OUT}"
    )


if __name__ == "__main__":
    main()
