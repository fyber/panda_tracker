import os
import logging
import logging.config

from flask import Flask, jsonify

from .core import mongo, jwt, ApplicationError
from .utils import register_blueprints


def create_app(settings_override=None):
    app = Flask('panda_tracker', instance_relative_config=True)

    app.config.from_object('panda_tracker.settings')
    app.config.from_pyfile('config.py', silent=True)
    app.config.from_object(settings_override)

    logging.config.dictConfig(app.config['LOGGING'])

    # Set the default JSON encoder
    # app.json_encoder = JSONEncoder

    mongo.init_app(app)
    jwt.init_app(app)

    root_package_path = os.path.dirname(__file__)
    register_blueprints(app, 'panda_tracker', root_package_path)

    app.errorhandler(ApplicationError)(application_error_handler)

    return app


def application_error_handler(error):
    return jsonify({
        'status_code': error.status_code,
        'error': error.error,
        'description': error.description,
    }), error.status_code
