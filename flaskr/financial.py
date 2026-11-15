"""Transaction history page contributed in the latest team project.

Keeps /financial/view while using the shared Shift Workbench layout.
Filters are read-only GET parameters, not database changes.
"""
from datetime import date
from decimal import Decimal

from flask import Blueprint, current_app, flash, render_template, request
from mysql.connector import Error as DatabaseError

from database.app import database
from flaskr.auth import login_required

bp = Blueprint('financial', __name__, url_prefix='/financial')


@bp.route('/view', methods=['GET'])
@login_required
def view():
    today = date.today()
    start_date = today.replace(day=1)
    end_date = today
    category = request.args.get('category', '').strip()
    error = None
    categories = []
    entries = []
    totals = {'revenue_total': Decimal('0.00'),
              'expense_total': Decimal('0.00'),
              'net_result': Decimal('0.00')}

    try:
        if request.args.get('start_date'):
            start_date = date.fromisoformat(request.args['start_date'])
        if request.args.get('end_date'):
            end_date = date.fromisoformat(request.args['end_date'])
        if start_date > end_date:
            raise ValueError('The start date must be before or equal to the end date.')
    except (ValueError, OverflowError):
        error = 'Please choose a valid date range.'
        start_date, end_date = today.replace(day=1), today

    try:
        categories = database.financial_categories()
        allowed_categories = {row['category'] for row in categories}
        if category and category not in allowed_categories:
            error = 'Please select a category from the list.'
            category = ''
        entries = database.financial_transactions(start_date, end_date,
                                                   category or None)
        if category:
            # Unlike the old page, the summary also respects the category choice.
            revenue = sum((Decimal(str(row['amount'])) for row in entries
                           if row['transaction_type'] == 'Revenue'), Decimal('0.00'))
            expense = sum((Decimal(str(row['amount'])) for row in entries
                           if row['transaction_type'] == 'Expense'), Decimal('0.00'))
            totals = {'revenue_total': revenue, 'expense_total': expense,
                      'net_result': revenue-expense}
        else:
            totals = database.financial_report(start_date, end_date)
    except (DatabaseError, RuntimeError, ValueError, TypeError, KeyError):
        current_app.logger.exception('Could not load financial records')
        error = 'Financial records could not be loaded. Check your database connection.'

    if error:
        flash(error, 'error')
    return render_template('financial/view.html', financial_total=totals,
                           financial_entries=entries, categories=categories,
                           selected_category=category,
                           start_date=start_date.isoformat(),
                           end_date=end_date.isoformat())
