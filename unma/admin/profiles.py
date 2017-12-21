# profiles.py
# Created by abdularis on 21/12/17

from flask import render_template, url_for, g, abort, redirect, flash
from flask.views import MethodView
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired

from unma.admin.wtformutil import UniqueValue
from unma.common import decorate_function
from unma.database import db_session
from unma.models import Admin
from unma.session import LoginRequired, SessionManager

render_template = decorate_function(render_template, page='profile', title='UNMA - Detail Profile')


class UpdatePasswordForm(FlaskForm):
    old_password = PasswordField('Password Lama', validators=[InputRequired()])
    new_password = PasswordField('Password Baru', validators=[InputRequired()])


class UpdateProfileInfoForm(FlaskForm):
    password = PasswordField('Verifikasi Password', validators=[InputRequired()])
    username = StringField('Username',
                           validators=[UniqueValue(Admin, Admin.username, message="Username sudah ada. Tidak boleh sama!")])
    name = StringField('Nama',
                       validators=[UniqueValue(Admin, Admin.name, message="Nama sudah ada. Tidak boleh sama!")])


class ProfileDetailViewModel:
    def __init__(self, admin_obj):
        self.name = admin_obj.name
        self.username = admin_obj.username
        self.password = admin_obj.password
        self.date_created = admin_obj.date_created
        self.last_login = admin_obj.last_login


class ProfileDetailView(MethodView):
    decorators = [LoginRequired('admin.login')]

    def get(self):
        return self.render_template()

    @staticmethod
    def render_template(form_update_password=None,
                        form_update_profile=None):
        admin = db_session.query(Admin).filter(Admin.username == g.curr_user.username).first()
        if admin:
            if not form_update_password: form_update_password = UpdatePasswordForm()
            if not form_update_profile: form_update_profile = UpdateProfileInfoForm()
            form_update_profile.name.render_kw = {'placeholder': admin.name}
            form_update_profile.username.render_kw = {'placeholder': admin.username}
            return render_template('admin/profile_detail.html',
                                   form_update_password=form_update_password,
                                   form_update_profile=form_update_profile,
                                   profile=ProfileDetailViewModel(admin))
        return abort(404)


class UpdatePasswordView(MethodView):
    decorators = [LoginRequired('admin.login')]

    def post(self):
        admin = db_session.query(Admin).filter(Admin.username == g.curr_user.username).first()
        if admin:
            form = UpdatePasswordForm()
            if form.validate_on_submit() and admin.verify_password(form.old_password.data):
                admin.password = form.new_password.data
                db_session.commit()

                flash("Password berhasil diupdate!", category='succ')
                return redirect(url_for('admin.profile_detail'))

            flash('Gagal mengupdate password baru!', category='warn')

            return ProfileDetailView.render_template(form_update_password=form)

        return abort(404)


class UpdateProfileInfoView(MethodView):
    decorators = [LoginRequired('admin.login')]

    def post(self):
        admin = db_session.query(Admin).filter(Admin.username == g.curr_user.username).first()
        if admin:
            form = UpdateProfileInfoForm()
            if form.validate_on_submit() and admin.verify_password(form.password.data):
                if form.name.data: admin.name = form.name.data
                if form.username.data: admin.username = form.username.data
                db_session.commit()

                SessionManager.set_session(admin)

                flash("Profile detail berhasil diupdate!", category='succ')
                return redirect(url_for('admin.profile_detail'))

            flash('Gagal mengupdate detail profile!', category='warn')
            return ProfileDetailView.render_template(form_update_profile=form)
        return abort(404)
