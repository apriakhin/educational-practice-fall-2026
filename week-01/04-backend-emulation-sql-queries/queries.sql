SELECT
    partners.id,
    partners.name,
    COUNT(deliveries.id) AS deliveries_count
FROM partners
LEFT JOIN deliveries ON deliveries.partner_id = partners.id
GROUP BY partners.id, partners.name
ORDER BY partners.name;


BEGIN;

WITH test_partner AS (
    INSERT INTO partners (name, inn, email, phone)
    VALUES ('ООО "Тест"', '0000000000', 'test@test.ru', '+71234567890')
    ON CONFLICT (inn) DO UPDATE
    SET name = EXCLUDED.name,
        email = EXCLUDED.email,
        phone = EXCLUDED.phone
    RETURNING id
)
INSERT INTO deliveries (partner_id, product_id, quantity)
SELECT id, 1, 1 
FROM test_partner;

COMMIT;


WITH params AS (
    SELECT
        1::BIGINT AS partner_id,
        DATE '2026-03-01' AS date_from,
        DATE '2026-03-31' AS date_to
)
SELECT
    deliveries.id AS delivery_id,
    deliveries.delivery_date,
    products.name AS product_name,
    deliveries.quantity,
    products.price,
    deliveries.quantity * products.price AS total_amount
FROM deliveries
JOIN products ON products.id = deliveries.product_id
JOIN params ON params.partner_id = deliveries.partner_id
WHERE deliveries.delivery_date BETWEEN params.date_from AND params.date_to
ORDER BY deliveries.delivery_date, deliveries.id;
