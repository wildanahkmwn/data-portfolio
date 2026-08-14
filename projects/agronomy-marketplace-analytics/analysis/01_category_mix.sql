WITH base AS (
    SELECT
        category,
        uniqExact(order_id) AS orders,
        sum(quantity) AS units,
        sum(quantity * unit_price) AS gmv
    FROM ecommerce.raw_orders FINAL
    WHERE order_date >= today() - 60
    GROUP BY category
),
tot AS (
    SELECT sum(gmv) AS total_gmv FROM base
)
SELECT
    b.category,
    b.orders,
    b.units,
    round(b.gmv, 0) AS gmv,
    round(100.0 * b.gmv / nullIf(t.total_gmv, 0), 1) AS gmv_share_pct,
    round(b.gmv / nullIf(b.orders, 0), 0) AS aov
FROM base b
CROSS JOIN tot t
ORDER BY b.gmv DESC;
