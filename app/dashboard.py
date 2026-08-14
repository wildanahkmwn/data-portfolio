"""Streamlit dashboard on top of ecommerce ClickHouse marts."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.ch_utils import get_client


st.set_page_config(page_title="Ecommerce Sales Dashboard", layout="wide")
st.title("Ecommerce Sales Dashboard")
st.caption("Portfolio demo: ClickHouse marts served via Streamlit")


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
            max(loaded_at) AS last_loaded_at,
            dateDiff('hour', max(loaded_at), now()) AS hours_since_load
        FROM ecommerce.raw_orders
        """
    )
    return daily, customers, products, freshness


try:
    daily, customers, products, freshness = load_frames()
except Exception as exc:
    st.error(
        "Cannot query ClickHouse. Start Docker and run the pipeline first:\n\n"
        "docker compose up -d\n"
        "python scripts/run_pipeline.py"
    )
    st.exception(exc)
    st.stop()

total_gmv = float(daily["gmv"].sum()) if len(daily) else 0.0
total_orders = int(daily["orders"].sum()) if len(daily) else 0
aov = (total_gmv / total_orders) if total_orders else 0.0
hours_since_load = (
    int(freshness["hours_since_load"].iloc[0]) if len(freshness) else None
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("GMV (IDR)", f"{total_gmv:,.0f}")
c2.metric("Orders", f"{total_orders:,}")
c3.metric("AOV (IDR)", f"{aov:,.0f}")
c4.metric("Hours since load", hours_since_load if hours_since_load is not None else "-")

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
