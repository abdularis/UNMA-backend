# students.py
# Created by abdularis on 18/10/17

from flask import render_template, request, url_for

from udas.database import db_session
from udas.models import Student
from udas.login import AdminRequired
from udas.crud import Crud, BaseCreateView, Interceptor, BaseReadView, BaseUpdateView, BaseDeleteView
from udas.forms import StudentForm
from udas.ajaxutil import create_response, STAT_SUCCESS, STAT_ERROR
from udas.decorator import decorate_function


render_template = decorate_function(render_template, page='student')


def render_html_data_list():
    results = db_session.query(Student).all()
    return render_template('admin/partials/std/student_list.html', objs=results)


class CreateView(BaseCreateView):
    decorators = [AdminRequired('admin.login')]

    def __init__(self):
        super().__init__(render_html_data_list,
                         get_interceptor=Interceptor(self.intercept_get))

    def _get_classes_options(self, study_program_id=None):
        res = StudentForm.get_classes_option(study_program_id)
        if res:
            html_select_options = \
                render_template('admin/partials/std/class_options.html', objs=res)
            return create_response(STAT_SUCCESS,
                                   html_extra=html_select_options)
        return create_response(STAT_ERROR)

    def intercept_get(self):
        if request.args.get('act') == 'cls':
            return False, self._get_classes_options(int(request.args.get('sp')))
        return True, None

    def save_form(self, form):
        std = Student()
        std.name = form.name.data
        std.username = form.username.data
        std.password = form.password.data
        std.class_id = form.std_class.data
        db_session.add(std)
        db_session.commit()
        return True, None

    def render_form(self, form):
        return render_template(
            'admin/partials/std/student_form.html',
            form=form,
            form_title='Tambah akun mahasiswa',
            form_action=url_for('admin.student_create'),
            form_id='newForm',
            btn_primary='Tambah')

    def create_form(self, method):
        return StudentForm(request.form) if method == 'POST' else StudentForm()


class ReadView(BaseReadView):
    decorators = [AdminRequired('admin.login')]

    def __init__(self):
        super().__init__(disable_detail_view=True)

    def render_list(self):
        return render_html_data_list()

    def render_container(self):
        return render_template('admin/students.html')


class UpdateView(BaseUpdateView):
    decorators = [AdminRequired('admin.login')]

    def __init__(self):
        super().__init__(render_html_data_list)

    def render_form(self, form, obj_id):
        return render_template(
            'admin/partials/std/student_form.html',
            form=form,
            form_title='Perbarui akun mahasiswa',
            form_action=url_for('admin.student_update', obj_id=obj_id),
            form_id='editForm',
            btn_primary='Perbarui')

    def modify_model(self, form, model):
        model.name = form.name.data
        model.username = form.username.data
        model.class_id = form.std_class.data
        if form.password.data:
            model.password = form.password.data
        db_session.commit()
        return True, None

    def create_form(self, method, model):
        if method == 'GET':
            form = StudentForm()
            form.name.data = model.name
            form.username.data = model.username
            form.password.render_kw = {'placeholder': 'Password disembunyikan!'}
            form.std_class.data = model.class_id
            form.study_program.data = model.my_class.study.id
            return form
        else:
            return StudentForm(request.form, True, model.username)

    def get_model(self, obj_id):
        return db_session.query(Student).get(obj_id)


class DeleteView(BaseDeleteView):
    decorators = [AdminRequired('admin.login')]

    def __init__(self):
        super().__init__(render_html_data_list)

    def get_model(self, obj_id):
        return db_session.query(Student).get(obj_id)

    def delete_model(self, model):
        db_session.delete(model)
        db_session.commit()
        return True, None

    def render_delete_form(self, model):
        return render_template('admin/partials/std/student_delete.html', obj=model)


CrudStudent = Crud(
    'student', 'students',
    CreateView,
    ReadView,
    UpdateView,
    DeleteView
)
