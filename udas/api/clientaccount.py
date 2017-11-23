# clientaccount.py
# Created by abdularis on 19/10/17

import datetime

from flask import request, g
from flask.views import MethodView
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired

from udas.database import db_session
from udas.models import Student, StudentToken
from .authutil import token_required, create_access_token
from .response import create_response, unauth_response


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired()])
    password = PasswordField(validators=[InputRequired()])
    fcm_token = StringField()

    def __init__(self):
        super().__init__(csrf_enabled=False)


class ClientAuthentication(MethodView):

    def post(self):
        form = LoginForm()
        if form.validate_on_submit():
            student = db_session.query(Student)\
                .filter(Student.username == form.username.data)\
                .first()

            if student and student.verify_password(form.password.data):
                token, payload = create_access_token(student.id, student.username)
                student.last_login = datetime.datetime.utcnow()

                stud_token = StudentToken()
                stud_token.student_id = student.id
                stud_token.acc_token = token
                stud_token.fcm_token = form.fcm_token.data
                db_session.query(StudentToken).filter(StudentToken.student_id == student.id).delete()
                db_session.add(stud_token)
                db_session.commit()

                data = {
                    'name': student.name,
                    'username': student.username,
                    'token': token,
                    'exp': payload['exp']
                }

                return create_response(True,
                                       message='Successfully logged in!',
                                       data=data)
        return create_response(False, message="Username and password doesn't match")

    @token_required
    def delete(self):
        db_session.query(StudentToken)\
            .filter(StudentToken.student_id == g.user_id, StudentToken.acc_token == g.user_token)\
            .delete()
        db_session.commit()
        return create_response(True, message='Successfully logged out')


class ClientProfile(MethodView):
    decorators = [token_required]

    def get(self):
        stud, stud_token = db_session.query(Student, StudentToken)\
            .filter(Student.id == g.user_id, StudentToken.acc_token == g.user_token)\
            .first()
        if stud and stud_token:
            data = {
                'name': stud.name,
                'username': stud.username,
                'fcm_token': stud_token.fcm_token,
                'recv_announce': len(stud.announcements),
                'class': {
                    'prog': stud.my_class.study.name,
                    'name': stud.my_class.name,
                    'year': stud.my_class.year,
                    'type': 'Reguler' if stud.my_class.type == 1 else 'Karyawan'
                }
            }
            return create_response(True, message='User account information', data=data)
        return create_response(False, s_code=404)

    def post(self):
        stud = db_session.query(Student).filter(Student.id == g.user_id).first()
        if stud and request.form.get('new_password') and request.form.get('old_password'):
            if stud.verify_password(request.form.get('old_password')):
                stud.password = request.form.get('new_password')
                db_session.commit()
                return create_response(True, message='Password updated', s_code=201)
            return unauth_response(message='Old password is wrong')
        return create_response(False, s_code=400)


class ClientToken(MethodView):
    decorators = [token_required]

    def get(self):
        return create_response(True, message='Firebase token', data={'fcm_token': g.user_fcm_token})

    def post(self):
        res = db_session.query(StudentToken).filter(StudentToken.student_id == g.user_id).first()
        if res and request.form.get('fcm_token'):
            res.fcm_token = request.form.get('fcm_token')
            db_session.commit()
            return create_response(True, message='Firebase token successfully updated')
        return create_response(False, s_code=400)
