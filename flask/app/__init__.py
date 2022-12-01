import logging
import os

from dotenv import load_dotenv
import rollbar
import rollbar.contrib.flask

from flask import Flask, got_request_exception
from flask_cors import CORS
from flask_login import LoginManager
from flask_pymysql import MySQL

from app.pusher import Pusher

db = MySQL()
login_manager = LoginManager()
pusher_client = Pusher()


def get_config():
    app_env = os.environ.get("FLASK_ENV").lower().title()
    return f'config.{app_env}Config'


def create_app(test_config=False):
    load_dotenv()

    app = Flask(__name__)
    if test_config:
        # load the test config if passed in
        app.config.from_object('config.TestConfig')
    else:
        app.config.from_object(get_config())
    app.logger.setLevel(logging.WARNING)

    @app.before_first_request
    def init_rollbar():
        """init rollbar module"""
        rollbar.init(
            # access token
            app.config['ROLLBAR_ACCESS_TOKEN'],
            # environment name
            app.config['STAGE'],
            # server root directory, makes tracebacks prettier
            root=os.path.dirname(os.path.realpath(__file__)),
            # flask already sets up logging
            allow_logging_basic_config=False)

        # send exceptions from `app` to rollbar, using flask's signal system.
        got_request_exception.connect(rollbar.contrib.flask.report_exception, app)

    # Add simple CORS support
    CORS(app)

    # Configure Mysql
    pymysql_connect_kwargs = {
        'user': app.config['MYSQL_USER'],
        'password': app.config['MYSQL_PASSWORD'],
        'host': app.config['MYSQL_HOST'],
        'port': int(app.config['MYSQL_PORT']),
        'database': app.config['MYSQL_DATABASE']
    }
    app.config['pymysql_kwargs'] = pymysql_connect_kwargs
    db.init_app(app)

    # Configure Flask-login
    login_manager.init_app(app)

    # Configure pusher
    pusher_client.init_app(app)

    from app import models, tokens, tasks, loaders, repositories

    from . import views
    views.init_app(app)

    @app.route('/')
    def hello_world():
        return 'Welcome to Flask Template.'

    return app
