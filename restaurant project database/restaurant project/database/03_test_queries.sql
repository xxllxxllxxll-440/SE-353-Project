-- RUN THIRD. Use these queries to take screenshots for your demonstration.
USE restaurant_project;
-- Confirm tables exist (nine core tables; two views).
SHOW FULL TABLES;
-- See inventory items / starting balances.
SELECT item_id, sku, name, quantity_on_hand, reorder_level, unit FROM inventory_items;
-- See low-stock warnings (initially Chicken Breast and Paper Napkins).
SELECT * FROM vw_low_stock ORDER BY item_name;
-- Confirm vendors exist.
SELECT vendor_id, name, email FROM vendors ORDER BY name;
-- Trace purchases and inventory movements after using the Python purchase function.
SELECT p.purchase_id,p.invoice_number,p.purchase_date,v.name AS vendor,
       p.total_amount FROM purchases p JOIN vendors v ON v.vendor_id=p.vendor_id
ORDER BY p.purchase_id DESC;
SELECT t.inventory_transaction_id,i.name,t.movement_type,t.quantity_change,t.reason
FROM inventory_transactions t JOIN inventory_items i ON i.item_id=t.item_id
ORDER BY t.inventory_transaction_id DESC;
-- FINANCIAL SUMMARY: includes purchases once, via expenses.purchase_id.
SET @report_start = '2026-10-01';
SET @report_end = '2026-10-31';
SELECT 'Selected period' AS period,
       (SELECT COALESCE(SUM(amount),0) FROM revenue WHERE revenue_date BETWEEN @report_start AND @report_end) AS revenue_total,
       (SELECT COALESCE(SUM(amount),0) FROM expenses WHERE expense_date BETWEEN @report_start AND @report_end) AS expense_total,
       (SELECT COALESCE(SUM(amount),0) FROM revenue WHERE revenue_date BETWEEN @report_start AND @report_end)
        - (SELECT COALESCE(SUM(amount),0) FROM expenses WHERE expense_date BETWEEN @report_start AND @report_end) AS net_result;
-- Monthly totals; quarterly or yearly grouping can be added later.
SELECT DATE_FORMAT(activity_date,'%Y-%m') AS month,
       SUM(CASE WHEN activity_type='REVENUE' THEN amount ELSE 0 END) AS revenue_total,
       SUM(CASE WHEN activity_type='EXPENSE' THEN amount ELSE 0 END) AS expense_total,
       SUM(CASE WHEN activity_type='REVENUE' THEN amount ELSE -amount END) AS net_result
FROM vw_financial_activity GROUP BY DATE_FORMAT(activity_date,'%Y-%m') ORDER BY month;
