"""Current-month summary for the Shift Workbench dashboard."""
from datetime import date

from flask import Blueprint, current_app, flash, render_template
from mysql.connector import Error as DatabaseError

from database.app import database
from flaskr.auth import login_required
from flaskr.workbench import recent_activity

bp = Blueprint('dashboard', __name__)


@bp.route('/')
@login_required
def dashboard():
    today = date.today()
    monthly = {'revenue_total': 0, 'expense_total': 0, 'net_result': 0,
               'inventory_count': 0, 'low_stock_count': 0, 'vendor_count': 0}
    alerts, activity = [], []
    try:
        monthly = database.dashboard(today.replace(day=1), today)
        alerts = database.low_stock()[:5]
        activity = recent_activity(5)
    except (DatabaseError, RuntimeError, ValueError, TypeError, KeyError):
        current_app.logger.exception('Dashboard data could not be loaded')
        flash('Some dashboard data could not be loaded. Check the database connection.', 'error')
    return render_template('dashboard.html', dashboard=monthly,
                           low_stock=alerts, activity=activity)
