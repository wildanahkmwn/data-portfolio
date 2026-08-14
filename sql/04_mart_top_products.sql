CREATE TABLE IF NOT EXISTS ecommerce.mart_top_products
(
    product_id String,
    product_name String,
    category String,
    orders UInt64,
    units UInt64,
    gmv Float64
)
ENGINE = MergeTree
ORDER BY (gmv, product_id);

TRUNCATE TABLE ecommerce.mart_top_products;

INSERT INTO ecommerce.mart_top_products
SELECT
    product_id,
    any(product_name) AS product_name,
    any(category) AS category,
    countDistinct(order_id) AS orders,
    sum(quantity) AS units,
    sum(quantity * unit_price) AS gmv
FROM ecommerce.raw_orders
GROUP BY product_id
ORDER BY gmv DESC;
