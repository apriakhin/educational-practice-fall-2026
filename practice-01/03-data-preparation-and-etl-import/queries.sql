SELECT 
    'partners' AS table_name, 
    COUNT(*) AS row_count 
FROM partners
UNION ALL
SELECT 
    'products', 
    COUNT(*) 
FROM products
UNION ALL
SELECT 
    'deliveries', 
    COUNT(*) 
FROM deliveries;
