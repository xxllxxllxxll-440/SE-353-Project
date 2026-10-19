-- RUN SECOND, after 01_create_database.sql.
-- Demonstration data only, not real Sixty-Three Social financial records.
-- Safe to re-run: seeded named rows and references are not duplicated.
USE restaurant_project;

INSERT INTO inventory_categories (name,description) VALUES
 ('Food','Ingredients and kitchen food items'),
 ('Beverages','Drinks and beverages'),
 ('Supplies','Cleaning, paper, and serving supplies')
ON DUPLICATE KEY UPDATE name = VALUES(name);

INSERT INTO vendors (name, phone, email) VALUES
 ('Fresh Valley Foods','555-0101','orders@example.test'),
 ('Midwest Beverage Co','555-0102','drinks@example.test'),
 ('Restaurant Supply','555-0103','supplies@example.test')
ON DUPLICATE KEY UPDATE name = VALUES(name);

INSERT INTO inventory_items (sku,name,category_id,preferred_vendor_id,unit,quantity_on_hand,reorder_level,estimated_unit_cost) VALUES
 ('FOOD-001','Chicken Breast', (SELECT category_id FROM inventory_categories WHERE name='Food'), (SELECT vendor_id FROM vendors WHERE name='Fresh Valley Foods'),'lb',8,10,3.50),
 ('FOOD-002','Rice', (SELECT category_id FROM inventory_categories WHERE name='Food'), (SELECT vendor_id FROM vendors WHERE name='Fresh Valley Foods'),'lb',25,8,1.20),
 ('BEV-001','Soda', (SELECT category_id FROM inventory_categories WHERE name='Beverages'), (SELECT vendor_id FROM vendors WHERE name='Midwest Beverage Co'),'case',12,5,6.00),
 ('SUP-001','Paper Napkins',(SELECT category_id FROM inventory_categories WHERE name='Supplies'),(SELECT vendor_id FROM vendors WHERE name='Restaurant Supply'),'box',3,4,9.00)
ON DUPLICATE KEY UPDATE sku = VALUES(sku);

INSERT INTO expense_categories (name) VALUES
 ('Inventory Purchases'),('Rent'),('Utilities'),('Other')
ON DUPLICATE KEY UPDATE name = VALUES(name);

-- Initial quantity changes are logged for a useful inventory audit trail.
INSERT INTO inventory_transactions (item_id,movement_type,quantity_change,reason,source_key)
SELECT item_id,'INITIAL',quantity_on_hand,'Demo opening balance',CONCAT('INITIAL:',sku)
FROM inventory_items
WHERE sku IN ('FOOD-001','FOOD-002','BEV-001','SUP-001')
ON DUPLICATE KEY UPDATE source_key = VALUES(source_key);

INSERT INTO expenses (expense_category_id,purchase_id,expense_date,amount,description)
SELECT expense_category_id,NULL,'2026-10-02',950.00,'Demo monthly rent'
FROM expense_categories WHERE name='Rent'
AND NOT EXISTS (SELECT 1 FROM expenses WHERE description='Demo monthly rent' AND expense_date='2026-10-02');

INSERT INTO expenses (expense_category_id,purchase_id,expense_date,amount,description)
SELECT expense_category_id,NULL,'2026-10-03',225.00,'Demo utilities'
FROM expense_categories WHERE name='Utilities'
AND NOT EXISTS (SELECT 1 FROM expenses WHERE description='Demo utilities' AND expense_date='2026-10-03');

INSERT INTO revenue (revenue_date,source,amount,description,external_reference) VALUES
 ('2026-10-04','Restaurant Sales',1800.00,'Demo daily restaurant sales','DEMO-REV-001'),
 ('2026-10-05','Event Revenue',1200.00,'Demo banquet revenue','DEMO-REV-002')
ON DUPLICATE KEY UPDATE external_reference = VALUES(external_reference);
