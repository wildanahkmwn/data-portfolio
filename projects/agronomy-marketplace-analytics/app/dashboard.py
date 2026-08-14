"""Lightweight Python dashboard on ClickHouse marts.

For client delivery, prefer Metabase (http://localhost:3000). Streamlit here is
a fast demo app, not the product you typically sell to business users.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.ch_utils import get_client


st.set_page_config(page_title="Agronomy Marketplace Dashboard", layout="wide")
st.title("Agronomy Marketplace Dashboard")
st.caption(
    "Demo app on ClickHouse marts. Client-facing BI: Metabase at http://localhost:3000"
)


@st.cache_data(ttl=60)
def load_frames():
    client = get_client()
    daily = client.query_df(
        """
        SELECT order_date, orders, gmv, aov, units
        FROM ecommerce.mart_daily_sales
        ORDER BY order_date
        """
    )
    customers = client.query_df(
        """
        SELECT customer_name, orders, gmv, aov, first_order_date, last_order_date
        FROM ecommerce.mart_customer_ltv
        ORDER BY gmv DESC
        LIMIT 20
        """
    )
    products = client.query_df(
        """
        SELECT product_name, category, orders, units, gmv
        FROM ecommerce.mart_top_products
        ORDER BY gmv DESC
        LIMIT 10
        """
    )
    freshness = client.query_df(
        """
        SELECT
            max(order_date) AS latest_order_date,
            max(synced_at) AS last_synced_at,
            dateDiff('hour', max(synced_at), now()) AS hours_since_sync
        FROM ecommerce.raw_orders FINAL
        """
    )
    return daily, customers, products, freshness


try:
    daily, customers, products, freshness = load_frames()
except Exception as exc:
    st.error(
        "Cannot query ClickHouse. Start the stack and run the pipeline first:\n\n"
        "docker compose up -d --build\n"
        "python scripts/run_pipeline.py"
    )
    st.exception(exc)
    st.stop()

total_gmv = float(daily["gmv"].sum()) if len(daily) else 0.0
total_orders = int(daily["orders"].sum()) if len(daily) else 0
aov = (total_gmv / total_orders) if total_orders else 0.0
hours_since_sync = (
    int(freshness["hours_since_sync"].iloc[0]) if len(freshness) else None
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("GMV (IDR)", f"{total_gmv:,.0f}")
c2.metric("Orders", f"{total_orders:,}")
c3.metric("AOV (IDR)", f"{aov:,.0f}")
c4.metric("Hours since sync", hours_since_sync if hours_since_sync is not None else "-")

st.subheader("Daily GMV")
if len(daily):
    chart_df = daily.set_index("order_date")[["gmv"]]
    st.line_chart(chart_df)
else:
    st.info("No daily sales rows yet.")

left, right = st.columns(2)
with left:
    st.subheader("Top products by GMV")
    st.dataframe(products, use_container_width=True, hide_index=True)
with right:
    st.subheader("Top customers by LTV")
    st.dataframe(customers, use_container_width=True, hide_index=True)

st.subheader("Data freshness")
st.dataframe(freshness, use_container_width=True, hide_index=True)
