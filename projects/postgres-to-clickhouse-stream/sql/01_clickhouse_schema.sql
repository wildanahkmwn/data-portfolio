CREATE DATABASE IF NOT EXISTS pg2ch;

CREATE TABLE IF NOT EXISTS pg2ch.raw_orders
(
    source_id UInt64,
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
    source_updated_at DateTime64(3, 'UTC'),
    synced_at DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(synced_at)
ORDER BY (order_date, order_id, product_id, source_id);

CREATE TABLE IF NOT EXISTS pg2ch.stream_watermarks
(
    stream_name String,
    last_updated_at DateTime64(3, 'UTC'),
    last_source_id UInt64,
    rows_synced UInt64,
    updated_at DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(updated_at)
ORDER BY stream_name;

CREATE TABLE IF NOT EXISTS pg2ch.mart_daily_sales
(
    order_date Date,
    orders UInt64,
    gmv Float64,
    aov Float64,
    units UInt64
)
ENGINE = MergeTree
ORDER BY order_date;
