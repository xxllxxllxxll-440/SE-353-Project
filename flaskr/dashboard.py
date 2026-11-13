from datetime import date

from flask import (
    Blueprint,
    flash,
    render_template
)

from flaskr.auth import login_required
from database.app import database

bp = Blueprint('dashboard', __name__)

# Initialize error
error = None

# Dashboard at root
@bp.route('/')
# Require a logged in user
@login_required
def dashboard():

    # Get current month's date range
    # Provides current date
    today = date.today()
    # Finds first day of month
    start_date = today.replace(day=1)
    # Sets the end date to today
    end_date = today

    # Retrieves the dashboard information
    if error is None:
        try:
            dashboard_data = database.dashboard(start_date, end_date)
        except:
            error = "Unknown error"

    # Reports error
    flash(error)
    
    # Renders HTML page while passing through dashboard data
    return render_template('dashboard.html', dashboard=dashboard_data)