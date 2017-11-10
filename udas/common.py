# common.py
# Created by abdularis on 07/11/17

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


def overrides(base_class):
    def overrider(method):
        assert(method.__name__ in dir(base_class))
        return method
    return overrider
