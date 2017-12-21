# publishers.py
# Created by abdularis on 19/10/17

from flask import render_template, request, url_for
from flask.views import MethodView
from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, StringField
from wtforms.validators import InputRequired

from unma.admin.wtformutil import UniqueValue, SwitchableRequired
from unma.ajaxutil import create_response, STAT_SUCCESS, STAT_INVALID, STAT_ERROR
from unma.common import decorate_function, CrudRouter
from unma.database import db_session
from unma.models import Admin, Department
from unma.session import AdminRequired


render_template = decorate_function(render_template, page='publisher')


class PublisherForm(FlaskForm):
    name = StringField('Nama',
                       validators=[InputRequired()])
    username = StringField('Username',
                           validators=[InputRequired(),
                                       UniqueValue(Admin, Admin.username, message="Username sudah ada. Tidak boleh sama!")])
    password = StringField('Password',
                           validators=[SwitchableRequired()])
    allowed_department = SelectMultipleField('Izin Publish Ke',
                                             validators=[InputRequired()],
                                             coerce=int,
                                             choices=[])

    def __init__(self, edit_mode=None, last_value=None):
        super().__init__(csrf_enabled=False)
        self.allowed_department.choices = [(obj.id, obj.name) for obj in db_session.query(Department).all()]
        self.password.validators[0].enable = not edit_mode
        UniqueValue.set_edit_mode_on_field(self.username, edit_mode, last_value)


def render_html_data_list():
    results = db_session.query(Admin).filter(Admin.role == 'PUB').all()
    return render_template('admin/partials/pub/publisher_list.html', objs=results)


def get_publisher(publisher_id):
    return db_session.query(Admin).filter(Admin.id == publisher_id, Admin.role == 'PUB').first()


class CreateView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self):
        form = PublisherForm()
        return create_response(STAT_SUCCESS, html_form=self.render_form(form))

    def post(self):
        form = PublisherForm()
        if form.validate_on_submit():
            assoc = db_session.query(Department).filter(Department.id.in_(form.allowed_department.data)).all()
            pub = Admin()
            pub.name = form.name.data
            pub.username = form.username.data
            pub.password = form.password.data
            pub.role = 'PUB'
            pub.departments = assoc
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


class ReadView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self):
        if request.args.get('act') == 'list':
            return create_response(STAT_SUCCESS, html_list=render_html_data_list())
        return render_template('admin/publishers.html')


class UpdateView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self, obj_id=None):
        model = get_publisher(obj_id)
        if model:
            form = PublisherForm()
            form.name.data = model.name
            form.username.data = model.username
            form.password.render_kw = {'placeholder': 'Password disembunyikan!'}
            form.allowed_department.data = [obj.id for obj in model.departments]
            return create_response(STAT_SUCCESS, html_form=self.render_form(form, obj_id=obj_id))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    def post(self, obj_id=None):
        model = get_publisher(obj_id)
        if model:
            form = PublisherForm(True, model.username)
            if form.validate_on_submit():
                assoc = db_session.query(Department).filter(Department.id.in_(form.allowed_department.data)).all()
                model.name = form.name.data
                model.username = form.username.data
                model.departments = assoc
                if form.password.data:
                    model.password = form.password.data
                db_session.commit()
                return create_response(STAT_SUCCESS, html_list=render_html_data_list())
            return create_response(STAT_INVALID, html_form=self.render_form(form, obj_id=obj_id))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    @staticmethod
    def render_form(form, obj_id):
        return render_template(
            'admin/partials/pub/publisher_form.html',
            form=form,
            form_title='Perbarui akun publisher',
            form_action=url_for('admin.publisher_update', obj_id=obj_id),
            form_id='editForm',
            btn_primary='Perbarui')


class DeleteView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self, obj_id):
        model = get_publisher(obj_id)
        if model:
            return create_response(STAT_SUCCESS,
                                   html_form=render_template('admin/partials/pub/publisher_delete.html', obj=model))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    def post(self, obj_id):
        model = get_publisher(obj_id)
        if model:
            db_session.delete(model)
            db_session.commit()
            return create_response(STAT_SUCCESS, html_list=render_html_data_list())
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))


CrudPublisher = CrudRouter(
    'publisher', 'publishers',
    CreateView,
    ReadView,
    UpdateView,
    DeleteView
)
