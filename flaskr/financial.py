from datetime import date

from flask import (
    Blueprint,
    flash,
    render_template,
    request
)

from flaskr.auth import login_required
from database.app import database

# Blueprint tied to /financial URLs
bp = Blueprint('financial', __name__, url_prefix='/financial')



# For viewing Financial Records
# Register view at 
@bp.route('/view', methods=('GET', 'POST'))
# Require a logged in user
@login_required
def dashboard():

    # Initialize error
    error = None

    # If user provides search data
    # Submits the data with POST for searching records
    if request.method == 'POST':
        start_date = date.fromisoformat(request.form['start_date'])
        end_date = date.fromisoformat(request.form['end_date'])

        # Verify that fields are not empty
        if not start_date:
            error = 'Start date is required.'
        elif not end_date:
            error = 'End date is required.'


    # If user doesn't provide search data (first load)
    if request.method == "GET":
        # Get current month's date range
        # Provides current date
        today = date.today()
        # Finds first day of month
        start_date = today.replace(day=1)
        # Sets the end date to today
        end_date = today

    # Retrieve info from database
    if error is None:
        try:
            # Summarizes current range
            financial_total = database.financial_report(start_date, end_date)
            # Provides all entries within range
            financial_entries = database.financial_transactions(start_date, end_date)
            # Provides categories
            categories = database.financial_categories()

        except:
            error = "Unknown error"

    # Reports errors
    if error is not None:
        flash(error)
    
    # Renders HTML page will passing through dashboard data
    return render_template('financial/view.html',
                           financial_total = financial_total,
                           financial_entries = financial_entries,
                           categories = categories,
                           start_date = start_date,
                           end_date = end_date)

# For editing / creating expenses
@bp.route('/expense', methods=('GET', 'POST'))
# Require a logged in user
@login_required
def modify():

    # Initialize error
    error = None

    # Pull expense categories with IDs
    categories = database.expense_categories()

    # When user submits the data with post
    if request.method == 'POST':
        category = request.form['category']
        expense_date = date.fromisoformat(request.form['expense_date'])
        amount = request.form['amount']
        description = request.form['description']

        # Validate that required fields are not empty
        if not description:
            error = "Description is required."
        elif not amount:
            error = "Amount is required."
        elif not expense_date:
            error = "Date is required."

    # Renders the HTML for the website
    return render_template('financial/expense.html',
                           categories=categories)