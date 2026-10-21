-- phase II database foundation
-- RUN FIRST in MySQL Workbench on the RESTAURANT PROJECT connection.
-- Safe on repeated runs: tables are only created if they do not already exist.
-- Does NOT delete tables or overwrite existing restaurant records.
CREATE DATABASE IF NOT EXISTS restaurant_project
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE restaurant_project;

CREATE TABLE IF NOT EXISTS inventory_categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS vendors (
    vendor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(30),
    email VARCHAR(150),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS inventory_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(40) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    category_id INT NOT NULL,
    preferred_vendor_id INT NULL,
    unit VARCHAR(30) NOT NULL,
    quantity_on_hand DECIMAL(12,2) NOT NULL DEFAULT 0,
    reorder_level DECIMAL(12,2) NOT NULL DEFAULT 0,
    estimated_unit_cost DECIMAL(12,2) NOT NULL DEFAULT 0,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_item_category FOREIGN KEY (category_id)
        REFERENCES inventory_categories(category_id),
    CONSTRAINT fk_item_vendor FOREIGN KEY (preferred_vendor_id)
        REFERENCES vendors(vendor_id),
    CONSTRAINT ck_item_qty CHECK (quantity_on_hand >= 0),
    CONSTRAINT ck_item_reorder CHECK (reorder_level >= 0),
    CONSTRAINT ck_item_cost CHECK (estimated_unit_cost >= 0),
    INDEX idx_item_name (name),
    INDEX idx_item_vendor (preferred_vendor_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS purchases (
    purchase_id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_id INT NOT NULL,
    invoice_number VARCHAR(80) NOT NULL,
    purchase_date DATE NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    notes VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_purchase_vendor FOREIGN KEY (vendor_id)
        REFERENCES vendors(vendor_id),
    CONSTRAINT uq_vendor_invoice UNIQUE (vendor_id, invoice_number),
    CONSTRAINT ck_purchase_total CHECK (total_amount >= 0),
    INDEX idx_purchase_date (purchase_date)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS purchase_items (
    purchase_item_id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity DECIMAL(12,2) NOT NULL,
    unit_cost DECIMAL(12,2) NOT NULL,
    line_total DECIMAL(12,2) NOT NULL,
    CONSTRAINT fk_line_purchase FOREIGN KEY (purchase_id)
        REFERENCES purchases(purchase_id),
    CONSTRAINT fk_line_item FOREIGN KEY (item_id)
        REFERENCES inventory_items(item_id),
    CONSTRAINT uq_purchase_item UNIQUE (purchase_id, item_id),
    CONSTRAINT ck_line_quantity CHECK (quantity > 0),
    CONSTRAINT ck_line_cost CHECK (unit_cost >= 0),
    CONSTRAINT ck_line_total CHECK (line_total >= 0)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS inventory_transactions (
    inventory_transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    purchase_id INT NULL,
    movement_type ENUM('INITIAL','PURCHASE','ADJUSTMENT') NOT NULL,
    quantity_change DECIMAL(12,2) NOT NULL,
    reason VARCHAR(255) NOT NULL,
    source_key VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_movement_item FOREIGN KEY (item_id)
        REFERENCES inventory_items(item_id),
    CONSTRAINT fk_movement_purchase FOREIGN KEY (purchase_id)
        REFERENCES purchases(purchase_id),
    CONSTRAINT ck_purchase_movement CHECK (
        movement_type <> 'PURCHASE' OR quantity_change > 0
    ),
    INDEX idx_movements_item_time (item_id, created_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS expense_categories (
    expense_category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS expenses (
    expense_id INT AUTO_INCREMENT PRIMARY KEY,
    expense_category_id INT NOT NULL,
    purchase_id INT NULL,
    expense_date DATE NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    description VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_expense_category FOREIGN KEY (expense_category_id)
        REFERENCES expense_categories(expense_category_id),
    CONSTRAINT fk_expense_purchase FOREIGN KEY (purchase_id)
        REFERENCES purchases(purchase_id),
    -- Each purchase adds at most one expense, which avoids duplicate reporting.
    CONSTRAINT uq_expense_purchase UNIQUE (purchase_id),
    CONSTRAINT ck_expense_amount CHECK (amount >= 0),
    INDEX idx_expense_date (expense_date)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS revenue (
    revenue_id INT AUTO_INCREMENT PRIMARY KEY,
    revenue_date DATE NOT NULL,
    source VARCHAR(100) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    description VARCHAR(255),
    external_reference VARCHAR(100) UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_revenue_amount CHECK (amount >= 0),
    INDEX idx_revenue_date (revenue_date)
) ENGINE=InnoDB;

CREATE OR REPLACE VIEW vw_low_stock AS
SELECT i.item_id, i.sku, i.name AS item_name,
       i.quantity_on_hand, i.reorder_level, i.unit,
       c.name AS category_name, v.name AS vendor_name
FROM inventory_items i
JOIN inventory_categories c ON c.category_id = i.category_id
LEFT JOIN vendors v ON v.vendor_id = i.preferred_vendor_id
WHERE i.active = TRUE AND i.quantity_on_hand <= i.reorder_level;

CREATE OR REPLACE VIEW vw_financial_activity AS
SELECT revenue_date AS activity_date, 'REVENUE' AS activity_type,
       amount, source AS description
FROM revenue
UNION ALL
SELECT expense_date AS activity_date, 'EXPENSE' AS activity_type,
       amount, description
FROM expenses;
