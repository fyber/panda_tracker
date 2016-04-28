from flask import Blueprint
from flask_jwt import jwt_required, current_identity

bp = Blueprint('events', __name__, url_prefix='/events')


@bp.route('/')
@jwt_required()
def index():
    return 'Привет, {}!'.format(current_identity)
