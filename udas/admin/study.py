# study.py
# Created by abdularis on 15/10/17

from flask import render_template, request, url_for
from flask.views import MethodView

from udas.ajaxutil import STAT_SUCCESS, create_response, STAT_ERROR, STAT_INVALID
from udas.database import db_session
from udas.models import Study
from udas.login import AdminRequired
from udas.crud import Crud, BaseCreateView, BaseUpdateView, BaseReadView, BaseDeleteView
from udas.forms import StudyForm
from udas.decorator import decorate_function


render_template = decorate_function(render_template, page='study')


def get_data_list():
    results = db_session.query(Study).order_by(Study.id.desc()).all()
    for res in results:
        res.classes_count = len(res.classes)
    return results


def render_html_data_list():
    return render_template('admin/partials/sp/studyprogram_list.html', objs=get_data_list())


class _CreateView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self):
        form = StudyForm()
        return create_response(STAT_SUCCESS, html_form=self.render_form(form))

    def post(self):
        form = StudyForm()
        if form.validate_on_submit():
            std = Study()
            std.name = form.name.data
            db_session.add(std)
            db_session.commit()
            return create_response(STAT_SUCCESS, html_list=render_html_data_list())
        return create_response(STAT_INVALID, html_form=self.render_form(form))

    @staticmethod
    def render_form(form):
        return render_template(
            'admin/partials/sp/studyprogram_form.html',
            form=form,
            form_title='Tambah data program studi baru',
            form_action=url_for('admin.study_create'),
            form_id='newForm',
            btn_primary='Tambah')


class _ReadView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self):
        if request.args.get('act') == 'list':
            html_list = render_html_data_list()
            return create_response(STAT_SUCCESS, html_list=html_list)
        return render_template('admin/studies.html')


class _UpdateView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self, obj_id):
        model = self.get_study_program(obj_id)
        if model:
            form = StudyForm()
            form.name.data = model.name
            return create_response(STAT_SUCCESS, html_form=self.render_form(form, obj_id=obj_id))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    def post(self, obj_id):
        model = self.get_study_program(obj_id)
        if model:
            form = StudyForm(True, model.name)
            if form.validate_on_submit():
                model.name = form.name.data
                db_session.commit()
                return create_response(STAT_SUCCESS, html_list=render_html_data_list())
            return create_response(STAT_INVALID, html_form=self.render_form(form, obj_id=obj_id))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    @staticmethod
    def get_study_program(obj_id):
        return db_session.query(Study).filter(Study.id == obj_id).first()

    @staticmethod
    def render_form(form, obj_id):
        return render_template(
            'admin/partials/sp/studyprogram_form.html',
            form=form,
            form_title='Perbarui data program studi',
            form_action=url_for('admin.study_update', obj_id=obj_id),
            form_id='editForm',
            btn_primary='Perbarui')


class _DeleteView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self, obj_id):
        model = self.get_study_program(obj_id)
        if model:
            return create_response(STAT_SUCCESS,
                                   html_form=render_template('admin/partials/sp/studyprogram_delete.html', obj=model))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    def post(self, obj_id):
        model = self.get_study_program(obj_id)
        if model:
            db_session.delete(model)
            db_session.commit()
            return create_response(STAT_SUCCESS, html_list=render_html_data_list())
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    @staticmethod
    def get_study_program(obj_id):
        return db_session.query(Study).filter(Study.id == obj_id).first()


CrudStudy = Crud(
    'study', 'studies',
    _CreateView,
    _ReadView,
    _UpdateView,
    _DeleteView
)
