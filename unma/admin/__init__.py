# __init__.py.py
# Created by abdularis on 08/10/17

from flask import Blueprint
from .auth import LoginView, LogoutView
from .index import IndexView
from .department import CrudDepartment
from .classes import CrudClass
from .students import CrudStudent
from .publishers import CrudPublisher
from .announcements import CrudAnnouncement
from .profiles import UpdatePasswordView, UpdateProfileInfoView, ProfileDetailView
from .lecturer import CrudLecturer


admin = Blueprint('admin', __name__,
                  url_prefix='/admin')

admin.add_url_rule('/home', view_func=IndexView.as_view('index'))
admin.add_url_rule('/login', view_func=LoginView.as_view('login'))
admin.add_url_rule('/logout', view_func=LogoutView.as_view('logout'))
admin.add_url_rule('/profile', view_func=ProfileDetailView.as_view('profile_detail'))
admin.add_url_rule('/profile/update_profile',
                   view_func=UpdateProfileInfoView.as_view('profile_update_profile'))
admin.add_url_rule('/profile/update_password',
                   view_func=UpdatePasswordView.as_view('profile_update_password'))

CrudDepartment.register_url_rules(admin)
CrudClass.register_url_rules(admin)
CrudStudent.register_url_rules(admin)
CrudPublisher.register_url_rules(admin)
CrudAnnouncement.register_url_rules(admin)
CrudLecturer.register_url_rules(admin)
