# publishers.py
# Created by abdularis on 19/10/17

from flask import render_template, request, url_for
from flask.views import MethodView

from udas.ajaxutil import create_response, STAT_SUCCESS, STAT_INVALID, STAT_ERROR
from udas.database import db_session
from udas.models import Admin, Study
from udas.login import AdminRequired
from udas.crud import Crud, BaseCreateView, BaseReadView, BaseUpdateView, BaseDeleteView
from udas.forms import PublisherForm
from udas.decorator import decorate_function


render_template = decorate_function(render_template, page='publisher')


def render_html_data_list():
    results = db_session.query(Admin).filter(Admin.role == 'PUB').all()
    return render_template('admin/partials/pub/publisher_list.html', objs=results)


class _CreateView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self):
        form = PublisherForm()
        return create_response(STAT_SUCCESS, html_form=self.render_form(form))

    def post(self):
        form = PublisherForm()
        if form.validate_on_submit():
            assoc = db_session.query(Study).filter(Study.id.in_(form.allowed_study_program.data)).all()
            pub = Admin()
            pub.name = form.name.data
            pub.username = form.username.data
            pub.password = form.password.data
            pub.role = 'PUB'
            pub.studies = assoc
            db_session.add(pub)
            db_session.commit()
            return create_response(STAT_SUCCESS, html_list=render_html_data_list())
        return create_response(STAT_INVALID, html_form=self.render_form(form))

    @staticmethod
    def render_form(form):
        return render_template(
            'admin/partials/pub/publisher_form.html',
            form=form,
            form_title='Tambah akun publisher',
            form_action=url_for('admin.publisher_create'),
            form_id='newForm',
            btn_primary='Tambah')


class _ReadView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self):
        if request.args.get('act') == 'list':
            return create_response(STAT_SUCCESS, html_list=render_html_data_list())
        return render_template('admin/publishers.html')


class _UpdateView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self, obj_id=None):
        model = self.get_publisher(obj_id)
        if model:
            form = PublisherForm()
            form.name.data = model.name
            form.username.data = model.username
            form.password.render_kw = {'placeholder': 'Password disembunyikan!'}
            form.allowed_study_program.data = [obj.id for obj in model.studies]
            return create_response(STAT_SUCCESS, html_form=self.render_form(form, obj_id=obj_id))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    def post(self, obj_id=None):
        model = self.get_publisher(obj_id)
        if model:
            form = PublisherForm(True, model.username)
            if form.validate_on_submit():
                assoc = db_session.query(Study).filter(Study.id.in_(form.allowed_study_program.data)).all()
                model.name = form.name.data
                model.username = form.username.data
                model.studies = assoc
                if form.password.data:
                    model.password = form.password.data
                db_session.commit()
                return create_response(STAT_SUCCESS, html_list=render_html_data_list())
            return create_response(STAT_INVALID, html_form=self.render_form(form, obj_id=obj_id))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    @staticmethod
    def get_publisher(publisher_id):
        return db_session.query(Admin).filter(Admin.id == publisher_id, Admin.role == 'PUB').first()

    @staticmethod
    def render_form(form, obj_id):
        return render_template(
            'admin/partials/pub/publisher_form.html',
            form=form,
            form_title='Perbarui akun publisher',
            form_action=url_for('admin.publisher_update', obj_id=obj_id),
            form_id='editForm',
            btn_primary='Perbarui')


class _DeleteView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self, obj_id):
        model = self.get_publisher(obj_id)
        if model:
            return create_response(STAT_SUCCESS,
                                   html_form=render_template('admin/partials/pub/publisher_delete.html', obj=model))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    def post(self, obj_id):
        model = self.get_publisher(obj_id)
        if model:
            db_session.delete(model)
            db_session.commit()
            return create_response(STAT_SUCCESS, html_list=render_html_data_list())
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    @staticmethod
    def get_publisher(publisher_id):
        return db_session.query(Admin).filter(Admin.id == publisher_id, Admin.role == 'PUB').first()


CrudPublisher = Crud(
    'publisher', 'publishers',
    _CreateView,
    _ReadView,
    _UpdateView,
    _DeleteView
)
