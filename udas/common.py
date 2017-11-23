# common.py
# Created by abdularis on 07/11/17

import functools
import os
import mimetypes

from werkzeug.utils import secure_filename
from udas import app


def save_uploaded_file(inner_folder, file):
    if file:
        filename = secure_filename(file.filename)
        folder_path = get_uploaded_file_folder(inner_folder)
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        file_path = os.path.join(folder_path, filename)
        file.save(file_path)
        return filename
    return None


def get_uploaded_file_folder(inner_folder):
    return os.path.join(app.config.get('UPLOAD_FOLDER'), inner_folder)


def get_uploaded_file_properties(inner_folder, file_name):
    file_path = os.path.join(get_uploaded_file_folder(inner_folder), file_name)
    file_size = 0
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)

    prop = {
        'name': file_name,
        'mimetype': mimetypes.guess_type(file_name)[0],
        'size': file_size
    }
    return prop


def decorate_function(f, **add_kwargs):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        kwargs.update(add_kwargs)
        return f(*args, **kwargs)
    return wrapper


class CrudRouter(object):

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
