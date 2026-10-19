"""Database layer for the Sixty-Three Social classroom prototype.

This module is meant to be imported by Cole's Flask/backend application.
It does not implement login, authorization, or a production-ready public API.
"""
import os
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")
CENTS = Decimal("0.01")


def money(value):
    try:
        x = Decimal(str(value)).quantize(CENTS, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError("Amount must be a valid number") from exc
    if not x.is_finite() or x < 0:
        raise ValueError("Amount cannot be negative")
    return x


def positive_qty(value):
    try:
        x = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError("Quantity must be a valid number") from exc
    if not x.is_finite() or x <= 0:
        raise ValueError("Quantity must be greater than zero")
    return x


def valid_date(value):
    if isinstance(value, date):
        return value.isoformat()
    return date.fromisoformat(str(value)).isoformat()


def get_connection():
    """Connect to the shared Aiven database with CA verification enabled."""
    expected = ["DB_HOST", "DB_PORT", "DB_USER", "DB_PASSWORD", "DB_SSL_CA"]
    missing = [k for k in expected if not os.getenv(k)]
    if missing:
        raise RuntimeError("Add these fields to .env: " + ", ".join(missing))
    ca = Path(os.environ["DB_SSL_CA"]).expanduser()
    if not ca.is_file():
        raise RuntimeError("DB_SSL_CA must point to your downloaded Aiven CA certificate")
    return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.getenv("DB_NAME", "restaurant_project"),
        ssl_ca=str(ca),
        ssl_disabled=False,
        ssl_verify_cert=True,
        ssl_verify_identity=True,
        connection_timeout=10,
        autocommit=False,
    )


def fetch_all(sql, params=()):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(sql, params)
            return cursor.fetchall()
        finally:
            cursor.close()
    finally:
        conn.close()


def fetch_one(sql, params=()):
    rows = fetch_all(sql, params)
    return rows[0] if rows else None


def connection_check():
    return fetch_one("SELECT DATABASE() AS database_name, VERSION() AS mysql_version")


def inventory():
    return fetch_all("""SELECT i.item_id, i.sku, i.name, c.name AS category,
                            v.name AS preferred_vendor, i.unit, i.quantity_on_hand,
                            i.reorder_level, i.estimated_unit_cost,
                            CASE WHEN i.quantity_on_hand <= i.reorder_level
                                THEN 'LOW' ELSE 'OK' END AS stock_status
                       FROM inventory_items i
                       JOIN inventory_categories c ON c.category_id=i.category_id
                       LEFT JOIN vendors v ON v.vendor_id=i.preferred_vendor_id
                       WHERE i.active=TRUE ORDER BY i.name""")


def low_stock():
    return fetch_all("SELECT * FROM vw_low_stock ORDER BY item_name")


def vendors():
    return fetch_all("SELECT vendor_id, name, phone, email FROM vendors WHERE active=TRUE ORDER BY name")


def financial_report(start, end):
    start, end = valid_date(start), valid_date(end)
    if start > end:
        raise ValueError("Start date must not be after end date")
    return fetch_one("""SELECT
        (SELECT COALESCE(SUM(amount),0) FROM revenue
         WHERE revenue_date BETWEEN %s AND %s) AS revenue_total,
        (SELECT COALESCE(SUM(amount),0) FROM expenses
         WHERE expense_date BETWEEN %s AND %s) AS expense_total,
        (SELECT COALESCE(SUM(amount),0) FROM revenue
         WHERE revenue_date BETWEEN %s AND %s) -
        (SELECT COALESCE(SUM(amount),0) FROM expenses
         WHERE expense_date BETWEEN %s AND %s) AS net_result""",
        (start, end, start, end, start, end, start, end))


def dashboard(start, end):
    totals = financial_report(start, end)
    counts = fetch_one("""SELECT
        (SELECT COUNT(*) FROM inventory_items WHERE active=TRUE) AS inventory_count,
        (SELECT COUNT(*) FROM vw_low_stock) AS low_stock_count,
        (SELECT COUNT(*) FROM vendors WHERE active=TRUE) AS vendor_count""")
    return {**counts, **totals}


