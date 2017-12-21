# auth.py
# Created by abdularis on 08/10/17
import datetime

from flask import redirect, url_for, render_template, flash
from flask.views import View
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired

from unma.database import db_session
from unma.models import Admin
from unma.session import RedirectIfLogin, LoginRequired, SessionManager


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(message='Silakan masukan username')])
    password = PasswordField('Password', validators=[InputRequired(message='Silakan masukan password')])


class LoginView(View):
    methods = ['GET', 'POST']
    decorators = [RedirectIfLogin('admin.index')]

    def dispatch_request(self):
        form = LoginForm()
        if form.validate_on_submit():
            admin = db_session.query(Admin).filter(Admin.username == form.username.data).first()
            if admin and admin.verify_password(form.password.data):
                SessionManager.set_session(admin)
                admin.last_login = datetime.datetime.utcnow()
                db_session.commit()
                return redirect(url_for('admin.index'))
            flash("Username & password doesn't match!", category='err')
        return render_template('admin/login.html', title='Admin Login', form=form)


class LogoutView(View):
    decorators = [LoginRequired('admin.login')]

    def dispatch_request(self):
        SessionManager.clear_session()
        return redirect(url_for('admin.login'))
