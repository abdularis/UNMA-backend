# students.py
# Created by abdularis on 18/10/17

from flask import render_template, request, url_for
from flask.views import MethodView

from udas.database import db_session
from udas.models import Student
from udas.login import AdminRequired
from udas.crud import Crud, BaseCreateView, Interceptor, BaseReadView, BaseUpdateView, BaseDeleteView
from udas.forms import StudentForm
from udas.ajaxutil import create_response, STAT_SUCCESS, STAT_ERROR, STAT_INVALID
from udas.decorator import decorate_function


render_template = decorate_function(render_template, page='student')


def render_html_data_list():
    results = db_session.query(Student).all()
    return render_template('admin/partials/std/student_list.html', objs=results)


class _CreateView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self):
        if request.args.get('act') == 'cls':
            return self._get_classes_options(int(request.args.get('sp')))
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
    def _get_classes_options(study_program_id=None):
        res = StudentForm.get_classes_option(study_program_id)
        if res:
            html_select_options = \
                render_template('admin/partials/std/class_options.html', objs=res)
            return create_response(STAT_SUCCESS,
                                   html_extra=html_select_options)
        return create_response(STAT_ERROR)

    @staticmethod
    def render_form(form):
        return render_template(
            'admin/partials/std/student_form.html',
            form=form,
            form_title='Tambah akun mahasiswa',
            form_action=url_for('admin.student_create'),
            form_id='newForm',
            btn_primary='Tambah')


class _ReadView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self):
        if request.args.get('act') == 'list':
            return create_response(STAT_SUCCESS, html_list=render_html_data_list())
        return render_template('admin/students.html')


class _UpdateView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self, obj_id):
        model = self.get_student(obj_id)
        if model:
            form = StudentForm()
            form.name.data = model.name
            form.username.data = model.username
            form.password.render_kw = {'placeholder': 'Password disembunyikan!'}
            form.std_class.data = model.class_id
            form.study_program.data = model.my_class.study.id
            return create_response(STAT_SUCCESS, html_form=self.render_form(form, obj_id=obj_id))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    def post(self, obj_id):
        model = self.get_student(obj_id)
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
    def get_student(student_id):
        return db_session.query(Student).filter(Student.id == student_id).first()

    @staticmethod
    def render_form(form, obj_id):
        return render_template(
            'admin/partials/std/student_form.html',
            form=form,
            form_title='Perbarui akun mahasiswa',
            form_action=url_for('admin.student_update', obj_id=obj_id),
            form_id='editForm',
            btn_primary='Perbarui')


class _DeleteView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self, obj_id):
        model = self.get_student(obj_id)
        if model:
            return create_response(STAT_SUCCESS,
                                   html_form=render_template('admin/partials/std/student_delete.html', obj=model))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    def post(self, obj_id):
        model = self.get_student(obj_id)
        if model:
            db_session.delete(model)
            db_session.commit()
            return create_response(STAT_SUCCESS, html_list=render_html_data_list())
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    @staticmethod
    def get_student(student_id):
        return db_session.query(Student).filter(Student.id == student_id).first()


CrudStudent = Crud(
    'student', 'students',
    _CreateView,
    _ReadView,
    _UpdateView,
    _DeleteView
)
