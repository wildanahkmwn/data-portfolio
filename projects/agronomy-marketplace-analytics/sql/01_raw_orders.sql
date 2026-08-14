CREATE DATABASE IF NOT EXISTS ecommerce;

-- Sink for Postgres order lines. ReplacingMergeTree keeps the newest version
-- of a source row so re-synced updates do not need mutations.
CREATE TABLE IF NOT EXISTS ecommerce.raw_orders
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

-- Stream state so the sync can resume after a restart.
CREATE TABLE IF NOT EXISTS ecommerce.stream_watermarks
(
    stream_name String,
    last_updated_at DateTime64(3, 'UTC'),
    last_source_id UInt64,
    rows_synced UInt64,
    updated_at DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(updated_at)
ORDER BY stream_name;
