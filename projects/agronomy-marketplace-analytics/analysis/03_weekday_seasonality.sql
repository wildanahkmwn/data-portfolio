SELECT
    dow,
    multiIf(
        dow = 1, 'Monday',
        dow = 2, 'Tuesday',
        dow = 3, 'Wednesday',
        dow = 4, 'Thursday',
        dow = 5, 'Friday',
        dow = 6, 'Saturday',
        'Sunday'
    ) AS weekday,
    orders,
    gmv,
    aov
FROM (
    SELECT
        toDayOfWeek(order_date) AS dow,
        uniqExact(order_id) AS orders,
        round(sum(quantity * unit_price), 0) AS gmv,
        round(sum(quantity * unit_price) / nullIf(uniqExact(order_id), 0), 0) AS aov
    FROM ecommerce.raw_orders FINAL
    GROUP BY dow
)
ORDER BY dow;
