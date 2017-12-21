# index.py
# Created by abdularis on 08/10/17

from flask import render_template, g
from flask.views import View

from unma.session import LoginRequired


class IndexView(View):
    decorators = [LoginRequired('admin.login')]

    def dispatch_request(self):
        return render_template('admin/index.html', title='UNMA Mobile Announcement')
