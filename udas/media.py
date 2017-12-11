# media.py
# Created by abdularis on 25/11/17

import os
import mimetypes

from werkzeug.utils import secure_filename
from udas import app

DEFAULT_THUMBNAIL_FILENAME = 'thumb.jpg'


def get_media_folder(announcement_id):
    media_folder = os.path.join(app.config.get('UPLOAD_FOLDER'), announcement_id)
    if not os.path.exists(media_folder):
        os.mkdir(media_folder)
    return media_folder


def get_upload_folder(announcement_id):
    upload_folder = os.path.join(get_media_folder(announcement_id), 'upload')
    if not os.path.exists(upload_folder):
        os.mkdir(upload_folder)
    return upload_folder


def get_thumbnail_file_path(announcement_id):
    return os.path.join(get_media_folder(announcement_id), DEFAULT_THUMBNAIL_FILENAME)


def save_uploaded_file(announcement_id, file):
    if file:
        filename = secure_filename(file.filename)
        folder_path = get_upload_folder(announcement_id)
        file_path = os.path.join(folder_path, filename)
        file.save(file_path)
        return filename
    return None


def get_uploaded_file_properties(announcement_id, file_name):
    file_path = os.path.join(get_upload_folder(announcement_id), file_name)
    file_size = 0
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)

    prop = {
        'name': file_name,
        'mimetype': mimetypes.guess_type(file_name)[0],
        'size': file_size
    }
    return prop

