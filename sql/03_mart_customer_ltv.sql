CREATE TABLE IF NOT EXISTS ecommerce.mart_customer_ltv
(
    customer_id String,
    customer_name String,
    first_order_date Date,
    last_order_date Date,
    orders UInt64,
    gmv Float64,
    aov Float64
)
ENGINE = MergeTree
ORDER BY (gmv, customer_id);

TRUNCATE TABLE ecommerce.mart_customer_ltv;

INSERT INTO ecommerce.mart_customer_ltv
SELECT
    customer_id,
    any(customer_name) AS customer_name,
    min(order_date) AS first_order_date,
    max(order_date) AS last_order_date,
    countDistinct(order_id) AS orders,
    sum(quantity * unit_price) AS gmv,
    sum(quantity * unit_price) / nullIf(countDistinct(order_id), 0) AS aov
FROM ecommerce.raw_orders
GROUP BY customer_id
ORDER BY gmv DESC;
