from datetime import datetime
from flask import Blueprint, request, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from ..core import jwt, mongo, InputError


@jwt.authentication_handler
def authenticate(username, password):
    user = mongo.db.users.find_one({'username': username})
    if not user:
        raise InputError('User {} not registered'.format(username))

    if not check_password_hash(user['pwhash'], password):
        raise InputError('Invalid password')

    return str(user['_id'])


@jwt.identity_handler
def identify(payload):
    """If we are here, token verification was successful.
    Do not load actual user model from mongo, as it's not always required.
    This can help us save few RPS on mongo reads.
    """
    return payload['identity']


@jwt.jwt_payload_handler
def jwt_payload_handler(identity):
    """Mostly copied from Flask-JWT._default_jwt_payload_handler() but adapted
    to support different meaning of identity parameter."""
    iat = datetime.utcnow()
    exp = iat + current_app.config.get('JWT_EXPIRATION_DELTA')
    nbf = iat + current_app.config.get('JWT_NOT_BEFORE_DELTA')
    return {'exp': exp, 'iat': iat, 'nbf': nbf, 'identity': identity}


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=('POST',))
def login():
    """Define auth endpoint here as /auth/login instead of Flask-JWT's default
    /auth."""
    return jwt.auth_request_callback()


@bp.route('/signup', methods=('POST',))
def signup():
    """Create new user from login/password pair."""
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if mongo.db.users.find_one({'username': username}):
        raise InputError('User {} already registered'.format(username))

    new_user_id = mongo.db.users.insert(
        {'username': username, 'pwhash': generate_password_hash(password)})

    identity = str(new_user_id)
    access_token = jwt.jwt_encode_callback(identity)
    return jwt.auth_response_callback(access_token, identity)
