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
    classes_mapper = None

    def __init__(self, id=None, name=''):
        super().__init__()
        self.id = id
        self.name = name

    @property
    def classes(self):
        return self.classes_mapper(self) if self.classes_mapper else None

    class ClassesMapper:
        def __call__(self, study_program):
            return None


class ClassModel(BaseRepoModel):
    students_mapper = None
    study_mapper = None

    def __init__(self):
        super().__init__()
        self.id = None
        self.study_id = None
        self.name = ''
        self.year = 0
        self.type = 0

    @property
    def students(self):
        return self.students_mapper(self) if self.students_mapper else None

    @property
    def study(self):
        return self.study_mapper(self) if self.study_mapper else None

    class StudentMapper:
        def __call__(self, cls):
            return None

    class StudyMapper:
        def __call__(self, cls):
            return None


class StudentModel(BaseUser):
    announcements_mapper = None

    def __init__(self, id=None, name='', username='', password='', date_created=None, last_login=None, class_id=None,):
        super().__init__(id, name, username, password, date_created, last_login)
        self.class_id = class_id

    @property
    def announcements(self):
        return self.announcements_mapper(self) if self.announcements_mapper else None

    class AnnouncementMapper:
        def __call__(self, student):
            return None


class TokenModel(BaseRepoModel):
    def __init__(self, student_id=None, access_token='', fcm_token=''):
        super().__init__()
        self.student_id = student_id
        self.access_token = access_token
        self.fcm_token = fcm_token


class AdminModel(BaseUser):
    permissions_mapper = None

    def __init__(self, id=None, name='', username='', password='', date_created=None, last_login=None, role=''):
        super().__init__(id, name, username, password, date_created, last_login)
        self.role = role

    @property
    def permissions(self):
        return self.permissions_mapper(self) if self.permissions_mapper else None

    class PermissionsMapper:
        def __call__(self, admin):
            return None


class AnnouncementModel(BaseRepoModel):
    publisher_mapper = None

    def __init__(self, id=None, public_id='', publisher_id=None, title='', description='', attachment=None, date_created=None, last_updated=None):
        super().__init__()
        self.id = None
        self.public_id = ''
        self.publisher_id = None
        self.title = ''
        self.description = ''
        self.attachment = None
        self.date_created = None
        self.last_updated = None

    @property
    def publisher(self):
        return self.publisher_mapper(self) if self.publisher_mapper else None

    class PublisherMapper:
        def __call__(self, announcement):
            return None


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


class AnnouncementRepo(BaseRepo):

    def get_by_public_id(self, public_id):
        pass

    def get_by_student_id(self, std_id):
        pass

    def get_by_publisher_id(self, pub_id):
        pass


__all__ = (
    'StudyModel', 'ClassModel', 'StudentModel', 'TokenModel', 'AdminModel', 'AnnouncementModel',
    'StudyRepo', 'StudentRepo', 'ClassRepo', 'StudentRepo', 'TokenRepo', 'AdminRepo', 'AnnouncementRepo'
)