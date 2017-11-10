# auth.py
# Created by abdularis on 08/10/17

from flask import request, redirect, url_for, render_template
from flask.views import View

from udas.repofactory import rf
from udas.forms import LoginForm
from udas.login import RedirectIfLogin, LoginRequired, SessionManager


class LoginView(View):
    methods = ['GET', 'POST']
    decorators = [RedirectIfLogin('admin.index')]

    def dispatch_request(self):
        form = LoginForm(request.form)
        if request.method == 'POST' and form.validate():
            admin = rf.admin_repo().check_for_account(form.username.data, form.password.data)
            if admin:
                SessionManager.set_session(admin)
                return redirect(url_for('admin.index'))
        return render_template('admin/login.html', title='Admin Login', form=form)


class LogoutView(View):
    decorators = [LoginRequired('admin.login')]

    def dispatch_request(self):
        SessionManager.clear_session()
        return redirect(url_for('admin.login'))
