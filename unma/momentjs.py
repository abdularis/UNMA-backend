# momentjs.py
# Created by abdularis on 19/01/18

import uuid

from jinja2 import Markup


class momentjs(object):
    def __init__(self, timestamp):
        self.timestamp = timestamp
        self.html_cls = "fm_%s" % str(uuid.uuid4())

    def render(self, format):
        if not self.timestamp:
            return '-'

        placeholder = '<span class="%s"></span>' % self.html_cls
        if isinstance(self.timestamp, float): moment_script = 'moment.unix("%d").%s' % (self.timestamp, format)
        elif isinstance(self.timestamp, str): moment_script = 'moment("%s").%s' % (str(self.timestamp), format)
        else: moment_script = '-'
        return Markup("%s<script>\n$('.%s').html(%s);\n</script>" % (placeholder, self.html_cls, moment_script))

    def format(self, fmt):
        return self.render("format(\"%s\")" % fmt)
