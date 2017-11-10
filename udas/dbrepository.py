# dbrepository.py
# Created by abdularis on 10/11/17

from udas.database import db_session
from udas.models import Study, Class, Student, StudentToken, Admin, Announcement
from udas.repository import *


class DbStudyRepo(StudyRepo):

    @staticmethod
    def map(study):
        model = StudyModel()
        model.id = study.id
        model.name = study.name
        model.raw = study
        return model

    def update_by_id(self, obj_id, updated_obj):
        if updated_obj.raw:
            updated_obj.raw.id = updated_obj.id
            updated_obj.raw.name = updated_obj.name
            db_session.commit()

    def delete_by_id(self, obj_id):
        std = db_session.query(Study).filter(Study.id == obj_id).first()
        if std:
            db_session.delete(std)
            db_session.commit()
            return True
        return False

    def get_by_student(self, std):
        study = db_session.query(Study).filter(Class.id == std.class_id, Class.study_id == Study.id).first()
        return DbStudyRepo.map(study)

    def get_by_id(self, obj_id):
        std = db_session.query(Study).filter(Study.id == obj_id).first()
        return DbStudyRepo.map(std) if std else None

    def get_all(self):
        students = db_session.query(Study).all()
        return [DbStudyRepo.map(obj) for obj in students]

    def add(self, new_obj):
        study = Study(name=new_obj.name)
        db_session.add(study)
        db_session.commit()

        new_obj.id = study.id
        new_obj.raw = study


class DbClassRepo(ClassRepo):

    @staticmethod
    def map(cls):
        model = ClassModel()
        model.id = cls.id
        model.name = cls.name
        model.study_id = cls.study_id
        model.type = cls.type
        model.year = cls.year
        model.raw = cls
        return model

    def update_by_id(self, obj_id, updated_obj):
        if updated_obj.raw:
            updated_obj.raw.study_id = updated_obj.study_id
            updated_obj.raw.name = updated_obj.name
            updated_obj.raw.year = updated_obj.year
            updated_obj.raw.type = updated_obj.type
            db_session.commit()

    def delete_by_id(self, obj_id):
        cls = db_session.query(Class).filter(Class.id == obj_id).first()
        if cls:
            db_session.delete(cls)
            db_session.commit()
            return True
        return False

    def add(self, new_obj):
        cls = Class(study_id=new_obj.study_id,
                    name=new_obj.name,
                    year=new_obj.year,
                    type=new_obj.type)
        db_session.add(cls)
        db_session.commit()
        new_obj.id = cls.id
        new_obj.raw = cls

    def get_study_program(self, cls):
        return DbStudyRepo.map(cls.raw.study)

    def get_by_study_programs(self, study_programs):
        ids = [obj.id for obj in study_programs]
        classes = db_session.query(Class).filter(Class.study_id.in_(ids)).all()
        return [DbClassRepo.map(obj) for obj in classes]

    def get_by_id(self, obj_id):
        cls = db_session.query(Class).filter(Class.id == obj_id).first()
        return DbClassRepo.map(cls) if cls else None

    def get_all(self):
        classes = db_session.query(Class).all()
        return [DbClassRepo.map(obj) for obj in classes]


class DbStudentRepo(StudentRepo):

    @staticmethod
    def map(std):
        model = StudentModel(id=std.id,
                             class_id=std.class_id,
                             name=std.name,
                             username=std.username,
                             password=std.password,
                             date_created=std.date_created,
                             last_login=std.last_login)
        model.raw = std
        return model

    def update_by_id(self, obj_id, updated_obj):
        if updated_obj.raw:
            updated_obj.raw.name = updated_obj.name
            updated_obj.raw.username = updated_obj.username
            updated_obj.raw.password = updated_obj.password
            updated_obj.raw.class_id = updated_obj.class_id
            updated_obj.raw.date_created = updated_obj.date_created
            updated_obj.raw.last_login = updated_obj.last_login
            db_session.commit()

    def delete_by_id(self, obj_id):
        std = db_session.query(Student).filter(Student.id == obj_id).first()
        if std:
            db_session.delete(std)
            db_session.commit()
            return True
        return False

    def add(self, new_obj):
        std = Student()
        std.name = new_obj.name
        std.username = new_obj.username
        std.password = new_obj.password
        std.class_id = new_obj.class_id
        std.date_created = new_obj.date_created
        std.last_login = new_obj.last_login
        db_session.add(std)
        db_session.commit()
        new_obj.id = std.id
        new_obj.raw = std

    def check_for_account(self, username, password):
        std = db_session.query(Student).filter(Student.username == username).first()
        if std:
            model = DbStudentRepo.map(std)
            if model.verify_password(password):
                return model
        return None

    def get_by_study_program(self, study):
        students = db_session.query(Student) \
                    .filter(Study.id == study.id,
                            Class.study_id == Study.id,
                            Student.class_id == Class.id) \
                    .all()
        return [DbStudentRepo.map(obj) for obj in students]

    def get_by_class(self, cls):
        students = db_session.query(Student).filter(Student.class_id == cls.id).all()
        return [DbStudentRepo.map(obj) for obj in students]

    def get_by_id(self, obj_id):
        std = db_session.query(Student).filter(Student.id == obj_id).first()
        return DbStudentRepo.map(std)

    def get_all(self):
        students = db_session.query(Student).all()
        return [DbStudentRepo.map(obj) for obj in students]


