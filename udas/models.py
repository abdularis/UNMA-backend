# models.py
# Created by abdularis on 15/10/17

from flask_bcrypt import generate_password_hash, check_password_hash

from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey, Table, func, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

BaseTable = declarative_base()


class BaseUser(object):

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    username = Column(String(50), unique=True)
    password = Column(String(128))
    date_created = Column(DateTime, default=func.now())
    last_login = Column(DateTime)


"""
    Tabel assosiasi many-to-many antara tabel publisher (Admin) dengan study
"""
pub_perm_assoc = Table('pub_perm_assoc', BaseTable.metadata,
                       Column('publisher_id', Integer, ForeignKey('admins.id'), primary_key=True),
                       Column('study_id', Integer, ForeignKey('studies.id'), primary_key=True))


class Study(BaseTable):
    __tablename__ = 'studies'

    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True)

    classes = relationship('Class',
                           back_populates='study',
                           cascade='all, delete, delete-orphan')
    admins = relationship('Admin',
                          secondary=pub_perm_assoc)


class _ClassType:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return self.name[:3]


ClassTypes = {
    1: _ClassType(1, 'Reguler'),
    2: _ClassType(2, 'Karyawan')
}


class Class(BaseTable):
    __tablename__ = 'classes'

    id = Column(Integer, primary_key=True)
    study_id = Column(Integer, ForeignKey('studies.id'))
    name = Column(String(10))
    year = Column(Integer)
    type = Column(Integer)

    study = relationship('Study', back_populates='classes')
    students = relationship('Student', back_populates='my_class',
                            cascade='all, delete, delete-orphan')

    def __str__(self):
        return '{} {} {} {}'.format(self.study.name, self.name, self.year, ClassTypes.get(self.type))


class Student(BaseUser, BaseTable):
    __tablename__ = 'students'

    class_id = Column(Integer, ForeignKey('classes.id'))

    my_class = relationship('Class', back_populates='students')
    announcements = relationship('StudentAnnouncementAssoc',
                                 back_populates='student',
                                 cascade='all, delete, delete-orphan')


class StudentToken(BaseTable):
    __tablename__ = 'stud_tokens'

    student_id = Column(Integer, ForeignKey('students.id'), primary_key=True)
    acc_token = Column(String(256), unique=True)
    fcm_token = Column(String(256), unique=True)

    student = relationship('Student')


class Admin(BaseUser, BaseTable):
    __tablename__ = 'admins'

    role = Column(String(3))

    studies = relationship('Study', secondary=pub_perm_assoc)
    announcements = relationship('Announcement', back_populates='publisher',
                                 cascade='all, delete, delete-orphan')


class Announcement(BaseTable):
    __tablename__ = 'announcements'

    id = Column(Integer, primary_key=True)
    public_id = Column(String(48), unique=True)
    publisher_id = Column(Integer, ForeignKey('admins.id'))
    title = Column(String(256))
    description = Column(Text)
    attachment = Column(String(256))
    date_created = Column(Float)
    last_updated = Column(Float)

    publisher = relationship('Admin', back_populates='announcements')
    students = relationship('StudentAnnouncementAssoc',
                            back_populates='announcement',
                            cascade='all, delete, delete-orphan')


class StudentAnnouncementAssoc(BaseTable):
    __tablename__ = 'studs_anns_assoc'

    student_id = Column(Integer, ForeignKey('students.id'), primary_key=True)
    announce_id = Column(Integer, ForeignKey('announcements.id'), primary_key=True)
    read = Column(Boolean, default=False)

    student = relationship('Student', back_populates='announcements')
    announcement = relationship('Announcement', back_populates='students')
