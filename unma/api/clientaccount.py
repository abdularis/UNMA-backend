# clientaccount.py
# Created by abdularis on 19/10/17

from flask import request, g
from flask.views import MethodView
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField
from wtforms.validators import InputRequired

from unma.common import time_now
from unma.database import db_session
from unma.models import Student, StudentToken, LecturerToken, Lecturer
from .authutil import token_required, create_access_token, TOKEN_TYPE_FOR_STUDENT, TOKEN_TYPE_FOR_LECTURER
from .response import create_response


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired()])
    password = PasswordField(validators=[InputRequired()])
    fcm_token = StringField()
    user_type = IntegerField(validators=[InputRequired()], default=TOKEN_TYPE_FOR_STUDENT)

    def __init__(self):
        super().__init__(csrf_enabled=False)


class UpdatePasswordForm(FlaskForm):
    old_password = PasswordField(validators=[InputRequired()])
    new_password = PasswordField(validators=[InputRequired()])
    fcm_token = StringField()

    def __init__(self):
        super().__init__(csrf_enabled=False)


def authorize_user(user, fcm_token, user_type):
    token, payload = create_access_token(user.id, user.username, user_type)
    user.last_login = time_now()

    if user_type == TOKEN_TYPE_FOR_STUDENT:
        stud_token = StudentToken()
        stud_token.student_id = user.id
        stud_token.acc_token = token
        stud_token.fcm_token = fcm_token
        db_session.query(StudentToken).filter(StudentToken.student_id == user.id).delete()
        db_session.add(stud_token)
    elif user_type == TOKEN_TYPE_FOR_LECTURER:
        lect_token = LecturerToken()
        lect_token.lecturer_id = user.id
        lect_token.acc_token = token
        lect_token.fcm_token = fcm_token
        db_session.query(LecturerToken).filter(LecturerToken.lecturer_id == user.id).delete()
        db_session.add(lect_token)
    db_session.commit()

    data = {
        'name': user.name,
        'username': user.username,
        'token': token,
        'exp': payload['exp']
    }
    return data


class ClientAuthentication(MethodView):

    def post(self):
        form = LoginForm()
        if form.validate_on_submit():
            user = None
            if form.user_type.data == TOKEN_TYPE_FOR_STUDENT:
                user = db_session.query(Student)\
                    .filter(Student.username == form.username.data)\
                    .first()
            elif form.user_type.data == TOKEN_TYPE_FOR_LECTURER:
                user = db_session.query(Lecturer)\
                    .filter(Lecturer.username == form.username.data)\
                    .first()

            if user and user.verify_password(form.password.data):
                data = authorize_user(user, form.fcm_token.data, form.user_type.data)
                return create_response(True,
                                       message='Successfully logged in!',
                                       data=data)
        return create_response(False, message="Username and password doesn't match")

    @token_required
    def delete(self):
        if g.user_type == TOKEN_TYPE_FOR_STUDENT:
            db_session.query(StudentToken) \
                .filter(StudentToken.student_id == g.user_id, StudentToken.acc_token == g.user_token) \
                .delete()
        elif g.user_type == TOKEN_TYPE_FOR_LECTURER:
            db_session.query(LecturerToken) \
                .filter(LecturerToken.lecturer_id == g.user_id, LecturerToken.acc_token == g.user_token) \
                .delete()
        db_session.commit()
        return create_response(True, message='Successfully logged out')


class ClientProfile(MethodView):
    decorators = [token_required]

    def get(self):
        data = None
        if g.user_type == TOKEN_TYPE_FOR_STUDENT:
            stud, stud_token = db_session.query(Student, StudentToken)\
                .filter(Student.id == g.user_id, StudentToken.acc_token == g.user_token)\
                .first()
            if stud and stud_token:
                data = {
                    'type': g.user_type,
                    'name': stud.name,
                    'username': stud.username,
                    'fcm_token': stud_token.fcm_token,
                    'class': {
                        'prog': stud.my_class.department.name,
                        'name': stud.my_class.name,
                        'year': stud.my_class.year,
                        'type': 'Reguler' if stud.my_class.type == 1 else 'Karyawan'
                    }
                }
        elif g.user_type == TOKEN_TYPE_FOR_LECTURER:
            lect, lect_token = db_session.query(Lecturer, LecturerToken)\
                .filter(Lecturer.id == g.user_id, LecturerToken.acc_token == g.user_token)\
                .first()
            if lect and lect_token:
                data = {
                    'type': g.user_type,
                    'name': lect.name,
                    'username': lect.username,
                    'fcm_token': lect_token.fcm_token
                }
        return create_response(True, message='User account information', data=data)
        # return create_response(False, s_code=404)

    def post(self):
        form = UpdatePasswordForm()
        if form.validate_on_submit():
            user = None
            if g.user_type == TOKEN_TYPE_FOR_STUDENT:
                user = db_session.query(Student).filter(Student.id == g.user_id).first()
            elif g.user_type == TOKEN_TYPE_FOR_LECTURER:
                user = db_session.query(Lecturer).filter(Lecturer.id == g.user_id).first()
            if user:
                if user.verify_password(form.old_password.data):
                    user.password = form.new_password.data
                    db_session.commit()
                    data = authorize_user(user, form.fcm_token.data, g.user_type)
                    return create_response(True, message='Password updated', data=data, s_code=201)
                return create_response(False, message='Old password is wrong')
        return create_response(False, s_code=400)


class ClientToken(MethodView):
    decorators = [token_required]

    def get(self):
        return create_response(True, message='Firebase token', data={'fcm_token': g.user_fcm_token})

    def post(self):
        if g.user_type == TOKEN_TYPE_FOR_STUDENT:
            res = db_session.query(StudentToken).filter(StudentToken.student_id == g.user_id).first()
        else:
            res = db_session.query(LecturerToken).filter(LecturerToken.student_id == g.user_id).first()
        if res and request.form.get('fcm_token'):
            res.fcm_token = request.form.get('fcm_token')
            db_session.commit()
            return create_response(True, message='Firebase token successfully updated')
        return create_response(False, s_code=400)
