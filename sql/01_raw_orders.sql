CREATE DATABASE IF NOT EXISTS ecommerce;

CREATE TABLE IF NOT EXISTS ecommerce.raw_orders
(
    order_id String,
    order_date Date,
    customer_id String,
    customer_name String,
    product_id String,
    product_name String,
    category String,
    quantity UInt32,
    unit_price Float64,
    currency String,
    loaded_at DateTime DEFAULT now()
)
ENGINE = MergeTree
ORDER BY (order_date, order_id);
