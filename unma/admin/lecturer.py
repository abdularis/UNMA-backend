# lecturer.py
# Created by abdularis on 23/01/18

from flask import render_template, request, url_for
from flask.views import MethodView
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired

from unma.admin.wtformutil import UniqueValue, SwitchableRequired
from unma.common import decorate_function, CrudRouter
from unma.database import db_session
from unma.models import Lecturer
from unma.session import AdminRequired
from unma.ajaxutil import create_response, STAT_SUCCESS, STAT_ERROR, STAT_INVALID


render_template = decorate_function(render_template, page='lecturer', title='UNMA - Dosen')


class LecturerForm(FlaskForm):
    name = StringField('Nama',
                       validators=[InputRequired()])
    username = StringField('Username',
                           validators=[InputRequired(),
                                       UniqueValue(Lecturer, Lecturer.username, message="Username sudah ada. Tidak boleh sama!")])
    password = StringField('Password',
                           validators=[SwitchableRequired()])

    def __init__(self, edit_mode=False, last_value=None):
        super().__init__(csrf_enabled=False)
        UniqueValue.set_edit_mode_on_field(self.username, edit_mode, last_value)
        self.password.validators[0].enable = not edit_mode


def render_html_data_list():
    results = db_session.query(Lecturer).all()
    return render_template('admin/partials/lect/lecturer_list.html', objs=results)


def get_lecturer(lecturer_id):
    return db_session.query(Lecturer).filter(Lecturer.id == lecturer_id).first()


class CreateView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self):
        form = LecturerForm()
        return create_response(STAT_SUCCESS, html_form=self.render_form(form))

    def post(self):
        form = LecturerForm()
        if form.validate_on_submit():
            std = Lecturer()
            std.name = form.name.data
            std.username = form.username.data
            std.password = form.password.data
            db_session.add(std)
            db_session.commit()
            return create_response(STAT_SUCCESS, html_list=render_html_data_list())
        return create_response(STAT_INVALID, html_form=self.render_form(form))

    @staticmethod
    def render_form(form):
        return render_template(
            'admin/partials/lect/lecturer_form.html',
            form=form,
            form_title='Tambah akun mahasiswa',
            form_action=url_for('admin.lecturer_create'),
            form_id='newForm',
            btn_primary='Tambah')


class ReadView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self):
        if request.args.get('act') == 'list':
            return create_response(STAT_SUCCESS, html_list=render_html_data_list())
        return render_template('admin/lecturers.html')


class UpdateView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self, obj_id):
        model = get_lecturer(obj_id)
        if model:
            form = LecturerForm()
            form.name.data = model.name
            form.username.data = model.username
            form.password.render_kw = {'placeholder': 'Password disembunyikan!'}
            return create_response(STAT_SUCCESS, html_form=self.render_form(form, obj_id=obj_id))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    def post(self, obj_id):
        model = get_lecturer(obj_id)
        if model:
            form = LecturerForm(True, model.username)
            if form.validate_on_submit():
                model.name = form.name.data
                model.username = form.username.data
                if form.password.data:
                    model.password = form.password.data
                db_session.commit()
                return create_response(STAT_SUCCESS, html_list=render_html_data_list())
            return create_response(STAT_INVALID, html_form=self.render_form(form, obj_id=obj_id))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    @staticmethod
    def render_form(form, obj_id):
        return render_template(
            'admin/partials/lect/lecturer_form.html',
            form=form,
            form_title='Perbarui akun dosen',
            form_action=url_for('admin.lecturer_update', obj_id=obj_id),
            form_id='editForm',
            btn_primary='Perbarui')


class DeleteView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self, obj_id):
        model = get_lecturer(obj_id)
        if model:
            return create_response(STAT_SUCCESS,
                                   html_form=render_template('admin/partials/lect/lecturer_delete.html', obj=model))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    def post(self, obj_id):
        model = get_lecturer(obj_id)
        if model:
            db_session.delete(model)
            db_session.commit()
            return create_response(STAT_SUCCESS, html_list=render_html_data_list())
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))


CrudLecturer = CrudRouter(
    'lecturer', 'lecturers',
    CreateView,
    ReadView,
    UpdateView,
    DeleteView
)
