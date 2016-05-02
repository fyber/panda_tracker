import os
import logging
import logging.config

from flask import Flask, jsonify

from .core import mongo, jwt, ApplicationError
from .utils import register_blueprints, JSONEncoder


def create_app(settings_override=None):
    app = Flask('panda_tracker', instance_relative_config=True)

    app.config.from_object('panda_tracker.settings')
    app.config.from_pyfile('config.py', silent=True)
    app.config.from_object(settings_override)

    logging.config.dictConfig(app.config['LOGGING'])

    # Set the default JSON encoder
    app.json_encoder = JSONEncoder

    mongo.init_app(app)
    jwt.init_app(app)

    root_package_path = os.path.dirname(__file__)
    register_blueprints(app, 'panda_tracker', root_package_path)

    app.errorhandler(ApplicationError)(application_error_handler)
    app.errorhandler(422)(handle_422)

    return app


def application_error_handler(error):
    return jsonify({
        'status_code': error.status_code,
        'error': error.error,
        'description': error.description,
    }), error.status_code


def handle_422(err):
    """This type of error is raised by webargs. Function copied from docs."""
    # webargs attaches additional metadata to the `data` attribute
    data = getattr(err, 'data')
    if data:
        # Get validations from the ValidationError object
        messages = data['exc'].messages
    else:
        messages = ['Invalid request']
    return jsonify({
        'messages': messages,
    }), 400
