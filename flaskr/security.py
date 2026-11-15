"""Small CSRF check for forms that change restaurant data."""

import hmac
import secrets

from flask import abort, request, session


def csrf_token():
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_urlsafe(32)
    return session["_csrf_token"]


def check_csrf():
    submitted = request.form.get("_csrf_token", "")
    expected = session.get("_csrf_token", "")
    if not submitted or not expected or not hmac.compare_digest(submitted, expected):
        abort(400, description="The form expired. Refresh and try again.")
