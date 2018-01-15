# announcements.py
# Created by abdularis on 20/10/17

import uuid
import time
import datetime
import logging
import os
import shutil
import requests

from flask import render_template, request, url_for, g, abort, send_from_directory, flash
from flask.views import MethodView
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, TextAreaField, RadioField, SelectMultipleField
from wtforms.validators import InputRequired

import unma.fcm as fcm
from unma.ajaxutil import create_response, STAT_SUCCESS, STAT_INVALID, STAT_ERROR
from unma.common import decorate_function, CrudRouter
from unma.database import db_session
from unma.media import save_uploaded_file, get_upload_folder, get_media_folder
from unma.models import Announcement, Student, StudentToken, StudentAnnouncementAssoc, Admin, Department, Class
from unma.session import LoginRequired
from unma.htmlfilter import filter_html
from unma.unmaapp import app

render_template = decorate_function(render_template, page='publish', title='UNMA - Pengumuman')


RECEIVER_TYPE_DEPARTMENT = (1, 'Prodi')
RECEIVER_TYPE_CLASSES = (2, 'Kelas')
RECEIVER_TYPE_STUDENTS = (3, 'Mahasiswa')


class AnnounceForm(FlaskForm):
    title = StringField('Judul',
                        validators=[InputRequired()])
    description = TextAreaField('Deskripsi/Isi')
    receiver_type = RadioField('Tipe Penerima',
                               validators=[InputRequired()],
                               coerce=int,
                               choices=[RECEIVER_TYPE_DEPARTMENT, RECEIVER_TYPE_CLASSES, RECEIVER_TYPE_STUDENTS],
                               default=RECEIVER_TYPE_DEPARTMENT[0])
    receiver = SelectMultipleField('Penerima',
                                   validators=[InputRequired()],
                                   coerce=int,
                                   choices=[])
    attachment = FileField('Attachment',
                           validators=[FileAllowed(['png', 'jpg', 'jpeg', 'bmp', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'],
                                                    'Tipe file tidak didukung.')])

    def __init__(self):
        super().__init__(csrf_enabled=False)
        self.receiver.choices = []

    def validate_on_submit_update(self):
        return self.is_submitted() and self.title.data and self.description.data


class AnnouncementModelView:
    def __init__(self, announcement):
        self.id = announcement.id
        self.title = announcement.title
        self.description = announcement.description
        self.public_id = announcement.public_id
        self.publisher = announcement.publisher.name
        self.attachment = announcement.attachment
        self.date_created = datetime.datetime.fromtimestamp(announcement.date_created) \
            .strftime('%d %b %Y %H:%M')
        self.last_updated = datetime.datetime.fromtimestamp(announcement.last_updated) \
            .strftime('%d %b %Y %H:%M')
        self.receivers = len(announcement.students)


def render_html_list_data():
    if g.curr_user.is_admin:
        results = db_session.query(Announcement).order_by(Announcement.id.desc()).all()
    else:
        publisher = db_session.query(Admin).filter(Admin.username == g.curr_user.username).first()
        results = db_session.query(Announcement) \
            .filter(Announcement.publisher == publisher) \
            .order_by(Announcement.id.desc()) \
            .all()
    results = [AnnouncementModelView(res) for res in results]
    return render_template('admin/partials/anc/announce_list.html', objs=results)


def get_announcement(anc_public_id):
    return db_session.query(Announcement).filter(Announcement.public_id == str(anc_public_id)).first()


def get_receiver_by_departments():
    if g.curr_user.is_admin:
        return [(obj.id, obj.name) for obj in db_session.query(Department).all()]
    else:
        publisher = db_session.query(Admin).filter(Admin.username == g.curr_user.username).first()
        return [(obj.id, obj.name) for obj in publisher.departments]


def get_receiver_by_classes():
    if g.curr_user.is_admin:
        return [(obj.id, str(obj))
                for obj in
                db_session.query(Class).order_by(Class.year.asc(), Class.department_id.asc()).all()]
    else:
        pub = db_session.query(Admin).filter(Admin.username == g.curr_user.username).first()
        choices = []
        for department in pub.departments:
            [choices.append((obj.id, str(obj))) for obj in department.classes]
        return choices


def get_receiver_by_students():
    if g.curr_user.is_admin:
        return [(obj.id, '%s - %s' % (obj.username, obj.name))
                for obj in
                db_session.query(Student).all()]
    else:
        pub = db_session.query(Admin).filter(Admin.username == g.curr_user.username).first()
        choices = []
        for department in pub.departments:
            for cls in department.classes:
                for student in cls.students:
                    choices.append((student.id, '%s - %s' % (student.username, student.name)))
        return choices


def get_receiver_list(receiver_type):
    if receiver_type == RECEIVER_TYPE_DEPARTMENT[0]:
        return get_receiver_by_departments()
    elif receiver_type == RECEIVER_TYPE_CLASSES[0]:
        return get_receiver_by_classes()
    elif receiver_type == RECEIVER_TYPE_STUDENTS[0]:
        return get_receiver_by_students()
    return []


class CreateView(MethodView):
    decorators = [LoginRequired('admin.login')]

    def get(self):
        if 'receiver_type' in request.args:
            recv_type = int(request.args['receiver_type'])
            form = AnnounceForm()
            form.receiver.choices = get_receiver_list(recv_type)
            html_data = render_template('admin/partials/anc/announce_receiver_selection.html', obj=form.receiver)
            return create_response(STAT_SUCCESS, html_extra=html_data)
        form = AnnounceForm()
        form.receiver.choices = get_receiver_list(form.receiver_type.data)
        return create_response(STAT_SUCCESS, html_form=self.render_form(form))

    def post(self):
        form = AnnounceForm()
        form.receiver.choices = get_receiver_list(form.receiver_type.data)
        if form.validate_on_submit():
            anc = Announcement()
            anc.public_id = str(uuid.uuid4())
            anc.date_created = time.time()
            anc.last_updated = anc.date_created
            anc.publisher = db_session.query(Admin).filter(Admin.username == g.curr_user.username).first()
            anc.title = form.title.data
            anc.description = filter_html(form.description.data)

            students = self.get_students_from_receiver_type(form)
            self.associate_announcement_with_students(anc, students)

            attachment_filename = save_uploaded_file(anc.public_id, form.attachment.data)
            if attachment_filename:
                anc.attachment = attachment_filename
            db_session.add(anc)
            db_session.commit()

            flash('Pengumuman berhasil di publish!', category='succ')

            self.send_notification(anc, students)

            html_extra_msg = render_template('admin/partials/anc/announce_save_notif.html')
            return create_response(STAT_SUCCESS, html_list=render_html_list_data(), html_extra=html_extra_msg)
        else:
            return create_response(STAT_INVALID, html_form=self.render_form(form))

    @staticmethod
    def render_form(form):
        return render_template(
            'admin/partials/anc/announce_form.html',
            form=form,
            form_title='Publish pengumuman',
            form_action=url_for('admin.announcement_create'),
            form_id='newForm',
            btn_primary='Publish')

    @staticmethod
    def associate_announcement_with_students(anc, students):
        for student in students:
            assoc = StudentAnnouncementAssoc()
            assoc.student = student
            assoc.announcement = anc
            anc.students.append(assoc)

    @staticmethod
    def get_students_from_receiver_type(form):
        students = []
        if form.receiver_type.data == RECEIVER_TYPE_DEPARTMENT[0]:
            # Prodi
            students = db_session.query(Student) \
                .filter(Department.id.in_(form.receiver.data),
                        Class.department_id == Department.id,
                        Student.class_id == Class.id) \
                .all()
        elif form.receiver_type.data == RECEIVER_TYPE_CLASSES[0]:
            # Kelas
            students = db_session.query(Student) \
                .filter(Student.class_id.in_(form.receiver.data)) \
                .all()
        elif form.receiver_type.data == RECEIVER_TYPE_STUDENTS[0]:
            # Mhs
            students = db_session.query(Student) \
                .filter(Student.id.in_(form.receiver.data)) \
                .all()
        return students

    @staticmethod
    def send_notification(anc, students):
        reg_ids = db_session.query(StudentToken.fcm_token) \
            .filter(StudentToken.student_id.in_([std.id for std in students])).all()
        if reg_ids:
            f = fcm.FcmNotification(app.config['FCM_SERVER_KEY'])
            try:
                data = {
                    'id': anc.public_id,
                    'title': anc.title,
                    'desc_size': len(anc.description) if anc.description else None,
                    'attachment': anc.attachment
                }
                responses = f.send([obj[0] for obj in reg_ids], data=data)
                for status_code, resp_msg in responses:
                    if status_code == 200 and len(resp_msg.results) > 0:
                        for result in resp_msg.results:
                            error = result[1].get('error')
                            if error in fcm.reg_id_errors:
                                fcm_token = result[0]
                                db_session.query(StudentToken).filter(StudentToken.fcm_token == fcm_token).delete()
                                logging.info('Account tokens deleted cause %s is %s' % (fcm_token, error))

                db_session.commit()
                return True
            except requests.exceptions.ConnectionError as msg:
                logging.info("Connection error can't send notification - %s" % str(msg))
                flash('Error koneksi ke firebase: gagal mengirim notifikasi ke pengguna!', category='warn')
                return False
        flash('Tidak ada penerima yang login untuk dikirim notifikasi!', category='warn')
        return False


class AnnouncementReceiverDetailViewModel:

    def __init__(self, announcement):
        self.announcement = AnnouncementModelView(announcement)
        self.receivers = announcement.students


class ReadView(MethodView):
    decorators = [LoginRequired('admin.login')]

    def get(self, obj_id=None):
        if request.args.get('act') == 'list':
            return create_response(STAT_SUCCESS, html_list=render_html_list_data())
        elif obj_id:
            if request.args.get('file'):
                file_folder = get_upload_folder(str(obj_id))
                if os.path.exists(file_folder):
                    return send_from_directory(file_folder, request.args['file'], as_attachment=True)

            model = get_announcement(obj_id)
            if model:
                if request.args.get('act') == 'receiver_detail':
                    receiver_detail = AnnouncementReceiverDetailViewModel(model)
                    return render_template('admin/announcement_receiver_detail.html', obj=receiver_detail)
                elif request.args.get('act') == 'resend_notification':
                    students = db_session.query(Student).filter(StudentAnnouncementAssoc.announce_id == model.id, Student.id == StudentAnnouncementAssoc.student_id).all()
                    print("Students: %d" % len(students))
                    if CreateView.send_notification(model, students):
                        flash('Notifikasi berhasil dikirim!', category='succ')
                    html_extra = render_template('admin/partials/anc/announce_save_notif.html')
                    return create_response(STAT_SUCCESS, html_extra=html_extra)
                return render_template('admin/announcement_detail.html', obj=AnnouncementModelView(model))
            return abort(404)
        return render_template('admin/announcements.html')


class UpdateView(MethodView):
    decorators = [LoginRequired('admin.login')]

    def get(self, obj_id):
        model = get_announcement(obj_id)
        if model:
            form = AnnounceForm()
            form.title.data = model.title
            form.description.data = model.description
            form.attachment.data = "Hello world"
            form.receiver.choices = get_receiver_by_departments()

            html_form = self.render_form(form, model)
            return create_response(STAT_SUCCESS, html_form=html_form)
        return create_response(STAT_ERROR, html_error='Object not found!')

    def post(self, obj_id):
        model = get_announcement(obj_id)
        if model:
            form = AnnounceForm()
            form.receiver.choices = get_receiver_list(form.receiver_type.data)

            if form.validate_on_submit_update():
                model.title = form.title.data
                model.description = filter_html(form.description.data)
                model.last_updated = time.time()

                students = []
                if form.receiver.data:
                    db_session.query(StudentAnnouncementAssoc)\
                        .filter(StudentAnnouncementAssoc.announce_id == model.id).delete()
                    students = CreateView.get_students_from_receiver_type(form)
                    CreateView.associate_announcement_with_students(model, students)
                else:
                    for student_assoc in model.students:
                        students.append(student_assoc.student)
                        student_assoc.read = False
                        print("read = False")

                if form.attachment.data:
                    attachment_filename = save_uploaded_file(model.public_id, form.attachment.data)
                    if attachment_filename:
                        model.attachment = attachment_filename
                db_session.commit()

                CreateView.send_notification(model, students)

                flash('Pengumuman berhasil di Update!', category='succ')

                html_extra = url_for('admin.announcement_read', obj_id=model.public_id)
                return create_response(STAT_SUCCESS, html_extra=html_extra)
            return create_response(STAT_INVALID, html_form=self.render_form(form, model))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    @staticmethod
    def render_form(form, model):
        attach_file_name = model.attachment if model.attachment else 'Tidak ada attachment'
        receiver_summary = str(len(model.students)) + " Mahasiswa menerima pesan ini"

        return render_template(
            'admin/partials/anc/announce_form_update.html',
            form=form,
            form_title='Update pengumuman',
            form_action=url_for('admin.announcement_update', obj_id=model.public_id),
            form_id='updateForm',
            btn_primary='Republish',
            receiver_summary=receiver_summary,
            attach_file_name=attach_file_name)


class DeleteView(MethodView):
    decorators = [LoginRequired('admin.login')]

    def get(self, obj_id):
        model = get_announcement(obj_id)
        if model:
            return create_response(STAT_SUCCESS,
                                   html_form=render_template('admin/partials/anc/announce_delete.html', obj=model))
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))

    def post(self, obj_id):
        model = get_announcement(obj_id)
        if model:
            if model.attachment:
                shutil.rmtree(get_media_folder(model.public_id), ignore_errors=True)
            db_session.delete(model)
            db_session.commit()
            if request.args.get('return') == 'redirect':
                return create_response(STAT_SUCCESS, html_extra=url_for('admin.announcement_read'))
            return create_response(STAT_SUCCESS, html_list=render_html_list_data())
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))


CrudAnnouncement = CrudRouter(
    'announcement', 'announcements',
    CreateView,
    ReadView,
    UpdateView,
    DeleteView,
    url_param_t='uuid'
)
