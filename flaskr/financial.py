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

# Initialize error
error = None

# For viewing Financial Records
# Register view at 
@bp.route('/view', methods=('GET', 'POST'))
# Require a logged in user
@login_required
def dashboard():
    # If user provides search data
    # Submits the data with POST for searching records
    if request.method == 'POST':
        start_date = date.fromisoformat(request.form['startdate'])
        end_date = date.fromisoformat(request.form['enddate'])

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
            financial_report = database.financial_report(start_date, end_date)
        except:
            error = "Unknown error"

    # Reports errors
    flash(error)
    
    # Renders HTML page will passing through dashboard data
    return render_template('financial/view.html', financial_data = financial_report)

