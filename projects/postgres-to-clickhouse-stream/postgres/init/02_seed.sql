-- Seed a small agronomy-style order set so the stream has something to move.

INSERT INTO marketplace_orders (
    order_id, order_date, customer_id, customer_name,
    product_id, product_name, category, quantity, unit_price, currency, updated_at
) VALUES
('ORD-PG-1001', CURRENT_DATE - 14, 'C-1001', 'Mitra Tani 1001', 'P-FERT-01', 'NPK 16-16-16 50kg', 'Pupuk', 10, 185000, 'IDR', now() - interval '14 days'),
('ORD-PG-1001', CURRENT_DATE - 14, 'C-1001', 'Mitra Tani 1001', 'P-HERB-01', 'Glyphosate 1L', 'Racun', 4, 72000, 'IDR', now() - interval '14 days'),
('ORD-PG-1002', CURRENT_DATE - 10, 'C-1002', 'Koperasi Hijau 1002', 'P-SEED-01', 'Benih Sawit Topaz 100 butir', 'Benih', 5, 950000, 'IDR', now() - interval '10 days'),
('ORD-PG-1003', CURRENT_DATE - 7, 'C-1003', 'UD Agro 1003', 'P-TOOL-01', 'Palm Sickle Pro', 'Tools', 8, 95000, 'IDR', now() - interval '7 days'),
('ORD-PG-1004', CURRENT_DATE - 5, 'C-1004', 'Toko Pupuk 1004', 'P-FERT-02', 'ZA Cap Daun 50kg', 'Pupuk', 20, 360000, 'IDR', now() - interval '5 days'),
('ORD-PG-1005', CURRENT_DATE - 3, 'C-1005', 'CV Kebun 1005', 'P-PPE-01', 'Safety Boots Size 42', 'PPE', 6, 210000, 'IDR', now() - interval '3 days'),
('ORD-PG-1006', CURRENT_DATE - 2, 'C-1002', 'Koperasi Hijau 1002', 'P-HERB-02', 'Roundup 486 SL 20L', 'Racun', 1, 2054795, 'IDR', now() - interval '2 days'),
('ORD-PG-1007', CURRENT_DATE - 1, 'C-1006', 'Gapoktan 1006', 'P-FERT-01', 'NPK 16-16-16 50kg', 'Pupuk', 12, 185000, 'IDR', now() - interval '1 day'),
('ORD-PG-1008', CURRENT_DATE, 'C-1007', 'Distributor Bibit 1007', 'P-SEED-02', 'Seedling Tray 50 cell', 'Nursery', 30, 28000, 'IDR', now() - interval '2 hours'),
('ORD-PG-1009', CURRENT_DATE, 'C-1003', 'UD Agro 1003', 'P-MAIN-01', 'Motor Grease 500g', 'Maintenance', 15, 45000, 'IDR', now() - interval '1 hour'),
('ORD-PG-1010', CURRENT_DATE, 'C-1008', 'Usaha Kebun 1008', 'P-FERT-02', 'ZA Cap Daun 50kg', 'Pupuk', 8, 360000, 'IDR', now() - interval '30 minutes'),
('ORD-PG-1011', CURRENT_DATE, 'C-1001', 'Mitra Tani 1001', 'P-HERB-01', 'Glyphosate 1L', 'Racun', 10, 72000, 'IDR', now() - interval '10 minutes');
