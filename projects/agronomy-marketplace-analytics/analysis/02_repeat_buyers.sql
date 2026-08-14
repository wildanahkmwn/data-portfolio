-- Repeat buyer rate: how many buyers come back more than once.

WITH buyer_orders AS (
    SELECT
        customer_id,
        uniqExact(order_id) AS orders,
        sum(quantity * unit_price) AS gmv
    FROM ecommerce.raw_orders FINAL
    GROUP BY customer_id
)
SELECT
    count() AS buyers,
    countIf(orders = 1) AS one_time_buyers,
    countIf(orders >= 2) AS repeat_buyers,
    round(100.0 * countIf(orders >= 2) / nullIf(count(), 0), 1) AS repeat_rate_pct,
    round(avg(gmv), 0) AS avg_buyer_gmv,
    round(avgIf(gmv, orders >= 2), 0) AS avg_repeat_buyer_gmv
FROM buyer_orders;
