from os.path import join
import pkgutil
import importlib
import logging
from flask import Blueprint


def register_blueprints(app, package_name, package_path):
    """Register all Blueprint instances on the specified Flask application found
    in all modules for the specified package.

    :param app: the Flask application
    :param package_name: the package name
    :param package_path: the package path
    """
    rv = []
    for _, name, ispkg in pkgutil.walk_packages([package_path]):
        if ispkg:
            register_blueprints(app, '{}.{}'.format(package_name, name),
                                join(package_path, name))

        m = importlib.import_module('%s.%s' % (package_name, name))
        for item in dir(m):
            item = getattr(m, item)
            if isinstance(item, Blueprint):
                app.register_blueprint(item)
            rv.append(item)
    return rv


def configure_logging(app):
    if app.debug:
        app.config['LOGGING']['loggers']['']['handlers'].append('console')

    logging.config.dictConfig(app.config['LOGGING'])
