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
