from functools import wraps
from werkzeug.wrappers import Response
from flask import jsonify
from flask.ext.pymongo import PyMongo
from flask_jwt import JWT

mongo = PyMongo()
jwt = JWT()


class ApplicationError(Exception):
    def __init__(self, error, description, status_code=500):
        self.error = error
        self.description = description
        self.status_code = status_code

    def __repr__(self):
        return self.error


class InputError(ApplicationError):
    def __init__(self, description):
        super().__init__('InputError', description, 400)


def route(bp, *args, **kwargs):
    """Almost like standard `route`, but with modified defaults and adds few
    nice features. For example any value returned by decorated view function
    will be converted to json unless force_json is set to False.
    """
    kwargs.setdefault('strict_slashes', False)
    force_json = kwargs.pop('force_json', True)
    output_schema = kwargs.pop('output_schema', None)

    def bp_router(f):
        @bp.route(*args, **kwargs)
        @wraps(f)
        def view_func_wrapper(*args, **kwargs):

            sc = 200
            rv = f(*args, **kwargs)
            if isinstance(rv, tuple):
                sc = rv[1]
                rv = rv[0]

            if output_schema:
                rv = output_schema.dump(rv).data

            if isinstance(rv, Response):
                return rv
            elif force_json:
                return jsonify(rv), sc
            else:
                return rv, sc

        return view_func_wrapper

    return bp_router
