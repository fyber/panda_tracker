from flask import Blueprint
from flask_jwt import jwt_required, current_identity

from ..core import route

bp = Blueprint('events', __name__, url_prefix='/events')


@route(bp, '/')
@jwt_required()
def index():
    return {'msg': 'Привет, {}!'.format(current_identity)}
