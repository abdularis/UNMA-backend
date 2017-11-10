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


class LoginManager:

    @staticmethod
    def login(account_getter, account_verifier, account_id, password):
        """
        Do login

        :param account_getter: callable object untuk mendapatkan account berdasarkan account_id
        :param account_verifier: callable object untuk verifikasi account yang telah didapatkan
                                    dari account_getter dan return dictionary
                                    {'success': True | False, 'is_admin'= True | False}
        :param account_id: unique identifier untuk account yang akan diambil dari callable account_getter
        :param password: password associated with account_id
        :return: True if login success False otherwise
        """

        if callable(account_getter) and callable(account_verifier):
            account = account_getter(account_id)
            if account:
                result = account_verifier(account, password)
                if result.get('success'):
                    is_admin = bool(result.get('is_admin'))
                    session[_sv_is_login] = True
                    session[_sv_is_admin] = is_admin
                    session[_sv_user_id] = account_id
                    _populates_global_var()
                    return True
        return False

    @staticmethod
    def logout():
        if not session[_sv_is_login]:
            return False
        session.pop(_sv_is_login, None)
        session.pop(_sv_is_admin, None)
        session.pop(_sv_user_id, None)
        return True
