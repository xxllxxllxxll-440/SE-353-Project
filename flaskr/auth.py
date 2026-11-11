
# For authentication

import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from database.app import database

# Blueprint tied to /auth URLs
bp = Blueprint('auth', __name__, url_prefix='/auth')


# Register view at /auth/register
@bp.route('/register', methods=('GET', 'POST'))
def register():
    # Submits the data with POST
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Obtains database information
        conn = database.get_db()
        error = None

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
            return redirect(url_for('index'))

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
            'SELECT * FROM userS WHERE id = %s',
            (user_id,)
        )
        g.user = cursor.fetchone()
        cursor.close()


# Logout view at /auth/logout
@bp.route('/logout')
def logout():
    # Clears cookies
    session.clear()

    # Redirects to the index of the website
    return redirect(url_for('index'))
