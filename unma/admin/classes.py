# classes.py
# Created by abdularis on 18/10/17

from flask import render_template, request, url_for, flash
from flask.views import MethodView
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, IntegerField
from wtforms.validators import InputRequired

from unma.ajaxutil import create_response, STAT_SUCCESS, STAT_INVALID, STAT_ERROR
from unma.common import decorate_function, CrudRouter
from unma.database import db_session
from unma.models import Class, ClassTypes, Department
from unma.session import AdminRequired


render_template = decorate_function(render_template, page='class')


class ClassForm(FlaskForm):
    department = SelectField('Prodi',
                             validators=[InputRequired()],
                             coerce=int,
                             choices=[])
    name = StringField('Nama',
                       validators=[InputRequired(message='Name harus diisi')])
    year = IntegerField('Tahun',
                        validators=[InputRequired(message='Tahun harus diisi')])
    cls_type = SelectField('Tipe Kelas',
                           validators=[InputRequired()],
                           coerce=int,
                           choices=[t for t in zip(ClassTypes.keys(), ClassTypes.values())])

    def __init__(self):
        super().__init__(csrf_enabled=False)
        self.department.choices = [(obj.id, obj.name) for obj in db_session.query(Department).all()]

    def validate(self):
        valid = super().validate()
        if not valid:
            return False

        res = db_session.query(Class) \
            .filter(Class.department_id == self.department.data,
                    Class.name == self.name.data,
                    Class.year == self.year.data,
                    Class.type == self.cls_type.data) \
            .first()
        if res:
            flash('Data kelas "%s %s %s %d" sudah ada.' %
                  (dict(self.department.choices).get(self.department.data),
                   self.name.data, ClassTypes.get(self.cls_type.data), self.year.data))
            return False
        return True


def render_html_data_list():
    results = db_session.query(Class).all()
    return render_template('admin/partials/cls/class_list.html', objs=results)


def get_class(obj_id):
    return db_session.query(Class).filter(Class.id == obj_id).first()


class CreateView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self):
        form = ClassForm()
        return create_response(STAT_SUCCESS, html_form=self.render_form(form))

    def post(self):
        form = ClassForm()
        if form.validate_on_submit():
            cls = Class()
            cls.department_id = form.department.data
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


class ReadView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self):
        if request.args.get('act') == 'list':
            return create_response(STAT_SUCCESS, html_list=render_html_data_list())
        return render_template('admin/classes.html')


class UpdateView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self, obj_id):
        model = get_class(obj_id)
        if model:
            form = ClassForm()
            form.name.data = model.name
            form.year.data = model.year
            form.department.data = model.department_id
            form.cls_type.data = model.type
            return create_response(STAT_SUCCESS, html_form=self.render_form(form, obj_id=obj_id))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    def post(self, obj_id):
        model = get_class(obj_id)
        if model:
            form = ClassForm()
            if form.validate_on_submit():
                model.department_id = form.department.data
                model.name = form.name.data
                model.year = form.year.data
                model.type = form.cls_type.data
                db_session.commit()
                return create_response(STAT_SUCCESS, html_list=render_html_data_list())
            return create_response(STAT_INVALID, html_form=self.render_form(form, obj_id=obj_id))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    @staticmethod
    def render_form(form, obj_id):
        return render_template(
            'admin/partials/cls/class_form.html',
            form=form,
            form_title='Perbarui data kelas',
            form_action=url_for('admin.class_update', obj_id=obj_id),
            form_id='editForm',
            btn_primary='Perbarui')


class DeleteView(MethodView):
    decorators = [AdminRequired('admin.login')]

    def get(self, obj_id):
        model = get_class(obj_id)
        if model:
            return create_response(STAT_SUCCESS,
                                   html_form=render_template('admin/partials/cls/class_delete.html', obj=model))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    def post(self, obj_id):
        model = get_class(obj_id)
        if model:
            db_session.delete(model)
            db_session.commit()
            return create_response(STAT_SUCCESS, html_list=render_html_data_list())
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))


CrudClass = CrudRouter(
    'class', 'classes',
    CreateView,
    ReadView,
    UpdateView,
    DeleteView
)
