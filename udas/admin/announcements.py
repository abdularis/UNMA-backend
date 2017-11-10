# announcements.py
# Created by abdularis on 20/10/17

import uuid
import time
import datetime
import logging
import os

import requests

import udas.fcm as fcm

from flask import render_template, request, url_for, g, abort, send_from_directory, flash

from udas.ajaxutil import create_response, STAT_SUCCESS
from udas.common import get_uploaded_file_folder, save_uploaded_file, overrides
from udas.database import db_session
from udas.models import Announcement, Student, StudentToken, StudentAnnouncementAssoc, Admin, Study, Class
from udas.login import LoginRequired
from udas.crud import Crud, BaseCreateView, BaseReadView, BaseUpdateView, BaseDeleteView, Interceptor
from udas.forms import AnnounceForm
from udas.decorator import decorate_function
from udas.htmlfilter import filter_html
from udas import app

render_template = decorate_function(render_template, page='publish')


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


class CreateView(BaseCreateView):
    decorators = [LoginRequired('admin.login')]

    def __init__(self):
        super().__init__(render_html_list_data, get_interceptor=Interceptor(self.intercept_get))

    def intercept_get(self):
        if 'recvtype' in request.args:
            recv_type = int(request.args['recvtype'])
            form = AnnounceForm(recv_type=recv_type)
            html_result = render_template('admin/partials/anc/announce_receiver_selection.html',
                                          obj=form.receiver)
            return False, create_response(STAT_SUCCESS, html_extra=html_result)
        return True, None

    @overrides(BaseCreateView)
    def create_form(self, method):
        return AnnounceForm()

    @overrides(BaseCreateView)
    def save_form(self, form):
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
            students = \
                db_session.query(Student) \
                    .filter(Study.id.in_(form.receiver.data),
                            Class.study_id == Study.id,
                            Student.class_id == Class.id) \
                    .all()
        elif form.recv_type.data == 2:
            # Kelas
            students = \
                db_session.query(Student) \
                    .filter(Student.class_id.in_(form.receiver.data)) \
                    .all()
        elif form.recv_type.data == 3:
            # Mhs
            students = \
                db_session.query(Student) \
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

        return True, render_template('admin/partials/anc/announce_save_notif.html')

    @overrides(BaseCreateView)
    def render_form(self, form):
        return render_template(
            'admin/partials/anc/announce_form.html',
            form=form,
            form_title='Publish pengumuman',
            form_action=url_for('admin.announcement_create'),
            form_id='newForm',
            btn_primary='Publish')

    def send_notification(self, anc, students):
        reg_ids = db_session.query(StudentToken.fcm_token) \
            .filter(StudentToken.student_id.in_([std.id for std in students])).all()
        if reg_ids:
            f = fcm.FcmNotification(app.config['FCM_SERVER_KEY'])
            try:
                responses = f.send([obj[0] for obj in reg_ids], {'title': anc.title})
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


class ReadView(BaseReadView):
    decorators = [LoginRequired('admin.login')]

    def __init__(self):
        super().__init__(get_interceptor=Interceptor(self.intercept_get))

    def intercept_get(self, *args, **kwargs):
        if kwargs.get('obj_id') and request.args.get('file'):
            file_folder = get_uploaded_file_folder(str(kwargs['obj_id']))
            if os.path.exists(file_folder):
                return False, send_from_directory(file_folder, request.args['file'])
        return True, None

    @overrides(BaseReadView)
    def render_list(self):
        return render_html_list_data()

    @overrides(BaseReadView)
    def render_detail(self, obj_id):
        res = db_session.query(Announcement).filter(Announcement.public_id == str(obj_id)).first()
        if res:
            return render_template('admin/announcement_detail.html', obj=AnnouncementModelView(res))
        return abort(404)

    @overrides(BaseReadView)
    def render_container(self):
        return render_template('admin/announcements.html')


class UpdateView(BaseUpdateView):
    decorators = [LoginRequired('admin.login')]


class DeleteView(BaseDeleteView):
    decorators = [LoginRequired('admin.login')]

    def render_delete_form(self, model):
        pass

    def delete_model(self, model):
        db_session.delete(model)
        db_session.commit()
        return True, None

    def get_model(self, obj_id):
        return db_session.query(Announcement).filter(Announcement.public_id == obj_id).first()


CrudAnnouncement = Crud(
    'announcement', 'announcements',
    CreateView,
    ReadView,
    UpdateView,
    DeleteView,
    url_param_t='uuid'
)
