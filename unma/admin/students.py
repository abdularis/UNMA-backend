# students.py
# Created by abdularis on 18/10/17

from flask import render_template, request, url_for
from flask.views import MethodView
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import InputRequired

from unma.admin.wtformutil import UniqueValue, SwitchableRequired
from unma.common import decorate_function, CrudRouter
from unma.database import db_session
from unma.models import Student, Class, Department
from unma.session import AdminRequired
from unma.ajaxutil import create_response, STAT_SUCCESS, STAT_ERROR, STAT_INVALID


render_template = decorate_function(render_template, page='student', title='UNMA - Mahasiswa')


class StudentForm(FlaskForm):
    name = StringField('Nama',
                       validators=[InputRequired()])
    department = SelectField('Prodi',
                             coerce=int,
                             choices=[])
    std_class = SelectField('Kelas',
                            validators=[InputRequired()],
                            coerce=int,
                            choices=[])
    username = StringField('Username',
                           validators=[InputRequired(),
                                       UniqueValue(Student, Student.username, message="Username sudah ada. Tidak boleh sama!")])
    password = StringField('Password',
                           validators=[SwitchableRequired()])

    def __init__(self, edit_mode=False, last_value=None):
        super().__init__(csrf_enabled=False)
        self.department.data = 0
        self.department.choices = self.get_department_option()
        self.std_class.choices = self.get_classes_option()

        UniqueValue.set_edit_mode_on_field(self.username, edit_mode, last_value)
        self.password.validators[0].enable = not edit_mode

    @staticmethod
    def get_department_option():
        choices = [(0, '--- program studi ---')]
        [choices.append((obj.id, obj.name)) for obj in db_session.query(Department).all()]
        return choices

    @staticmethod
    def get_classes_option(sp_id=None):
        if sp_id and sp_id > 0:
            res = db_session.query(Class)\
                .filter(Class.department_id == sp_id)\
                .order_by(Class.department_id.asc())\
                .all()
        else:
            res = db_session.query(Class).order_by(Class.department_id.asc()).all()
        return [(obj.id, str(obj)) for obj in res]


def render_html_data_list():
    results = db_session.query(Student).all()
    return render_template('admin/partials/std/student_list.html', objs=results)


def get_student(student_id):
    return db_session.query(Student).filter(Student.id == student_id).first()


class CreateView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self):
        form = StudentForm()
        return create_response(STAT_SUCCESS, html_form=self.render_form(form))

    def post(self):
        form = StudentForm()
        if form.validate_on_submit():
            std = Student()
            std.name = form.name.data
            std.username = form.username.data
            std.password = form.password.data
            std.class_id = form.std_class.data
            db_session.add(std)
            db_session.commit()
            return create_response(STAT_SUCCESS, html_list=render_html_data_list())
        return create_response(STAT_INVALID, html_form=self.render_form(form))

    @staticmethod
    def render_form(form):
        res = db_session.query(Class).order_by(Class.department_id.asc()).all()
        return render_template(
            'admin/partials/std/student_form.html',
            form=form,
            form_title='Tambah akun mahasiswa',
            form_action=url_for('admin.student_create'),
            form_id='newForm',
            btn_primary='Tambah',
            classes=res)


class ReadView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self):
        if request.args.get('act') == 'list':
            return create_response(STAT_SUCCESS, html_list=render_html_data_list())
        return render_template('admin/students.html')


class UpdateView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self, obj_id):
        model = get_student(obj_id)
        if model:
            form = StudentForm()
            form.name.data = model.name
            form.username.data = model.username
            form.password.render_kw = {'placeholder': 'Password disembunyikan!'}
            form.std_class.data = model.class_id
            form.department.data = model.my_class.department.id
            return create_response(STAT_SUCCESS, html_form=self.render_form(form, obj_id=obj_id))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    def post(self, obj_id):
        model = get_student(obj_id)
        if model:
            form = StudentForm(True, model.username)
            if form.validate_on_submit():
                model.name = form.name.data
                model.username = form.username.data
                model.class_id = form.std_class.data
                if form.password.data:
                    model.password = form.password.data
                db_session.commit()
                return create_response(STAT_SUCCESS, html_list=render_html_data_list())
            return create_response(STAT_INVALID, html_form=self.render_form(form, obj_id=obj_id))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    @staticmethod
    def render_form(form, obj_id):
        return render_template(
            'admin/partials/std/student_form.html',
            form=form,
            form_title='Perbarui akun mahasiswa',
            form_action=url_for('admin.student_update', obj_id=obj_id),
            form_id='editForm',
            btn_primary='Perbarui')


class DeleteView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self, obj_id):
        model = get_student(obj_id)
        if model:
            return create_response(STAT_SUCCESS,
                                   html_form=render_template('admin/partials/std/student_delete.html', obj=model))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    def post(self, obj_id):
        model = get_student(obj_id)
        if model:
            db_session.delete(model)
            db_session.commit()
            return create_response(STAT_SUCCESS, html_list=render_html_data_list())
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))


CrudStudent = CrudRouter(
    'student', 'students',
    CreateView,
    ReadView,
    UpdateView,
    DeleteView
)