class DbTokenRepo(TokenRepo):

    def delete_by(self, stud_id=None, acc_token=None, fcm_token=None):
        token = self.get_token(stud_id, acc_token, fcm_token)
        db_session.delete(token)
        db_session.commit()

    def get_by(self, student_id=None, acc_token=None, fcm_token=None):
        token = self.get_token(student_id, acc_token, fcm_token)
        return TokenModel(student_id=token.student_id,
                          access_token=token.acc_token,
                          fcm_token=token.fcm_token)

    def update(self, student_id, acc_token=None, fcm_token=None):
        token = self.get_token(student_id)
        token.acc_token = acc_token
        token.fcm_token = fcm_token
        db_session.commit()

    def get_token(self, stud_id=None, acc_token=None, fcm_token=None):
        filters = []
        if stud_id:
            filters.append(StudentToken.id == stud_id)
        if acc_token:
            filters.append(StudentToken.acc_token == acc_token)
        if fcm_token:
            filters.append(StudentToken.fcm_token == fcm_token)
        return db_session.query(StudentToken) \
            .filter(filters) \
            .first()


class DbAdminRepo(AdminRepo):

    @staticmethod
    def map(adm):
        if not adm:
            return None
        model = AdminModel(id=adm.id,
                           name=adm.name,
                           username=adm.username,
                           password=adm.password,
                           date_created=adm.date_created,
                           last_login=adm.last_login,
                           role=adm.role)
        model.raw = adm
        return model

    def update_by_id(self, obj_id, updated_obj, study_prog_ids):
        if updated_obj.raw:
            updated_obj.raw.name = updated_obj.name
            updated_obj.raw.username = updated_obj.username
            updated_obj.raw.password = updated_obj.password
            updated_obj.raw.date_created = updated_obj.date_created
            updated_obj.raw.last_login = updated_obj.last_login
            updated_obj.raw.role = updated_obj.role
            if study_prog_ids:
                updated_obj.raw.studies = db_session.query(Study).filter(Study.id.in_(study_prog_ids)).all()
            db_session.commit()

    def delete_by_id(self, obj_id):
        adm = db_session.query(Admin).filter(Admin.id == obj_id).first()
        if adm:
            db_session.delete(adm)
            db_session.commit()
            return True
        return False

    def add(self, new_obj, study_prog_ids):
        adm = Admin()
        adm.name = new_obj.name
        adm.username = new_obj.username
        adm.password = new_obj.password
        adm.date_created = new_obj.date_created
        adm.last_login = new_obj.last_login
        adm.role = new_obj.role
        adm.studies = db_session.query(Study).filter(Study.id.in_(study_prog_ids)).all()
        db_session.add(adm)
        db_session.commit()
        new_obj.id = adm.id
        new_obj.raw = adm

    def check_for_account(self, username, password):
        adm = db_session.query(Admin).filter(Admin.username == username).first()
        if adm:
            model = DbAdminRepo.map(adm)
            if model.verify_password(password):
                return model
        return None

    def get_publisher_by_id(self, obj_id):
        adm = db_session.query(Admin).filter(Admin.id == obj_id, Admin.role == 'PUB').first()
        return DbAdminRepo.map(adm)

    def get_publisher_by_username(self, username):
        adm = db_session.query(Admin).filter(Admin.username == username, Admin.role == 'PUB').first()
        return DbAdminRepo.map(adm)

    def get_allowed_study_programs(self, adm):
        return [DbStudyRepo.map(obj) for obj in adm.raw.studies]

    def get_all_publisher(self):
        admins = db_session.query(Admin).filter(Admin.role == 'PUB').all()
        return [DbAdminRepo.map(obj) for obj in admins]


