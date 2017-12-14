# department.py
# Created by abdularis on 15/10/17

from flask import render_template, request, url_for
from flask.views import MethodView
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired

from unma.admin.wtformutil import UniqueValue
from unma.ajaxutil import STAT_SUCCESS, create_response, STAT_ERROR, STAT_INVALID
from unma.common import decorate_function, CrudRouter
from unma.database import db_session
from unma.models import Department
from unma.session import AdminRequired


render_template = decorate_function(render_template, page='department')


class DepartmentForm(FlaskForm):

    name = StringField('Nama',
                       validators=[InputRequired(message="Nama tidak boleh kosong"),
                                   UniqueValue(Department, Department.name, message="Nama sudah ada. Tidak boleh sama!")])

    def __init__(self, edit_mode=False, last_value=''):
        super().__init__(csrf_enabled=False)
        UniqueValue.set_edit_mode_on_field(self.name, edit_mode, last_value)


def get_data_list():
    results = db_session.query(Department).order_by(Department.id.desc()).all()
    for res in results:
        res.classes_count = len(res.classes)
    return results


def render_html_data_list():
    return render_template('admin/partials/dept/department_list.html', objs=get_data_list())


def get_department(obj_id):
    return db_session.query(Department).filter(Department.id == obj_id).first()


class _CreateView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self):
        form = DepartmentForm()
        return create_response(STAT_SUCCESS, html_form=self.render_form(form))

    def post(self):
        form = DepartmentForm()
        if form.validate_on_submit():
            std = Department()
            std.name = form.name.data
            db_session.add(std)
            db_session.commit()
            return create_response(STAT_SUCCESS, html_list=render_html_data_list())
        return create_response(STAT_INVALID, html_form=self.render_form(form))

    @staticmethod
    def render_form(form):
        return render_template(
            'admin/partials/dept/department_form.html',
            form=form,
            form_title='Tambah data program studi baru',
            form_action=url_for('admin.department_create'),
            form_id='newForm',
            btn_primary='Tambah')


class _ReadView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self):
        if request.args.get('act') == 'list':
            html_list = render_html_data_list()
            return create_response(STAT_SUCCESS, html_list=html_list)
        return render_template('admin/departments.html')


class _UpdateView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self, obj_id):
        model = get_department(obj_id)
        if model:
            form = DepartmentForm()
            form.name.data = model.name
            return create_response(STAT_SUCCESS, html_form=self.render_form(form, obj_id=obj_id))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    def post(self, obj_id):
        model = get_department(obj_id)
        if model:
            form = DepartmentForm(True, model.name)
            if form.validate_on_submit():
                model.name = form.name.data
                db_session.commit()
                return create_response(STAT_SUCCESS, html_list=render_html_data_list())
            return create_response(STAT_INVALID, html_form=self.render_form(form, obj_id=obj_id))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    @staticmethod
    def render_form(form, obj_id):
        return render_template(
            'admin/partials/dept/department_form.html',
            form=form,
            form_title='Perbarui data program studi',
            form_action=url_for('admin.department_update', obj_id=obj_id),
            form_id='editForm',
            btn_primary='Perbarui')


class _DeleteView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self, obj_id):
        model = get_department(obj_id)
        if model:
            return create_response(STAT_SUCCESS,
                                   html_form=render_template('admin/partials/dept/department_delete.html', obj=model))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    def post(self, obj_id):
        model = get_department(obj_id)
        if model:
            db_session.delete(model)
            db_session.commit()
            return create_response(STAT_SUCCESS, html_list=render_html_data_list())
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))


CrudDepartment = CrudRouter(
    'department', 'departments',
    _CreateView,
    _ReadView,
    _UpdateView,
    _DeleteView
)
