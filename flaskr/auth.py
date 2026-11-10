# For authentication

import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from database.app import database as db

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
        db = db.get_db()
        error = None

        # Validates that fields are not empty
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        # Pushes into database
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            # Occurs if user already exists
            except db.IntegrityError:
                error = f"User {username} is already registered."
            # Navigates to login page if user creation is successful
            else:
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
        db = db.get_db()
        error = None
        # Find user
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        # No matching user found
        if user is None:
            error = 'Incorrect username.'
        # Incorrect password
        elif not check_password_hash(user['password'], password):
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
        g.user = db.get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

# Logout view at /auth/logout
@bp.route('/logout')
def logout():
    # Clears cookies
    session.clear()
    # Redirects to the index of the website
    return redirect(url_for('index'))