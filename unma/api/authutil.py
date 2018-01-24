# auth.py
# Created by abdularis on 19/10/17
import datetime
import functools
import jwt

from flask import request, g

from unma.unmaapp import app
from unma.database import db_session
from unma.models import StudentToken, LecturerToken
from .response import unauth_response


TOKEN_TYPE_FOR_STUDENT = 1
TOKEN_TYPE_FOR_LECTURER = 2


def create_access_token(user_id, username, token_type):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30),
        'iat': datetime.datetime.utcnow(),
        'uid': user_id,
        'unm': username,
        'typ': token_type
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
                    result = None
                    if payload.get('typ') == TOKEN_TYPE_FOR_STUDENT:
                        result = db_session.query(StudentToken) \
                            .filter(StudentToken.student_id == payload.get('uid'),
                                    StudentToken.acc_token == token).first()
                    elif payload.get('typ') == TOKEN_TYPE_FOR_LECTURER:
                        result = db_session.query(LecturerToken) \
                            .filter(LecturerToken.lecturer_id == payload.get('uid'),
                                    LecturerToken.acc_token == token).first()
                    if not result:
                        return unauth_response()

                    g.user_token = token
                    g.user_type = payload.get('typ')
                    g.user_id = payload.get('uid')
                    g.user_username = payload.get('unm')
                    g.user_fcm_token = result.fcm_token
                    return f(*args, **kwargs)
                except jwt.InvalidTokenError:
                    pass
        return unauth_response()

    return wrapper
