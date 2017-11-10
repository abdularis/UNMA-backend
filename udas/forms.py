# forms.py
# Created by abdularis on 08/10/17

from flask import g, flash
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, IntegerField, SelectField, \
    SelectMultipleField, TextAreaField, ValidationError, RadioField
from wtforms.validators import InputRequired

from udas.database import db_session
from udas.models import Study, Class, Student, Admin, ClassTypes
from udas.repofactory import rf


class UniqueValue(object):

    def __init__(self, model_t, model_id_t, edit_mode=False, last_value='', message="This field must be unique"):
        self.message = message
        self.model_t = model_t
        self.model_id_t = model_id_t
        self.edit_mode = edit_mode
        self.last_value = last_value

    def __call__(self, form, field):
        result = db_session.query(self.model_t).filter(self.model_id_t == field.data).first()
        if result:
            if not self.edit_mode or field.data != self.last_value:
                raise ValidationError(self.message)

    @staticmethod
    def set_edit_mode_on_field(field, edit_mode, last_value):
        for validator in field.validators:
            if isinstance(validator, UniqueValue):
                validator.edit_mode = edit_mode
                validator.last_value = last_value


class SwitchableRequired(InputRequired):

    def __init__(self, enable=True, message=None):
        super().__init__(message)
        self.enable = enable

    def __call__(self, form, field):
        if self.enable:
            super().__call__(form, field)


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(message='Username tidak boleh kosong')])
    password = PasswordField('Password', validators=[InputRequired(message='Silakan masukan password')])


class StudyForm(FlaskForm):

    name = StringField('Nama', validators=[InputRequired(message="Nama tidak boleh kosong"),
                                           UniqueValue(Study, Study.name, message="Nama sudah ada. Tidak boleh sama!")])

    def __init__(self, formdata=None, edit_mode=False, last_value=''):
        super().__init__(csrf_enabled=False)
        UniqueValue.set_edit_mode_on_field(self.name, edit_mode, last_value)


class ClassForm(FlaskForm):
    study_program = SelectField('Prodi', validators=[InputRequired()], coerce=int, choices=[])
    name = StringField('Nama', validators=[InputRequired(message='Name harus diisi')])
    year = IntegerField('Tahun', validators=[InputRequired(message='Tahun harus diisi')])
    cls_type = SelectField('Tipe Kelas', validators=[InputRequired()],
                           coerce=int,
                           choices=[t for t in zip(ClassTypes.keys(), ClassTypes.values())])

    def __init__(self, formdata=None):
        super().__init__(csrf_enabled=False)
        self.study_program.choices = [(obj.id, obj.name) for obj in db_session.query(Study).all()]

    def validate(self):
        valid = super().validate()
        if not valid:
            return False

        res = db_session.query(Class) \
            .filter(Class.study_id == self.study_program.data,
                    Class.name == self.name.data,
                    Class.year == self.year.data,
                    Class.type == self.cls_type.data) \
            .first()
        if res:
            flash('Data kelas "%s %s %s %d" sudah ada.' %
                  (dict(self.study_program.choices).get(self.study_program.data),
                   self.name.data, ClassTypes.get(self.cls_type.data), self.year.data))
            return False
        return True


class StudentForm(FlaskForm):
    name = StringField('Nama', validators=[InputRequired()])
    study_program = SelectField('Prodi', coerce=int, choices=[])
    std_class = SelectField('Kelas', validators=[InputRequired()], coerce=int, choices=[])
    username = StringField('Username', validators=[InputRequired(),
                                                   UniqueValue(Student, Student.username, message="Username sudah ada. Tidak boleh sama!")])
    password = StringField('Password', validators=[SwitchableRequired()])

    def __init__(self, formdata=None, edit_mode=False, last_value=None):
        super().__init__(csrf_enabled=False)
        self.study_program.data = 0
        self.study_program.choices = self.get_study_prog_option()
        self.std_class.choices = self.get_classes_option()

        UniqueValue.set_edit_mode_on_field(self.username, edit_mode, last_value)
        self.password.validators[0].enable = not edit_mode

    @staticmethod
    def get_study_prog_option():
        choices = [(0, '--- program studi ---')]
        [choices.append((obj.id, obj.name)) for obj in db_session.query(Study).all()]
        return choices

    @staticmethod
    def get_classes_option(sp_id=None):
        if sp_id and sp_id > 0:
            res = db_session.query(Class)\
                .filter(Class.study_id == sp_id)\
                .order_by(Class.study_id.asc())\
                .all()
        else:
            res = db_session.query(Class).order_by(Class.study_id.asc()).all()
        return [(obj.id, str(obj)) for obj in res]


class PublisherForm(FlaskForm):
    name = StringField('Nama', validators=[InputRequired()])
    username = StringField('Username',
                           validators=[InputRequired(),
                                       UniqueValue(Admin, Admin.username, message="Username sudah ada. Tidak boleh sama!")])
    password = StringField('Password', validators=[SwitchableRequired()])
    allowed_study_program = SelectMultipleField('Izin Publish Ke', validators=[InputRequired()], coerce=int, choices=[])

    def __init__(self, formdata=None, edit_mode=None, last_value=None):
        super().__init__(csrf_enabled=False)
        self.allowed_study_program.choices = [(obj.id, obj.name) for obj in db_session.query(Study).all()]
        self.password.validators[0].enable = not edit_mode
        UniqueValue.set_edit_mode_on_field(self.username, edit_mode, last_value)


class AnnounceForm(FlaskForm):
    title = StringField('Judul', validators=[InputRequired()])
    description = TextAreaField('Deskripsi/Isi')
    recv_type = RadioField('Tipe Penerima', validators=[InputRequired()],
                           coerce=int, choices=[(1, 'Prodi'), (2, 'Kelas'), (3, 'Mahasiswa')],
                           default=1)
    receiver = SelectMultipleField('Penerima',
                                   validators=[InputRequired()],
                                   coerce=int, choices=[])
    attachment = FileField('Attachment', validators=[FileAllowed(['png', 'jpg', 'bmp', 'pdf'], 'Tipe file tidak didukung.')])

    def __init__(self, recv_type=None):
        super().__init__(csrf_enabled=False)
        if recv_type:
            self.recv_type.data = recv_type

        if self.recv_type.data == 1:
            # Prodi
            if g.is_admin:
                study_progs = rf.study_repo().get_all()
            else:
                publisher = rf.admin_repo().get_publisher_by_username(g.curr_user)
                study_progs = rf.admin_repo().get_allowed_study_programs(publisher)
            self.receiver.choices = [(obj.id, obj.name) for obj in study_progs]
        elif self.recv_type.data == 2:
            # Kelas
            if g.is_admin:
                classes = rf.class_repo().get_all()
            else:
                publisher = rf.admin_repo().get_publisher_by_username(g.curr_user)
                study_progs = rf.admin_repo().get_allowed_study_programs(publisher)
                classes = rf.class_repo().get_by_study_programs(study_progs)
            self.receiver.choices = [(obj.id, obj.name) for obj in classes]
        elif self.recv_type.data == 3:
            if g.is_admin:
                self.receiver.choices = [(obj.id, '%s - %s' % (obj.username, obj.name))
                                         for obj in
                                         db_session.query(Student).all()]
            else:
                pub = db_session.query(Admin).filter(Admin.username == g.curr_user).first()
                self.receiver.choices = []
                for study in pub.studies:
                    for cls in study.classes:
                        for student in cls.students:
                            self.receiver.choices.append((student.id, '%s - %s' % (student.username, student.name)))
