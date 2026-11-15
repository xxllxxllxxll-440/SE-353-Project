import os
from decimal import Decimal
from flask import Flask
from database.app import database as db
from flaskr.security import csrf_token


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    # For local development only. Set FLASK_SECRET_KEY before real deployment.
    app.config.from_mapping(SECRET_KEY=os.getenv('FLASK_SECRET_KEY', 'dev'))
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    @app.template_filter('cash')
    def cash(value):
        return '${:,.2f}'.format(Decimal(str(value or 0)))

    @app.context_processor
    def common_context():
        from datetime import date
        return dict(csrf_token=csrf_token, current_month=date.today().strftime('%B %Y'))

    @app.teardown_appcontext
    def close_connection(error=None):
        db.close_db(error)

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import auth, dashboard, financial, workbench
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(workbench.bp)
    app.register_blueprint(financial.bp)
    return app
