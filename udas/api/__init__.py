# __init__.py
# Created by abdularis on 19/10/17

from flask import Blueprint

from .announcements import AnnouncementList, AnnouncementDescription, AttachmentDownload, AnnouncementRead, \
    AnnouncementThumbnail
from .clientaccount import ClientAuthentication, ClientProfile, ClientToken


api = Blueprint('api', __name__, url_prefix='/api')

get_announcement = AnnouncementList.as_view('announcement')

api.add_url_rule('/session', view_func=ClientAuthentication.as_view('auth'))
api.add_url_rule('/profile', view_func=ClientProfile.as_view('profile'))
api.add_url_rule('/token', view_func=ClientToken.as_view('token'))
api.add_url_rule('/announcements', view_func=get_announcement)
api.add_url_rule('/announcements/<uuid:obj_id>', view_func=get_announcement)
api.add_url_rule('/announcements/<uuid:obj_id>/thumbnail', view_func=AnnouncementThumbnail.as_view('announcement_thumbnail'))
api.add_url_rule('/announcements/<uuid:pub_id>/description',
                 view_func=AnnouncementDescription.as_view('announcement_description'))
api.add_url_rule('/announcements/<uuid:pub_id>/attachment/<string:filename>',
                 view_func=AttachmentDownload.as_view('announcement_attachment'))
api.add_url_rule('/announcements/<uuid:pub_id>/read',
                 view_func=AnnouncementRead.as_view('announcement_read'))
