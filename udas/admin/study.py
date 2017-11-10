# study.py
# Created by abdularis on 15/10/17

from flask import render_template, request, url_for

from udas.repofactory import rf, StudyModel
from udas.login import AdminRequired
from udas.crud import Crud, BaseCreateView, BaseUpdateView, BaseReadView, BaseDeleteView
from udas.forms import StudyForm
from udas.decorator import decorate_function


render_template = decorate_function(render_template, page='study')


def get_data_list():
    results = rf.study_repo().get_all()
    for res in results:
        res.classes_count = len(res.classes)
    return results


def render_html_data_list():
    return render_template('admin/partials/sp/studyprogram_list.html', objs=get_data_list())


class CreateView(BaseCreateView):
    decorators = [AdminRequired('admin.login')]

    def __init__(self):
        super().__init__(render_html_data_list)

    def create_form(self, method):
        return StudyForm()

    def save_form(self, form):
        study = StudyModel()
        study.name = form.name.data
        rf.study_repo().add(study)
        return True, None

    def render_form(self, form):
        return render_template(
            'admin/partials/sp/studyprogram_form.html',
            form=form,
            form_title='Tambah data program studi baru',
            form_action=url_for('admin.study_create'),
            form_id='newForm',
            btn_primary='Tambah')


class ReadView(BaseReadView):
    decorators = [AdminRequired('admin.login')]

    def __init__(self):
        super().__init__(disable_detail_view=True)

    def render_container(self):
        return render_template('admin/studies.html')

    def render_list(self):
        results = get_data_list()
        return render_template('admin/partials/sp/studyprogram_list.html', objs=results)


class UpdateView(BaseUpdateView):
    decorators = [AdminRequired('admin.login')]

    def __init__(self):
        super().__init__(render_html_data_list)

    def get_model(self, obj_id):
        return rf.study_repo().get_by_id(obj_id)

    def create_form(self, method, model):
        if method == 'GET':
            form = StudyForm()
            form.name.data = model.name
            for cls in model.classes:
                for std in cls.students:
                    print(std.name)
            return form
        else:
            return StudyForm(request.form, True, model.name)

    def modify_model(self, form, model):
        model.name = form.name.data
        rf.study_repo().update_by_id(model.id, model)
        return True, None

    def render_form(self, form, obj_id):
        return render_template(
            'admin/partials/sp/studyprogram_form.html',
            form=form,
            form_title='Perbarui data program studi',
            form_action=url_for('admin.study_update', obj_id=obj_id),
            form_id='editForm',
            btn_primary='Perbarui')


class DeleteView(BaseDeleteView):

    def __init__(self):
        super().__init__(render_html_data_list)

    def get_model(self, obj_id):
        return rf.study_repo().get_by_id(obj_id)

    def render_delete_form(self, model):
        return render_template('admin/partials/sp/studyprogram_delete.html', obj=model)

    def delete_model(self, model):
        rf.study_repo().delete_by_id(model.id)
        return True, None


CrudStudy = Crud(
    'study', 'studies',
    CreateView,
    ReadView,
    UpdateView,
    DeleteView
)