def record_purchase(vendor_id, invoice_number, purchase_date, lines, notes=""):
    """Receive a purchase with ONE atomic transaction:
    purchase + purchase lines + inventory increases + movements + one expense.
    A duplicate vendor/invoice fails and changes nothing (safe against retries).
    lines example: [{"item_id":1,"quantity":"5","unit_cost":"3.50"}].
    """
    if not lines:
        raise ValueError("A purchase needs at least one item")
    invoice_number = str(invoice_number).strip()
    if not invoice_number:
        raise ValueError("Invoice/reference cannot be blank")
    when = valid_date(purchase_date)
    vendor_id = int(vendor_id)
    normalized = []
    seen = set()
    for line in lines:
        item_id = int(line["item_id"])
        if item_id in seen:
            raise ValueError("List each item only once per purchase")
        seen.add(item_id)
        qty, cost = positive_qty(line["quantity"]), money(line["unit_cost"])
        normalized.append((item_id, qty, cost, (qty * cost).quantize(CENTS, rounding=ROUND_HALF_UP)))
    total = sum((x[3] for x in normalized), Decimal("0.00"))
    conn = get_connection()
    try:
        conn.start_transaction()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT vendor_id FROM vendors WHERE vendor_id=%s AND active=TRUE", (vendor_id,))
            if cursor.fetchone() is None:
                raise ValueError("Vendor not found or inactive")
            # Lock items in a consistent order for concurrent purchase requests.
            for item_id in sorted(seen):
                cursor.execute("SELECT item_id FROM inventory_items WHERE item_id=%s AND active=TRUE FOR UPDATE", (item_id,))
                if cursor.fetchone() is None:
                    raise ValueError(f"Inventory item {item_id} was not found or is inactive")
            cursor.execute("""INSERT INTO purchases
                (vendor_id, invoice_number, purchase_date, total_amount, notes)
                VALUES (%s,%s,%s,%s,%s)""",
                (vendor_id, invoice_number, when, total, notes))
            purchase_id = cursor.lastrowid
            for item_id, qty, cost, line_total in normalized:
                cursor.execute("""INSERT INTO purchase_items
                    (purchase_id,item_id,quantity,unit_cost,line_total)
                    VALUES (%s,%s,%s,%s,%s)""",
                    (purchase_id, item_id, qty, cost, line_total))
                line_id = cursor.lastrowid
                cursor.execute("""UPDATE inventory_items
                    SET quantity_on_hand=quantity_on_hand+%s,
                        estimated_unit_cost=%s WHERE item_id=%s""", (qty, cost, item_id))
                cursor.execute("""INSERT INTO inventory_transactions
                    (item_id,purchase_id,movement_type,quantity_change,reason,source_key)
                    VALUES (%s,%s,'PURCHASE',%s,%s,%s)""",
                    (item_id, purchase_id, qty, f"Received invoice {invoice_number}", f"PURCHASE_ITEM:{line_id}"))
            cursor.execute("""INSERT INTO expenses
                (expense_category_id,purchase_id,expense_date,amount,description)
                SELECT expense_category_id,%s,%s,%s,%s FROM expense_categories
                WHERE name='Inventory Purchases'""",
                (purchase_id, when, total, f"Vendor purchase {invoice_number}"))
            if cursor.rowcount != 1:
                raise ValueError("Expense category 'Inventory Purchases' missing; run sample data setup")
            conn.commit()
            return {"purchase_id": purchase_id, "total_amount": str(total), "items_received": len(normalized)}
        finally:
            cursor.close()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def record_expense(expense_category_id, expense_date, amount, description):
    if not str(description).strip():
        raise ValueError("Expense description is required")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        try:
            cursor.execute("""INSERT INTO expenses
                (expense_category_id,purchase_id,expense_date,amount,description)
                VALUES (%s,NULL,%s,%s,%s)""",
                (int(expense_category_id), valid_date(expense_date), money(amount), str(description).strip()))
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def record_revenue(revenue_date, source, amount, description="", external_reference=None):
    if not str(source).strip():
        raise ValueError("Revenue source is required")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        try:
            cursor.execute("""INSERT INTO revenue
                (revenue_date,source,amount,description,external_reference)
                VALUES (%s,%s,%s,%s,%s)""",
                (valid_date(revenue_date), str(source).strip(), money(amount), description, external_reference))
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