class DbAnnouncementRepo(AnnouncementRepo):

    @staticmethod
    def map(anc):
        m = AnnouncementModel(id=anc.id,
                              public_id=anc.public_id,
                              publisher_id=anc.publisher_id,
                              title=anc.title,
                              description=anc.description,
                              attachment=anc.attachment,
                              date_created=anc.date_created,
                              last_updated=anc.last_updated)
        m.raw = anc
        return m

    def update_by_id(self, obj_id, updated_obj):
        if updated_obj.raw:
            updated_obj.raw.public_id = updated_obj.public_id
            updated_obj.raw.publisher_id = updated_obj.publisher_id
            updated_obj.raw.title = updated_obj.title
            updated_obj.raw.description = updated_obj.description
            updated_obj.raw.attachment = updated_obj.attachment
            updated_obj.raw.date_created = updated_obj.date_created
            updated_obj.raw.last_updated = updated_obj.last_updated
            db_session.commit()

    def delete_by_id(self, obj_id):
        anc = db_session.query(Announcement).filter(Announcement.id == obj_id).first()
        if anc:
            db_session.delete(anc)
            db_session.commit()
            return True
        return False

    def get_by_id(self, obj_id):
        anc = db_session.query(Announcement).filter(Announcement.id == obj_id).first()
        return self.map(anc)

    def get_by_public_id(self, public_id):
        anc = db_session.query(Announcement).filter(Announcement.public_id == public_id).first()
        return self.map(anc)

    def get_by_student_id(self, std_id):
        std = db_session.query(Student).filter(Student.id == std_id).first()
        if std:
            announcements = std.announcements
            return [self.map(obj) for obj in announcements]
        return None

    def get_by_publisher_id(self, pub_id):
        announcements = db_session.query(Announcement) \
            .filter(Announcement.publisher_id == pub_id) \
            .order_by(Announcement.id.desc()) \
            .all()
        return [self.map(obj) for obj in announcements]

    def add(self, new_obj):
        anc = Announcement()
        anc.public_id = new_obj.public_id
        anc.publisher_id = new_obj.publisher_id
        anc.title = new_obj.title
        anc.description = new_obj.description
        anc.attachment = new_obj.attachment
        anc.date_created = new_obj.date_created
        anc.last_updated = new_obj.last_updated
        db_session.add(anc)
        db_session.commit()
        new_obj.id = anc.id
        new_obj.raw = anc

    def get_all(self):
        announcements = db_session.query(Announcement)\
            .order_by(Announcement.last_updated.desc())\
            .all()
        return [self.map(obj) for obj in announcements]


class ClassesMapper(StudyModel.ClassesMapper):
    def __call__(self, study_program):
        return [DbClassRepo.map(obj) for obj in study_program.raw.classes]


class StudentMapper(ClassModel.StudentMapper):
    def __call__(self, cls):
        return [DbStudentRepo.map(obj) for obj in cls.raw.students]


class StudyMapper(ClassModel.StudyMapper):
    def __call__(self, cls):
        return DbStudyRepo.map(cls.raw.study)


class AnnouncementMapper(StudentModel.AnnouncementMapper):
    def __call__(self, student):
        return [DbAnnouncementRepo.map(obj) for obj in student.raw.announcements]


class PermissionsMapper(AdminModel.PermissionsMapper):
    def __call__(self, admin):
        return [DbStudyRepo.map(obj) for obj in admin.raw.studies]


class PublisherMapper(AnnouncementModel.PublisherMapper):
    def __call__(self, announcement):
        return DbAdminRepo.map(announcement.raw.publisher)


# init
StudyModel.classes_mapper = ClassesMapper()
ClassModel.students_mapper = StudentMapper()
ClassModel.study_mapper = StudyMapper()
StudentModel.announcements_mapper = AnnouncementMapper()
AnnouncementModel.publisher_mapper = PublisherMapper()
