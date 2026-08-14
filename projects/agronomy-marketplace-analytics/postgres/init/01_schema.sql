-- Operational source of truth for marketplace order lines.

CREATE TABLE IF NOT EXISTS marketplace_orders (
    id              BIGSERIAL PRIMARY KEY,
    order_id        TEXT           NOT NULL,
    order_date      DATE           NOT NULL,
    customer_id     TEXT           NOT NULL,
    customer_name   TEXT           NOT NULL,
    product_id      TEXT           NOT NULL,
    product_name    TEXT           NOT NULL,
    category        TEXT           NOT NULL,
    quantity        INTEGER        NOT NULL CHECK (quantity > 0),
    unit_price      NUMERIC(14, 2) NOT NULL CHECK (unit_price >= 0),
    currency        TEXT           NOT NULL DEFAULT 'IDR',
    updated_at      TIMESTAMPTZ    NOT NULL DEFAULT now(),
    UNIQUE (order_id, product_id)
);

-- Watermark scans read (updated_at, id) in order.
CREATE INDEX IF NOT EXISTS idx_marketplace_orders_watermark
    ON marketplace_orders (updated_at, id);
