"""Shift Workbench pages, connected to the existing database helpers."""

from datetime import date
from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, request, url_for
from mysql.connector import IntegrityError

from database.app import database
from flaskr.auth import login_required
from flaskr.security import check_csrf

bp = Blueprint("workbench", __name__)


def this_month():
    today = date.today()
    return today.replace(day=1), today


def recent_activity(limit=10):
    # This view already exists in database/app/01_create_database.sql.
    return database.fetch_all(
        """SELECT activity_date, activity_type, description, amount
           FROM vw_financial_activity
           ORDER BY activity_date DESC, activity_type DESC
           LIMIT %s""", (limit,)
    )


def categories():
    return database.fetch_all(
        "SELECT expense_category_id, name FROM expense_categories ORDER BY name"
    )


def safe_date(value):
    # Existing database helper validates the date; default keeps the form simple.
    return value or date.today().isoformat()


@bp.route("/inventory")
@login_required
def inventory():
    items = database.inventory()
    term = request.args.get("q", "").strip().lower()
    low_only = request.args.get("low") == "1"
    if term:
        items = [item for item in items if term in " ".join(
            str(item.get(k) or "") for k in ("name", "sku", "category", "preferred_vendor")
        ).lower()]
    if low_only:
        items = [item for item in items if item["stock_status"] == "LOW"]
    return render_template("workbench/inventory.html", items=items,
                           search=request.args.get("q", ""), low_only=low_only)


@bp.route("/suppliers")
@login_required
def suppliers():
    return render_template("workbench/suppliers.html", suppliers=database.vendors())


@bp.route("/purchases", methods=("GET", "POST"))
@login_required
def purchases():
    if request.method == "POST":
        check_csrf()
        try:
            vendors = request.form.get("vendor_id")
            invoice = request.form.get("invoice_number", "")
            when = safe_date(request.form.get("purchase_date"))
            notes = request.form.get("notes", "").strip()
            item_ids = request.form.getlist("item_id")
            qtys = request.form.getlist("quantity")
            costs = request.form.getlist("unit_cost")
            if not (len(item_ids) == len(qtys) == len(costs)) or len(item_ids) > 20:
                raise ValueError("Enter between 1 and 20 purchase lines")
            lines = [dict(item_id=i, quantity=q, unit_cost=c)
                     for i, q, c in zip(item_ids, qtys, costs) if i or q or c]
            result = database.record_purchase(vendors, invoice, when, lines, notes)
        except (ValueError, TypeError, KeyError, IntegrityError) as error:
            flash(f"Could not record purchase: {error}", "error")
        else:
            flash("Purchase recorded. Inventory and expenses were updated together.", "success")
            return redirect(url_for("workbench.purchases"))
    return render_template("workbench/purchases.html", vendors=database.vendors(),
                           items=database.inventory(), today=date.today().isoformat())


@bp.route("/revenue", methods=("GET", "POST"))
@login_required
def revenue():
    if request.method == "POST":
        check_csrf()
        try:
            database.record_revenue(
                safe_date(request.form.get("revenue_date")),
                request.form.get("source", "").strip(),
                request.form.get("amount", ""),
                request.form.get("description", "").strip(),
            )
        except (ValueError, TypeError, IntegrityError) as error:
            flash(f"Could not record revenue: {error}", "error")
        else:
            flash("Revenue saved successfully.", "success")
            return redirect(url_for("workbench.revenue"))
    start, end = this_month()
    totals = database.financial_report(start, end)
    return render_template("workbench/revenue.html", totals=totals,
                           today=date.today().isoformat(), activity=recent_activity(8))


@bp.route("/expenses", methods=("GET", "POST"))
@login_required
def expenses():
    if request.method == "POST":
        check_csrf()
        try:
            database.record_expense(
                request.form.get("expense_category_id", ""),
                safe_date(request.form.get("expense_date")),
                request.form.get("amount", ""),
                request.form.get("description", "").strip(),
            )
        except (ValueError, TypeError, IntegrityError) as error:
            flash(f"Could not record expense: {error}", "error")
        else:
            flash("Expense saved successfully.", "success")
            return redirect(url_for("workbench.expenses"))
    start, end = this_month()
    totals = database.financial_report(start, end)
    return render_template("workbench/expenses.html", totals=totals,
                           categories=categories(), today=date.today().isoformat(),
                           activity=recent_activity(8))


@bp.route("/reports")
@login_required
def reports():
    start, end = this_month()
    raw_start = request.args.get("start", "")
    raw_end = request.args.get("end", "")
    try:
        start = date.fromisoformat(raw_start) if raw_start else start
        end = date.fromisoformat(raw_end) if raw_end else end
        if start > end:
            raise ValueError("Start date must be before end date")
    except ValueError:
        flash("Please choose a valid date range.", "error")
        return redirect(url_for("workbench.reports"))
    totals = database.financial_report(start, end)
    return render_template("workbench/reports.html", totals=totals,
                           start=start.isoformat(), end=end.isoformat(),
                           activity=recent_activity(15),
                           low_stock=database.low_stock())
