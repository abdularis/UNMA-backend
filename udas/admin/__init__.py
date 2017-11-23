# __init__.py.py
# Created by abdularis on 08/10/17

from flask import Blueprint
from .auth import LoginView, LogoutView
from .index import IndexView
from .study import CrudStudy
from .classes import CrudClass
from .students import CrudStudent
from .publishers import CrudPublisher
from .announcements import CrudAnnouncement


admin = Blueprint('admin', __name__,
                  url_prefix='/admin')

admin.add_url_rule('/home', view_func=IndexView.as_view('index'))
admin.add_url_rule('/login', view_func=LoginView.as_view('login'))
admin.add_url_rule('/logout', view_func=LogoutView.as_view('logout'))

CrudStudy.register_url_rules(admin)
CrudClass.register_url_rules(admin)
CrudStudent.register_url_rules(admin)
CrudPublisher.register_url_rules(admin)
CrudAnnouncement.register_url_rules(admin)
