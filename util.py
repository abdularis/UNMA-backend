# util.py
# Created by abdularis on 08/10/17

import os
import csv
import json

from unma.models import BaseTable, Admin, Department, Class, Student, Lecturer

CSV_LECTURERS = 'data/dosen.csv'
CSV_ADMIN = 'data/admin.csv'
CSV_PUBLISHERS = 'data/publishers.csv'
CSV_DEPARTMENTS = 'data/departments.csv'
# CLASSES_DESCRIPTOR = [
#     'data/classes/tii_a_2014.json',
#     'data/classes/tif_a_2014.json',
#     'data/classes/tim_a_2014.json',
#     'data/classes/tis_a_2014.json'
# ]
CLASSES_DESCRIPTOR = [
    'data/classes/tif_kelas_kp_2017.json'
]


def _write_json_config(dict_config, file_path):
    with open(file_path, 'w') as f:
        json.dump(dict_config, f)
        print('\tConfig created: %s' % file_path)


def init_lecturers(db_session):
    print("[*] Import akun dosen")
    with open(CSV_LECTURERS) as csv_file:
        data = csv.reader(csv_file, delimiter=';')
        for row in data:
            lect = Lecturer()
            lect.name = row[0]
            lect.username = row[1]
            lect.password = '123'
            db_session.add(lect)
            print('\tAkun dosen ditambahkan: %s - %s' % (row[0], row[1]))


def init_admin(db_session):
    print("[*] Initialize admin account...")
    with open(CSV_ADMIN) as csv_file:
        data = csv.reader(csv_file)
        for row in data:
            admin = Admin()
            admin.name = row[0]
            admin.username = row[1]
            admin.password = row[2]
            admin.role = 'ADM'
            db_session.add(admin)
            print('\tAdmin ditambahkan: %s' % admin.name)


def init_publishers(db_session):
    print("[*] Initialize publisher accounts...")
    with open(CSV_PUBLISHERS) as csv_file:
        data = csv.reader(csv_file)
        for row in data:
            publisher = Admin()
            publisher.name = row[0]
            publisher.username = row[1]
            publisher.password = row[2]
            publisher.role = 'PUB'
            db_session.add(publisher)
            print('\tPublisher ditambahkan: %s, %s' % (publisher.name, publisher.username))


def init_departments(db_session):
    print("[*] Initialize departments table...")
    with open(CSV_DEPARTMENTS) as csv_file:
        data = csv.reader(csv_file)
        for row in data:
            dep = Department()
            dep.id = row[0]
            dep.name = row[1]
            db_session.add(dep)
            print('\tProdi ditambahkan: %s' % (dep.name))


def init_classes(db_session):
    print("[*] Initialize classes and its students...")
    for file_path in CLASSES_DESCRIPTOR:
        with open(file_path, 'r') as file:
            c_json = json.loads(file.read())
            c = Class()
            c.id = c_json['id']
            c.department_id = c_json['prodi_id']
            c.name = c_json['name']
            c.year = c_json['year']
            c.type = c_json['type']
            db_session.add(c)
            print('\t- Kelas: %d, %d, %s %d' % (c.department_id, c.year, c.name, c.type))

            csv_file_path = c_json['students_csv_path']
            with open(csv_file_path) as csv_file:
                csv_data = csv.reader(csv_file)
                for row in csv_data:
                    stud = Student()
                    stud.name = row[0]
                    stud.username = row[1]
                    stud.class_id = c.id
                    stud.password = '123'
                    db_session.add(stud)
                    print('\t\t- Mahasiswa ditambahkan: %s, %s' % (stud.name, stud.username))


def gen_db(url_connection):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(url_connection)
    print("[*] Creating database tables...")
    BaseTable.metadata.create_all(engine)

    session = sessionmaker(bind=engine)
    db_session = session()

    init_admin(db_session)
    init_publishers(db_session)
    init_departments(db_session)
    init_classes(db_session)
    init_lecturers(db_session)

    db_session.commit()
    cfg = {
        "DATABASE": url_connection,
    }
    _write_json_config(cfg, 'unma/config/db_config.json')
    print("[*] Database successfully generated")


def gen_app_dirs(upload_folder):
    # Initialize all needed directories
    if not os.path.exists(upload_folder):
        print("[*] Creating upload directory...")
        os.makedirs(upload_folder, exist_ok=True)

    _write_json_config({"UPLOAD_FOLDER": upload_folder}, 'unma/config/path_config.json')


def gen_fcm_config(fcm_server_key):
    _write_json_config({"FCM_SERVER_KEY": fcm_server_key}, 'unma/config/fcm_config.json')
