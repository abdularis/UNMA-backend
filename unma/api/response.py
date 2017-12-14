# apiutils.py
# Created by abdularis on 19/10/17

from flask import jsonify, make_response


def create_response(success, message='', data=None, s_code=200):
    json = jsonify(success=success, message=message, data=data) if data\
        else jsonify(success=success, message=message)
    return make_response(json, s_code)


def unauth_response(message="Unauthorized access"):
    return create_response(False, message, s_code=401)


def bad_response(message="Bad request"):
    return create_response(False, message=message, s_code=400)
