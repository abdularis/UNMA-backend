# crud.py
# Created by abdularis on 15/10/17

import functools

from flask import request, render_template
from flask.views import MethodView

from .ajaxutil import create_response, STAT_SUCCESS, STAT_ERROR, STAT_INVALID


class Interceptor(object):

    def __init__(self, interceptor):
        if not callable(interceptor):
            raise ValueError('interceptor must be a callable')
        self.interceptor = interceptor

    def __call__(self, f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            proceed, result = self.interceptor(*args, **kwargs)
            if proceed:
                return f(*args, **kwargs)
            else:
                return result
        return wrapper


class InterceptableView(MethodView):
    """Interceptable view dimana request(GET & POST) dapat di intercept/cegat
       sebelum diproses oleh method get() atau post()"""

    def __init__(self, get_interceptor, post_interceptor):
        """
        Constructor

        :param get_interceptor: interceptor for get method
        :param post_interceptor: interceptor for post method
        """
        if get_interceptor:
            if isinstance(get_interceptor, Interceptor):
                self.get = get_interceptor(self.get)
            else:
                raise ValueError('GET interceptor must be an object of type Interceptor')
        if post_interceptor:
            if isinstance(post_interceptor, Interceptor):
                self.post = post_interceptor(self.post)
            else:
                raise ValueError('POST interceptor must be an object of type Interceptor')


class BaseCreateView(InterceptableView):

    def __init__(self, html_data_list_renderer,
                 get_interceptor=None, post_interceptor=None):
        super().__init__(get_interceptor, post_interceptor)
        self.html_data_list_renderer = html_data_list_renderer

    def get(self):
        form = self.create_form('GET')
        return create_response(STAT_SUCCESS, html_form=self.render_form(form))

    def post(self):
        form = self.create_form('POST')
        if form.validate_on_submit():
            success, msg = self.save_form(form)
            if success:
                return create_response(STAT_SUCCESS, html_list=self.html_data_list_renderer(), html_extra=msg)
            else:
                return create_response(STAT_ERROR, html_error=msg)
        else:
            return create_response(STAT_INVALID, html_form=self.render_form(form))

    def create_form(self, method):
        """
        Override method ini untuk membuat form yang sesuai dengan kebutuhan

        :param method: either 'GET' or 'POST'
        :return: form object
        """
        return None

    def render_form(self, form):
        """
        Render the passed form object

        :param form: form tobe rendered
        :return: rendered form in the form of html or any kind of data string
        """
        return ''

    def save_form(self, form):
        """
        Save the data inside form into some persistence (file, db etc.)

        :param form: form with the data inside it
        :return: (success, additional message)
        """
        return False, ''


class BaseReadView(InterceptableView):

    def __init__(self,
                 disable_detail_view=False,
                 get_interceptor=None):
        super().__init__(get_interceptor, None)
        self.disable_detail_view = disable_detail_view

    def __call__(self):
        return self.render_list()

    def get(self, obj_id=None):
        if request.args.get('act') == 'list':
            html_list = self.render_list()
            return create_response(STAT_SUCCESS, html_list=html_list)
        elif obj_id and not self.disable_detail_view:
            return self.render_detail(obj_id)
        else:
            return self.render_container()

    def render_container(self):
        """
        Render halaman utama/main container untuk halaman CRUD

        :return: rendered container page
        """
        pass

    def render_detail(self, obj_id):
        """
        Render detail view of a specified object id

        :param obj_id: unique object identifier
        :return: rendered detail view
        """
        pass

    def render_list(self):
        """
        Render list of objects to be placed in a main container or some kind of container

        :return: rendered list of objects
        """
        pass


class BaseUpdateView(InterceptableView):

    def __init__(self, html_data_list_renderer,
                 get_interceptor=None, post_interceptor=None):
        super().__init__(get_interceptor, post_interceptor)
        self.html_data_list_renderer = html_data_list_renderer

    def get(self, obj_id=None):
        model = self.get_model(obj_id)
        if model:
            form = self.create_form('GET', model=model)
            return create_response(STAT_SUCCESS, html_form=self.render_form(form, obj_id=obj_id))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    def post(self, obj_id=None):
        model = self.get_model(obj_id)
        if model:
            form = self.create_form('POST', model=model)
            if form.validate_on_submit():
                success, msg = self.modify_model(form, model=model)
                if success:
                    return create_response(STAT_SUCCESS, html_list=self.html_data_list_renderer(), html_extra=msg)
                else:
                    return create_response(STAT_ERROR, html_error=msg)
            return create_response(STAT_INVALID, html_form=self.render_form(form, obj_id=obj_id))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    def get_model(self, obj_id):
        """
        Query the model object from persistence with uniquely identified by obj_id

        :param obj_id: unique identifier of a model
        :return: either a model object or None
        """
        return None

    def modify_model(self, form, model):
        """
        Modify the model based on the value of the form

        :param form: form with the data inside it
        :param model: a model object which data is to be modified from the form data
        :return: tuple (success, additional message)
        """
        return False, ''

    def create_form(self, method, model):
        """
        Override method ini untuk membuat form yang sesuai dengan kebutuhan,
        dengan data di populate dari object model

        :param method: either 'GET' or 'POST'
        :param model: a model object returned by get_model() method
        :return: form object
        """
        return None

    def render_form(self, form, obj_id):
        """
        Render the form object with obj_id as a unique id of a given object model

        :param form: form tobe rendered
        :param obj_id: a unique identifier for a model, retrieved from URL
        :return: rendered form in the form of html or any kind of data string
        """
        return ''


class BaseDeleteView(InterceptableView):
    def __init__(self, html_data_list_renderer,
                 get_interceptor=None, post_interceptor=None):
        super().__init__(get_interceptor, post_interceptor)
        self.html_data_list_renderer = html_data_list_renderer

    def get(self, obj_id):
        model = self.get_model(obj_id)
        if model:
            return create_response(STAT_SUCCESS,
                                   html_form=self.render_delete_form(model=model))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    def post(self, obj_id):
        model = self.get_model(obj_id)
        if model:
            success, err_msg = self.delete_model(model)
            if success:
                return create_response(STAT_SUCCESS, html_list=self.html_data_list_renderer())
            else:
                return create_response(STAT_ERROR, html_error=err_msg)
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    def get_model(self, obj_id):
        return None

    def delete_model(self, model):
        """
        Delete a given model object from the persistence

        :param model: to be deleted
        :return: tuple (success, error message)
        """
        return False, ''

    def render_delete_form(self, model):
        """
        Render delete form to confirm if the given model should be deleted

        :param model: a model to confirm to be deleted
        :return: renderer form
        """
        return None


class Crud(object):

    def __init__(self, endpoint_prefix, url_prefix, create_t, read_t, update_t, delete_t, url_param_t='int'):
        self.url_prefix = url_prefix
        self.url_param_t = url_param_t
        create_view = create_t.as_view('%s_create' % endpoint_prefix)
        read_view = read_t.as_view('%s_read' % endpoint_prefix)
        update_view = update_t.as_view('%s_update' % endpoint_prefix)
        delete_view = delete_t.as_view('%s_delete' % endpoint_prefix)

        self.views = {
            'create': create_view,
            'read': read_view,
            'update': update_view,
            'delete': delete_view
        }

    def register_url_rules(self, app):
        create_url = '/%s/new' % self.url_prefix
        read_url = '/%s' % self.url_prefix
        detail_url = '/%s/<%s:obj_id>' % (self.url_prefix, self.url_param_t)
        update_url = '/%s/<%s:obj_id>/update' % (self.url_prefix, self.url_param_t)
        delete_url = '/%s/<%s:obj_id>/delete' % (self.url_prefix, self.url_param_t)

        app.add_url_rule(create_url, view_func=self.views['create'])
        app.add_url_rule(read_url, view_func=self.views['read'])
        app.add_url_rule(detail_url, view_func=self.views['read'])
        app.add_url_rule(update_url, view_func=self.views['update'])
        app.add_url_rule(delete_url, view_func=self.views['delete'])
