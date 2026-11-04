# For authentication

import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

# May need to modify this
from database.app import database

# Blueprint tied to /auth URLs
bp = Blueprint('auth', __name__, url_prefix='/auth')