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
CLASSES_DESCRIPTOR = [
    'data/classes/tif_kelas_kp_2017.json'
]
# CLASSES_DESCRIPTOR = [
#     'data/classes/tii_a_2014.json',
#     'data/classes/tif_a_2014.json',
#     'data/classes/tim_a_2014.json',
#     'data/classes/tis_a_2014.json'
# ]


def _write_json_config(dict_config, file_path):
    with open(file_path, 'w') as f:
        json.dump(dict_config, f)
        print('\tBerkas config dibuat: %s' % file_path)


def import_lecturers(db_session, csv_filename, default_password='123'):
    """
    Import akun dosen dari data csv

    Format csv:
        separator ; (semicolon)
        Nama Dosen;NIDN

    :param db_session: session database
    :param csv_filename: path ke berkas csv
    :param default_password: default password untuk akun
    """

    print("[*] Import akun dosen %s" % csv_filename)
    with open(csv_filename) as csv_file:
        data = csv.reader(csv_file, delimiter=';')
        for row in data:
            lect = Lecturer()
            lect.name = row[0]
            lect.username = row[1]
            lect.password = default_password
            db_session.add(lect)
            print('\t- Akun dosen ditambahkan: %s - %s' % (row[0], row[1]))


def import_admin(db_session, csv_filename, default_password='123'):
    """
    Import akun admin
    Format csv: Name,Username

    :param db_session: session database
    :param csv_filename: path ke berkas csv
    :param default_password: default password untuk akun
    """

    print("[*] Import akun admin %s" % csv_filename)
    with open(csv_filename) as csv_file:
        data = csv.reader(csv_file)
        for row in data:
            admin = Admin()
            admin.name = row[0]
            admin.username = row[1]
            admin.password = default_password
            admin.role = 'ADM'
            db_session.add(admin)
            print('\t- Admin ditambahkan: %s' % admin.name)


def import_publishers(db_session, csv_filename, default_password='123'):
    """
    Import akun publisher
    Format csv: Name,Username

    :param db_session: session database
    :param csv_filename: path ke berkas csv
    :param default_password: default password untuk akun
    """

    print("[*] Import akun publisher %s" % csv_filename)
    with open(csv_filename) as csv_file:
        data = csv.reader(csv_file)
        for row in data:
            publisher = Admin()
            publisher.name = row[0]
            publisher.username = row[1]
            publisher.password = default_password
            publisher.role = 'PUB'
            db_session.add(publisher)
            print('\t- Publisher ditambahkan: %s, %s' % (publisher.name, publisher.username))


def import_departments(db_session, csv_filename):
    """
    Import data program studi
    Format csv: Id Prodi,Nama Prodi

    :param db_session: session database
    :param csv_filename: path ke berkas csv
    """
    print("[*] Import akun prodi (departments) %s" % csv_filename)
    with open(csv_filename) as csv_file:
        data = csv.reader(csv_file)
        for row in data:
            dep = Department()
            dep.id = row[0]
            dep.name = row[1]
            db_session.add(dep)
            print('\t- Prodi ditambahkan: %s' % (dep.name))


def import_classes(db_session, json_filename_list, student_default_password='123'):
    """
    Import data kelas berserta dengan akun mahasiswa-nya
    Format json:
    {
        "id": angka unit sebagai id kelas,
        "prodi_id": id untuk prodi kelas ini,
        "name": nama kelas seperti 'A',
        "year": tahung angkatan seperti 2014,
        "type": tipe kelas 1 untuk regular dan 2 untuk karyawan,
        "students_csv_path": path ke file csv yang berisi daftar data mahasiswa
    }
    Format csv untuk field students_csv_path: Nama,NPM

    :param db_session: session database
    :param json_filename_list: list untuk daftar path ke berkas json
    :param student_default_password: default password untuk setiap akun mahasiswa
    """

    print("[*] Import data kelas dan mahasiswa")
    for file_path in json_filename_list:
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
                    stud.password = student_default_password
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

    import_admin(db_session, CSV_ADMIN)
    import_publishers(db_session, CSV_PUBLISHERS)
    import_departments(db_session, CSV_DEPARTMENTS)
    import_classes(db_session, CLASSES_DESCRIPTOR)
    import_lecturers(db_session, CSV_LECTURERS)

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
