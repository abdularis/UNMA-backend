# repository.py
# Created by abdularis on 10/11/17

from flask_bcrypt import generate_password_hash, check_password_hash


class BaseRepoModel:
    def __init__(self):
        self.raw = None


class BaseUser(BaseRepoModel):
    def __init__(self, id=None, name='', username='', password='', date_created=None, last_login=None):
        super().__init__()
        self.id = id
        self.name = name
        self.username = username
        self._password = password
        self.date_created = date_created
        self.last_login = last_login

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    def verify_password(self, other):
        return check_password_hash(self._password, other)


class StudyModel(BaseRepoModel):
    def __init__(self):
        super().__init__()
        self.id = None
        self.name = ''


class ClassModel(BaseRepoModel):
    def __init__(self):
        super().__init__()
        self.id = None
        self.study_id = None
        self.name = ''
        self.year = 0
        self.type = 0


class StudentModel(BaseUser):
    def __init__(self, id=None, name='', username='', password='', date_created=None, last_login=None, class_id=None,):
        super().__init__(id, name, username, password, date_created, last_login)
        self.class_id = class_id


class TokenModel(BaseRepoModel):
    def __init__(self, student_id=None, access_token='', fcm_token=''):
        super().__init__()
        self.student_id = student_id
        self.access_token = access_token
        self.fcm_token = fcm_token


class AdminModel(BaseUser):
    def __init__(self, id=None, name='', username='', password='', date_created=None, last_login=None, role='', studies=None):
        super().__init__(id, name, username, password, date_created, last_login)
        self.role = role
        self.static_studies = studies
        self.dynamic_studies = None


class AnnouncementModel(BaseRepoModel):
    def __init__(self):
        super().__init__()
        self.id = None
        self.public_id = ''
        self.publisher_id = None
        self.title = ''
        self.description = ''
        self.attachment = None
        self.date_created = None
        self.last_updated = None


class BaseRepo:

    def add(self, new_obj):
        pass

    def get_by_id(self, obj_id):
        pass

    def get_all(self):
        pass

    def update_by_id(self, obj_id, updated_obj):
        pass

    def delete_by_id(self, obj_id):
        pass

    def delete_all(self):
        pass


class StudyRepo(BaseRepo):

    def get_by_student(self, std):
        pass


class ClassRepo(BaseRepo):

    def get_by_study_programs(self, study_programs):
        pass

    def get_study_program(self, cls):
        pass


class StudentRepo(BaseRepo):

    def check_for_account(self, username, password):
        pass

    def get_by_class(self, cls):
        pass

    def get_by_study_program(self, study):
        pass


class TokenRepo:

    def get_by(self, student_id=None, acc_token=None, fcm_token=None):
        pass

    def update(self, student_id, acc_token, fcm_token):
        pass

    def delete_by(self, stud_id=None, acc_token=None, fcm_token=None):
        pass


class AdminRepo:

    def add(self, new_obj, study_prog_ids):
        pass

    def check_for_account(self, username, password):
        pass

    def get_publisher_by_id(self, obj_id):
        pass

    def get_publisher_by_username(self, username):
        pass

    def get_all_publisher(self):
        pass

    def get_allowed_study_programs(self, adm):
        pass

    def update_by_id(self, obj_id, updated_obj, study_prog_ids):
        pass

    def delete_by_id(self, obj_id):
        pass

    def delete_all(self):
        pass


class AnnouncementRepo(BaseRepo):

    def get_by_student(self, std):
        pass


__all__ = (
    'StudyModel', 'ClassModel', 'StudentModel', 'TokenModel', 'AdminModel', 'AnnouncementModel',
    'StudyRepo', 'StudentRepo', 'ClassRepo', 'StudentRepo', 'TokenRepo', 'AdminRepo', 'AnnouncementRepo'
)