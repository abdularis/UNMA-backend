# announcements.py
# Created by abdularis on 20/10/17

import uuid
import time
import datetime
import logging
import os
import requests

from flask import render_template, request, url_for, g, abort, send_from_directory, flash
from flask.views import MethodView
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, TextAreaField, RadioField, SelectMultipleField
from wtforms.validators import InputRequired

import udas.fcm as fcm
from udas.ajaxutil import create_response, STAT_SUCCESS, STAT_INVALID, STAT_ERROR
from udas.common import get_uploaded_file_folder, save_uploaded_file, decorate_function, CrudRouter
from udas.database import db_session
from udas.models import Announcement, Student, StudentToken, StudentAnnouncementAssoc, Admin, Study, Class
from udas.session import LoginRequired
from udas.htmlfilter import filter_html
from udas import app

render_template = decorate_function(render_template, page='publish')


class AnnounceForm(FlaskForm):
    title = StringField('Judul', validators=[InputRequired()])
    description = TextAreaField('Deskripsi/Isi')
    recv_type = RadioField('Tipe Penerima', validators=[InputRequired()],
                           coerce=int, choices=[(1, 'Prodi'), (2, 'Kelas'), (3, 'Mahasiswa')],
                           default=1)
    receiver = SelectMultipleField('Penerima',
                                   validators=[InputRequired()],
                                   coerce=int, choices=[])
    attachment = FileField('Attachment',
                           validators=[FileAllowed(['png', 'jpg', 'jpeg', 'bmp', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'],
                                                    'Tipe file tidak didukung.')])

    def fill_receiver_with_study_progs(self):
        if g.is_admin:
            self.receiver.choices = [(obj.id, obj.name) for obj in db_session.query(Study).all()]
        else:
            publisher = db_session.query(Admin).filter(Admin.username == g.curr_user).first()
            self.receiver.choices = [(obj.id, obj.name) for obj in publisher.studies]

    def fill_receiver_with_classes(self):
        if g.is_admin:
            self.receiver.choices = [(obj.id, str(obj))
                                     for obj in
                                     db_session.query(Class).order_by(Class.year.asc(), Class.study_id.asc()).all()]
        else:
            pub = db_session.query(Admin).filter(Admin.username == g.curr_user).first()
            self.receiver.choices = []
            for study in pub.studies:
                [self.receiver.choices.append((obj.id, str(obj))) for obj in study.classes]

    def fill_receiver_with_students(self):
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

    def __init__(self, recv_type=None):
        super().__init__(csrf_enabled=False)
        if recv_type:
            self.recv_type.data = recv_type

        if self.recv_type.data == 1:
            # Prodi
            self.fill_receiver_with_study_progs()
        elif self.recv_type.data == 2:
            # Kelas
            self.fill_receiver_with_classes()
        elif self.recv_type.data == 3:
            # Students
            self.fill_receiver_with_students()


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
    if g.is_admin:
        results = db_session.query(Announcement).order_by(Announcement.id.desc()).all()
    else:
        publisher = db_session.query(Admin).filter(Admin.username == g.curr_user).first()
        results = db_session.query(Announcement) \
            .filter(Announcement.publisher == publisher) \
            .order_by(Announcement.id.desc()) \
            .all()
    results = [AnnouncementModelView(res) for res in results]
    return render_template('admin/partials/anc/announce_list.html', objs=results)


def get_announcement(anc_public_id):
    return db_session.query(Announcement).filter(Announcement.public_id == str(anc_public_id)).first()


class _CreateView(MethodView):
    decorators = [LoginRequired('admin.login')]

    def get(self):
        if 'recvtype' in request.args:
            recv_type = int(request.args['recvtype'])
            form = AnnounceForm(recv_type=recv_type)
            html_data = render_template('admin/partials/anc/announce_receiver_selection.html', obj=form.receiver)
            return create_response(STAT_SUCCESS, html_extra=html_data)
        form = AnnounceForm()
        return create_response(STAT_SUCCESS, html_form=self.render_form(form))

    def post(self):
        form = AnnounceForm()
        if form.validate_on_submit():
            anc = Announcement()
            anc.public_id = str(uuid.uuid4())
            anc.date_created = time.time()
            anc.last_updated = anc.date_created
            anc.publisher = db_session.query(Admin).filter(Admin.username == g.curr_user).first()
            anc.title = form.title.data
            anc.description = filter_html(form.description.data)

            students = []
            if form.recv_type.data == 1:
                # Prodi
                students = db_session.query(Student) \
                    .filter(Study.id.in_(form.receiver.data),
                            Class.study_id == Study.id,
                            Student.class_id == Class.id) \
                    .all()
            elif form.recv_type.data == 2:
                # Kelas
                students = db_session.query(Student) \
                    .filter(Student.class_id.in_(form.receiver.data)) \
                    .all()
            elif form.recv_type.data == 3:
                # Mhs
                students = db_session.query(Student) \
                    .filter(Student.id.in_(form.receiver.data)) \
                    .all()

            for student in students:
                assoc = StudentAnnouncementAssoc()
                assoc.student = student
                assoc.announcement = anc
                anc.students.append(assoc)
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
    def send_notification(anc, students):
        reg_ids = db_session.query(StudentToken.fcm_token) \
            .filter(StudentToken.student_id.in_([std.id for std in students])).all()
        if reg_ids:
            f = fcm.FcmNotification(app.config['FCM_SERVER_KEY'])
            try:
                responses = f.send([obj[0] for obj in reg_ids], data={'title': anc.title})
                for status_code, resp_msg in responses:
                    if status_code == 200 and len(resp_msg.results) > 0:
                        error = resp_msg.results[0][1].get('error')
                        if error in fcm.reg_id_errors:
                            fcm_token = resp_msg.results[0][0]
                            db_session.query(StudentToken).filter(StudentToken.fcm_token == fcm_token).delete()
                            logging.info('Account tokens deleted cause %s is %s' % (fcm_token, error))
                db_session.commit()
            except requests.exceptions.ConnectionError as msg:
                logging.info("Can't send notification - %s" % str(msg))
                flash('Error koneksi ke firebase: gagal mengirim notifikasi ke pengguna!', category='warn')


class _ReadView(MethodView):
    decorators = [LoginRequired('admin.login')]

    def get(self, obj_id=None):
        if request.args.get('act') == 'list':
            return create_response(STAT_SUCCESS, html_list=render_html_list_data())
        elif obj_id:
            if request.args.get('file'):
                file_folder = get_uploaded_file_folder(str(obj_id))
                if os.path.exists(file_folder):
                    return send_from_directory(file_folder, request.args['file'])

            res = db_session.query(Announcement).filter(Announcement.public_id == str(obj_id)).first()
            if res:
                return render_template('admin/announcement_detail.html', obj=AnnouncementModelView(res))
            return abort(404)
        return render_template('admin/announcements.html')


class _UpdateView(MethodView):
    decorators = [LoginRequired('admin.login')]

    def get(self, obj_id):
        # ToDo Implement update on announcement
        return create_response(STAT_ERROR, html_error='<div class="modal-body">Not implemented yet</div>')


class _DeleteView(MethodView):
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
            db_session.delete(model)
            db_session.commit()
            return create_response(STAT_SUCCESS, html_list=render_html_list_data())
        return create_response(STAT_ERROR, html_error=render_template('admin/partials/error/ajax_404.html'))


CrudAnnouncement = CrudRouter(
    'announcement', 'announcements',
    _CreateView,
    _ReadView,
    _UpdateView,
    _DeleteView,
    url_param_t='uuid'
)
