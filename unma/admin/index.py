# index.py
# Created by abdularis on 08/10/17

from flask import render_template, g
from flask.views import View
from sqlalchemy import desc

from unma.admin import announcements
from unma.database import db_session
from unma.models import Announcement, Admin
from unma.session import LoginRequired


class IndexViewModel(object):
    def __init__(self):
        self.latest_announcements = self.get_latest_announcements()

    @staticmethod
    def get_latest_announcements():
        if g.curr_user.is_admin:
            query = db_session.query(Announcement).order_by(desc(Announcement.last_updated)).limit(3)
        else:
            publisher = db_session.query(Admin).filter(Admin.username == g.curr_user.username).first()
            query = db_session.query(Announcement).filter(Announcement.publisher == publisher).order_by(desc(Announcement.last_updated)).limit(3)

        results = query.all()
        announcement_view_model = None
        if results:
            announcement_view_model = [announcements.AnnouncementModelView(result) for result in results]
        return announcement_view_model


class IndexView(View):
    decorators = [LoginRequired('admin.login')]

    def dispatch_request(self):
        view_model = IndexViewModel()
        print(type(view_model.latest_announcements))
        return render_template('admin/index.html', model=view_model, title='UNMA Mobile Announcement')
