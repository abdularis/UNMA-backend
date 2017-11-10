# login.py
# Created by abdularis on 08/10/17

import functools

from flask import session, redirect, url_for, g

_sv_is_login = 'is_user_login'
_sv_is_admin = 'is_admin'
_sv_user_id = 'user_id'


def _populates_global_var():
    g.is_login = bool(session.get(_sv_is_login))
    g.is_admin = bool(session.get(_sv_is_admin))
    g.curr_user = session.get(_sv_user_id)


class ParamDecorator:
    """
    Base decorator untuk decorator berparameter (parameterized decorator)
    """

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return self._do(func, *args, **kwargs)
        return wrapper

    def _do(self, func, *args, **kwargs):
        return None


class RedirectIfLogin(ParamDecorator):
    """
    Redirect ke @redirect_to endpoint jika user telah login
    """

    def __init__(self, redirect_to, admin=False):
        self.redirect_to = redirect_to
        self.admin = admin

    def _do(self, func, *args, **kwargs):
        if self.admin:
            if session.get(_sv_is_login) and session.get(_sv_is_admin):
                return redirect(url_for(self.redirect_to))
        elif session.get(_sv_is_login):
            return redirect(url_for(self.redirect_to))
        return func(*args, **kwargs)


class LoginRequired(ParamDecorator):
    """
    Redirect ke @redirect_failed endpoint jika user belum login
    """

    def __init__(self, redirect_failed):
        self.redirect_failed = redirect_failed

    def _do(self, func, *args, **kwargs):
        if session.get(_sv_is_login):
            _populates_global_var()
            return func(*args, **kwargs)
        else:
            return redirect(url_for(self.redirect_failed))


class AdminRequired(ParamDecorator):
    """
    Redirect ke @redirect_failed endpoint jika bukan admin yang login
    """

    def __init__(self, redirect_failed):
        self.redirect_failed = redirect_failed

    def _do(self, func, *args, **kwargs):
        if session.get(_sv_is_login) and session.get(_sv_is_admin):
            _populates_global_var()
            return func(*args, **kwargs)
        else:
            return redirect(url_for(self.redirect_failed))


class SessionManager:

    @staticmethod
    def set_session(admin):
        session[_sv_is_login] = True
        session[_sv_is_admin] = bool(admin.role == 'ADM')
        session[_sv_user_id] = admin.username
        _populates_global_var()

    @staticmethod
    def clear_session():
        if not session[_sv_is_login]:
            return False
        session.pop(_sv_is_login, None)
        session.pop(_sv_is_admin, None)
        session.pop(_sv_user_id, None)
        return True
