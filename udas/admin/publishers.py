# publishers.py
# Created by abdularis on 19/10/17

from flask import render_template, request, url_for

from udas.repofactory import rf, AdminModel
from udas.login import AdminRequired
from udas.crud import Crud, BaseCreateView, BaseReadView, BaseUpdateView, BaseDeleteView
from udas.forms import PublisherForm
from udas.decorator import decorate_function


render_template = decorate_function(render_template, page='publisher')


def render_html_data_list():
    results = rf.admin_repo().get_all_publisher()
    return render_template('admin/partials/pub/publisher_list.html', objs=results)


class CreateView(BaseCreateView):
    decorators = [AdminRequired('admin.login')]

    def __init__(self):
        super().__init__(render_html_data_list)

    def create_form(self, method):
        return PublisherForm(request.form) if method == 'POST' else PublisherForm()

    def save_form(self, form):
        pub = AdminModel()
        pub.name = form.name.data
        pub.username = form.username.data
        pub.password = form.password.data
        pub.role = 'PUB'
        rf.admin_repo().add(pub, form.allowed_study_program.data)
        return True, None

    def render_form(self, form):
        return render_template(
            'admin/partials/pub/publisher_form.html',
            form=form,
            form_title='Tambah akun publisher',
            form_action=url_for('admin.publisher_create'),
            form_id='newForm',
            btn_primary='Tambah')


class ReadView(BaseReadView):
    decorators = [AdminRequired('admin.login')]

    def __init__(self):
        super().__init__(disable_detail_view=True)

    def render_list(self):
        return render_html_data_list()

    def render_container(self):
        return render_template('admin/publishers.html')


class UpdateView(BaseUpdateView):
    decorators = [AdminRequired('admin.login')]

    def __init__(self):
        super().__init__(render_html_data_list)

    def get_model(self, obj_id):
        return rf.admin_repo().get_publisher_by_id(obj_id)

    def modify_model(self, form, model):
        model.name = form.name.data
        model.username = form.username.data
        if form.password.data:
            model.password = form.password.data
        rf.admin_repo().update_by_id(model.id, model, form.allowed_study_program.data)
        return True, None

    def create_form(self, method, model):
        if method == 'GET':
            form = PublisherForm()
            form.name.data = model.name
            form.username.data = model.username
            form.password.render_kw = {'placeholder': 'Password disembunyikan!'}
            form.allowed_study_program.data = [obj.id for obj in rf.admin_repo().get_allowed_study_programs(model)]
            return form
        else:
            return PublisherForm(request.form, True, model.username)

    def render_form(self, form, obj_id):
        return render_template(
            'admin/partials/pub/publisher_form.html',
            form=form,
            form_title='Perbarui akun publisher',
            form_action=url_for('admin.publisher_update', obj_id=obj_id),
            form_id='editForm',
            btn_primary='Perbarui')


class DeleteView(BaseDeleteView):
    decorators = [AdminRequired('admin.login')]

    def __init__(self):
        super().__init__(render_html_data_list)

    def get_model(self, obj_id):
        return rf.admin_repo().get_publisher_by_id(obj_id)

    def delete_model(self, model):
        rf.admin_repo().delete_by_id(model.id)
        return True, None

    def render_delete_form(self, model):
        return render_template('admin/partials/pub/publisher_delete.html', obj=model)


CrudPublisher = Crud(
    'publisher', 'publishers',
    CreateView,
    ReadView,
    UpdateView,
    DeleteView
)
