# study.py
# Created by abdularis on 18/10/17

from flask import render_template, request, url_for

from udas.database import db_session
from udas.models import Class
from udas.login import AdminRequired
from udas.crud import Crud, BaseCreateView, BaseReadView, BaseUpdateView, BaseDeleteView
from udas.forms import ClassForm
from udas.decorator import decorate_function


render_template = decorate_function(render_template, page='class')


def render_html_data_list():
    results = db_session.query(Class).all()
    return render_template('admin/partials/cls/class_list.html', objs=results)


class CreateView(BaseCreateView):
    decorators = [AdminRequired('admin.login')]

    def __init__(self):
        super().__init__(render_html_data_list)

    def create_form(self, method):
        return ClassForm(request.form) if method == 'POST' else ClassForm()

    def save_form(self, form):
        cls = Class()
        cls.study_id = form.study_program.data
        cls.name = form.name.data
        cls.year = form.year.data
        cls.type = form.cls_type.data
        db_session.add(cls)
        db_session.commit()
        return True, None

    def render_form(self, form):
        return render_template(
            'admin/partials/cls/class_form.html',
            form=form,
            form_title='Tambah data kelas baru',
            form_action=url_for('admin.class_create'),
            form_id='newForm',
            btn_primary='Tambah')


class ReadView(BaseReadView):
    decorators = [AdminRequired('admin.login')]

    def __init__(self):
        super().__init__(disable_detail_view=True)

    def render_list(self):
        return render_html_data_list()

    def render_container(self):
        return render_template('admin/classes.html')


class UpdateView(BaseUpdateView):
    decorators = [AdminRequired('admin.login')]

    def __init__(self):
        super().__init__(render_html_data_list)

    def get_model(self, obj_id):
        return db_session.query(Class).get(obj_id)

    def modify_model(self, form, model):
        model.study_id = form.study_program.data
        model.name = form.name.data
        model.year = form.year.data
        model.type = form.cls_type.data
        db_session.commit()
        return True, None

    def create_form(self, method, model):
        if method == 'GET':
            form = ClassForm()
            form.study_program.data = model.study_id
            form.name.data = model.name
            form.year.data = model.year
            form.cls_type.data = model.type
            return form
        else:
            return ClassForm(request.form)

    def render_form(self, form, obj_id):
        return render_template(
            'admin/partials/cls/class_form.html',
            form=form,
            form_title='Perbarui data kelas',
            form_action=url_for('admin.class_update', obj_id=obj_id),
            form_id='editForm',
            btn_primary='Perbarui')


class DeleteView(BaseDeleteView):
    decorators = [AdminRequired('admin.login')]

    def __init__(self):
        super().__init__(render_html_data_list)

    def get_model(self, obj_id):
        return db_session.query(Class).get(obj_id)

    def delete_model(self, model):
        db_session.delete(model)
        db_session.commit()
        return True, None

    def render_delete_form(self, model):
        return render_template('admin/partials/cls/class_delete.html', obj=model)


CrudClass = Crud(
    'class', 'classes',
    CreateView,
    ReadView,
    UpdateView,
    DeleteView
)
