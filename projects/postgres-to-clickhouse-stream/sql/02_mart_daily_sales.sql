TRUNCATE TABLE IF EXISTS pg2ch.mart_daily_sales;

INSERT INTO pg2ch.mart_daily_sales
SELECT
    order_date,
    uniqExact(order_id) AS orders,
    sum(quantity * unit_price) AS gmv,
    gmv / orders AS aov,
    sum(quantity) AS units
FROM pg2ch.raw_orders FINAL
GROUP BY order_date
ORDER BY order_date;
