# study.py
# Created by abdularis on 18/10/17

from flask import render_template, request, url_for
from flask.views import MethodView

from udas.ajaxutil import create_response, STAT_SUCCESS, STAT_INVALID, STAT_ERROR
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


class _CreateView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self):
        form = ClassForm()
        return create_response(STAT_SUCCESS, html_form=self.render_form(form))

    def post(self):
        form = ClassForm()
        if form.validate_on_submit():
            cls = Class()
            cls.study_id = form.study_program.data
            cls.name = form.name.data
            cls.year = form.year.data
            cls.type = form.cls_type.data
            db_session.add(cls)
            db_session.commit()
            return create_response(STAT_SUCCESS, html_list=render_html_data_list())
        return create_response(STAT_INVALID, html_form=self.render_form(form))

    @staticmethod
    def render_form(form):
        return render_template(
            'admin/partials/cls/class_form.html',
            form=form,
            form_title='Tambah data kelas baru',
            form_action=url_for('admin.class_create'),
            form_id='newForm',
            btn_primary='Tambah')


class _ReadView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self):
        if request.args.get('act') == 'list':
            return create_response(STAT_SUCCESS, html_list=render_html_data_list())
        return render_template('admin/classes.html')


class _UpdateView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self, obj_id):
        model = self.get_class(obj_id)
        if model:
            form = ClassForm()
            form.name.data = model.name
            form.year.data = model.year
            form.study_program.data = model.study_id
            form.cls_type.data = model.type
            return create_response(STAT_SUCCESS, html_form=self.render_form(form, obj_id=obj_id))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    def post(self, obj_id):
        model = self.get_class(obj_id)
        if model:
            form = ClassForm()
            if form.validate_on_submit():
                model.study_id = form.study_program.data
                model.name = form.name.data
                model.year = form.year.data
                model.type = form.cls_type.data
                db_session.commit()
                return create_response(STAT_SUCCESS, html_list=render_html_data_list())
            return create_response(STAT_INVALID, html_form=self.render_form(form, obj_id=obj_id))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    @staticmethod
    def get_class(obj_id):
        return db_session.query(Class).filter(Class.id == obj_id).first()

    @staticmethod
    def render_form(form, obj_id):
        return render_template(
            'admin/partials/cls/class_form.html',
            form=form,
            form_title='Perbarui data kelas',
            form_action=url_for('admin.class_update', obj_id=obj_id),
            form_id='editForm',
            btn_primary='Perbarui')


class _DeleteView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self, obj_id):
        model = self.get_class(obj_id)
        if model:
            return create_response(STAT_SUCCESS,
                                   html_form=render_template('admin/partials/cls/class_delete.html', obj=model))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    def post(self, obj_id):
        model = self.get_class(obj_id)
        if model:
            db_session.delete(model)
            db_session.commit()
            return create_response(STAT_SUCCESS, html_list=render_html_data_list())
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    @staticmethod
    def get_class(obj_id):
        return db_session.query(Class).filter(Class.id == obj_id).first()


CrudClass = Crud(
    'class', 'classes',
    _CreateView,
    _ReadView,
    _UpdateView,
    _DeleteView
)
