WITH first_orders AS (
    SELECT
        customer_id,
        min(order_date) AS first_order_date,
        toStartOfMonth(min(order_date)) AS cohort_month
    FROM ecommerce.raw_orders FINAL
    GROUP BY customer_id
),
orders AS (
    SELECT
        customer_id,
        order_id,
        order_date,
        quantity * unit_price AS line_gmv
    FROM ecommerce.raw_orders FINAL
),
spend AS (
    SELECT
        f.cohort_month,
        f.customer_id,
        sumIf(o.line_gmv, o.order_date <= f.first_order_date + 30) AS gmv_d30,
        uniqExactIf(o.order_id, o.order_date <= f.first_order_date + 30) AS orders_d30
    FROM first_orders f
    INNER JOIN orders o ON o.customer_id = f.customer_id
    GROUP BY f.cohort_month, f.customer_id
)
SELECT
    cohort_month,
    count() AS buyers,
    round(avg(gmv_d30), 0) AS avg_ltv_d30,
    round(quantile(0.5)(gmv_d30), 0) AS median_ltv_d30,
    round(avg(orders_d30), 2) AS avg_orders_d30
FROM spend
GROUP BY cohort_month
ORDER BY cohort_month;
