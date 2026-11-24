
# For authentication

import functools

import secrets

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)

from werkzeug.security import check_password_hash, generate_password_hash

from database.app import database
from flaskr.security import check_csrf

# Blueprint tied to /auth URLs
bp = Blueprint('auth', __name__, url_prefix='/auth')


# Register view at /auth/register
@bp.route('/register', methods=('GET', 'POST'))
def register():
    # Submits the data with POST
    if request.method == 'POST':
        check_csrf()

        username = request.form['username']
        password = request.form['password']
        registration_code = request.form.get('registration_code', '')

        # Obtains database information
        conn = database.get_db()
        error = None

        # Validate registration code
        # Gets current registration code from secrets
        expected_code = current_app.config.get('REGISTRATION_CODE')

        # Checks code
        # If registration code is unavailable
        if not expected_code:
            error = 'Registration is currently unavailable.'
        # Checks if code matches
        elif not secrets.compare_digest(registration_code, expected_code):
            error = 'Invalid registration code.'


        # Validates that fields are not empty
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        # Pushes into database
        if error is None:
            cursor = conn.cursor()

            try:
                cursor.execute(
                    "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                    (username, generate_password_hash(password)),
                )
                conn.commit()

            # Occurs if user already exists
            except database.mysql.connector.IntegrityError:
                conn.rollback()
                error = f"User {username} is already registered."

            finally:
                cursor.close()

            # Navigates to login page if user creation is successful
            if error is None:
                return redirect(url_for("auth.login"))

        flash(error)

    # Renders the HTML for the registration form
    return render_template('auth/register.html')


# Login view at /auth/login
@bp.route('/login', methods=('GET', 'POST'))
def login():
    # Receive user and password data
    if request.method == 'POST':
        check_csrf()
        username = request.form['username']
        password = request.form['password']

        # Connect to database
        conn = database.get_db()
        error = None

        # Find user
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            'SELECT * FROM users WHERE username = %s',
            (username,)
        )
        user = cursor.fetchone()
        cursor.close()

        # No matching user found
        if user is None:
            error = 'Incorrect username.'

        # Incorrect password
        elif not check_password_hash(user['password_hash'], password):
            error = 'Incorrect password.'

        # Login, store user_id
        if error is None:
            # Stores in cookie in browser
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('dashboard.dashboard'))

        flash(error)

    # Renders HTML for login page
    return render_template('auth/login.html')


# Verifies user before each request
# Runs before view function
@bp.before_app_request
def load_logged_in_user():
    # Pulls cookie with user info
    user_id = session.get('user_id')

    if user_id is None:
        # Sets if user is none
        g.user = None
    else:
        # Verifies that user exists in server
        conn = database.get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            'SELECT * FROM users WHERE id = %s',
            (user_id,)
        )
        g.user = cursor.fetchone()
        cursor.close()


# Logout view at /auth/logout
@bp.route('/logout')
def logout():
    # Clears cookies
    session.clear()

    # Redirects to the dashboard of the website
    return redirect(url_for('dashboard.dashboard'))

# Decorator checks if user is logged in before access website
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        # If not logged in, redirects to login page
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
