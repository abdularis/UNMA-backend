# auth.py
# Created by abdularis on 19/10/17
import datetime
import functools
import jwt

from flask import request, g

from udas import app
from udas.database import db_session
from udas.models import StudentToken
from .response import unauth_response


def create_access_token(user_id, username):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30),
        'iat': datetime.datetime.utcnow(),
        'uid': user_id,
        'unm': username
    }
    token = jwt.encode(payload, app.config.get('SECRET_KEY')).decode('utf-8')
    return token, payload


def token_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        # Authorization: key=<access token>
        auth_key_pair = request.headers.get('Authorization')
        if auth_key_pair:
            auth_key_pair = auth_key_pair.split('=', 1)
            if len(auth_key_pair) >= 2 and auth_key_pair[0].lower() == 'key':
                try:
                    token = auth_key_pair[1]
                    payload = jwt.decode(token, app.config.get('SECRET_KEY'))
                    result = db_session.query(StudentToken) \
                        .filter(StudentToken.student_id == payload.get('uid'),
                                StudentToken.acc_token == token).first()
                    if not result:
                        return unauth_response()

                    g.user_token = token
                    g.user_id = payload.get('uid')
                    g.user_username = payload.get('unm')
                    g.user_fcm_token = result.fcm_token
                    return f(*args, **kwargs)
                except jwt.InvalidTokenError:
                    pass
        return unauth_response()

    return wrapper
