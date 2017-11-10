# auth.py
# Created by abdularis on 08/10/17

from flask import request, redirect, url_for, render_template
from flask.views import View

from udas.database import db_session
from udas.models import Admin
from udas.forms import LoginForm
from udas.login import RedirectIfLogin, LoginRequired, LoginManager


class LoginView(View):
    methods = ['GET', 'POST']
    decorators = [RedirectIfLogin('admin.index')]

    def dispatch_request(self):
        form = LoginForm(request.form)
        if request.method == 'POST' and form.validate():
            if LoginManager.login(self._get_account, self._verify_account,
                                  form.username.data, form.password.data):
                return redirect(url_for('admin.index'))
        return render_template('admin/login.html', title='Admin Login', form=form)

    @staticmethod
    def _get_account(account_id):
        """account_id berdasarkan pada username dan password
           yang diberikan pada LoginManager.login()"""

        return db_session.query(Admin)\
            .filter(Admin.username == account_id).first()

    @staticmethod
    def _verify_account(account, password):
        success = account.verify_password(password)
        return {'success': success,
                'is_admin': True if account.role == 'ADM' and success else False}


class LogoutView(View):
    decorators = [LoginRequired('admin.login')]

    def dispatch_request(self):
        LoginManager.logout()
        return redirect(url_for('admin.login'))
