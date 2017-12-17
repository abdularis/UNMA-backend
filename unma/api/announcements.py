# announcements.py
# Created by abdularis on 07/11/17

import os

from flask import request, g, send_from_directory, abort, url_for, make_response
from flask.views import MethodView

from unma.api.authutil import token_required
from unma.api.response import create_response
from unma.database import db_session
from unma.media import get_uploaded_file_properties, get_upload_folder
from unma.models import StudentAnnouncementAssoc, Announcement


class AnnouncementDescription(MethodView):
    decorators = [token_required]

    def get(self, pub_id):
        result = db_session.query(Announcement.description)\
                    .filter(Announcement.public_id == str(pub_id))\
                    .first()
        if result:
            return result[0]
        return make_response('Description not found!', 404)


class AttachmentDownload(MethodView):
    decorators = [token_required]

    def get(self, pub_id, filename):
        folder_path = get_upload_folder(str(pub_id))
        if os.path.exists(folder_path):
            return send_from_directory(folder_path, filename)
        return abort(404)


class AnnouncementRead(MethodView):
    decorators = [token_required]

    def put(self, pub_id):
        res = db_session.query(StudentAnnouncementAssoc)\
            .filter(Announcement.public_id == str(pub_id),
                    StudentAnnouncementAssoc.student_id == g.user_id,
                    StudentAnnouncementAssoc.announce_id == Announcement.id)\
            .first()

        if res:
            if not res.read:
                res.read = True
                db_session.commit()
            return create_response(True, message='Announcement has been marked as read')
        return create_response(False, s_code=404)


class AnnouncementList(MethodView):
    decorators = [token_required]

    def get(self, obj_id=None):
        if obj_id:
            result = db_session.query(StudentAnnouncementAssoc.read, Announcement)\
                .filter(StudentAnnouncementAssoc.student_id == g.user_id,
                    Announcement.id == StudentAnnouncementAssoc.announce_id, Announcement.public_id == str(obj_id))\
                .first()
            if result and len(result) >= 2:
                return create_response(True, data=self.build_announcement_json_object(result[0], result[1]))
            else:
                return create_response(False, message="Data not found!")

        filters = [StudentAnnouncementAssoc.student_id == g.user_id,
                   Announcement.id == StudentAnnouncementAssoc.announce_id]
        if 'since' in request.args:
            filters.append(Announcement.last_updated >= float(request.args.get('since')))

        results = None
        if 'limit' in request.args and 'page' in request.args:
            limit = int(request.args['limit'])
            page = int(request.args['page'])

            if limit > 0 and page >= 0:
                offset = limit * page

                results = db_session.query(StudentAnnouncementAssoc.read, Announcement) \
                    .filter(*filters) \
                    .order_by(Announcement.last_updated.desc()) \
                    .limit(limit) \
                    .offset(offset) \
                    .all()

        if not results:
            results = db_session.query(StudentAnnouncementAssoc.read, Announcement) \
                .filter(*filters) \
                .order_by(Announcement.last_updated.desc()) \
                .all()

        data = []
        if results and len(results) > 0:
            for read, announcement in results:
                ann_json = self.build_announcement_json_object(read, announcement)
                data.append(ann_json)
        return create_response(True, data=data)

    @staticmethod
    def build_announcement_json_object(read, announcement):
        obj = {
            'id': announcement.public_id,
            'title': announcement.title,
            'description': None,
            'publisher': announcement.publisher.name,
            'last_updated': announcement.last_updated,
            'attachment': None,
            'read': True if read else False
        }

        if announcement.description:
            size = len(announcement.description)
            obj['description'] = {
                'url': url_for('api.announcement_description',
                               pub_id=announcement.public_id,
                               _external=True),
                'content': announcement.description if (size / 1024) <= 8 else None,
                'size': size
            }

        if announcement.attachment:
            obj['attachment'] = get_uploaded_file_properties(announcement.public_id, announcement.attachment)
            obj['attachment']['url'] = url_for('api.announcement_attachment',
                                               pub_id=announcement.public_id,
                                               filename=announcement.attachment,
                                               _external=True)

        return obj