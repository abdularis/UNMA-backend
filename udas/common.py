# common.py
# Created by abdularis on 07/11/17

import functools


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
