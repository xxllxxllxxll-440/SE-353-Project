from flask import Flask
from database.app import database as db


def create_app(test_config=None):
    # create and configure the app
    # Creates instance
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # Keeps data safe, needs modified before publishing
        SECRET_KEY='dev'
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # a simple page that says hello (temp)
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # Importing authentication blueprint
    from . import auth
    app.register_blueprint(auth.bp)

    # Importing dashboard blueprint
    from . import dashboard
    app.register_blueprint(dashboard.bp)
    # Needed to push dashboard to root of site
    app.add_url_rule('/', endpoint='dashboard')

    # Importing financial blueprint
    from . import financial
    app.register_blueprint(financial.bp)

    return app