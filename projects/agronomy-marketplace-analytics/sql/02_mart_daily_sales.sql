CREATE TABLE IF NOT EXISTS ecommerce.mart_daily_sales
(
    order_date Date,
    orders UInt64,
    gmv Float64,
    aov Float64,
    units UInt64
)
ENGINE = MergeTree
ORDER BY order_date;

TRUNCATE TABLE ecommerce.mart_daily_sales;

INSERT INTO ecommerce.mart_daily_sales
SELECT
    order_date,
    countDistinct(order_id) AS orders,
    sum(quantity * unit_price) AS gmv,
    sum(quantity * unit_price) / nullIf(countDistinct(order_id), 0) AS aov,
    sum(quantity) AS units
FROM ecommerce.raw_orders FINAL
GROUP BY order_date
ORDER BY order_date;
