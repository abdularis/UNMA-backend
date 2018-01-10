# util.py
# Created by abdularis on 08/10/17

import os
import csv
import json

from unma import app
from unma.models import BaseTable, Admin, Department, Class, Student


CSV_ADMIN = 'data/admin.csv'
CSV_PUBLISHERS = 'data/publishers.csv'
CSV_DEPARTMENTS = 'data/departments.csv'
CSV_CLASSES = 'data/classes.csv'
CLASSES_DESCRIPTOR = [
    'data/classes/tif_a_2014.json'
]


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
                    stud.password = '123456789'
                    db_session.add(stud)
                    print('\t\t- Mahasiswa ditambahkan: %s, %s' % (stud.name, stud.username))


def gen_db():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    print("[*] Creating database tables...")
    engine = create_engine(app.config['DATABASE'])
    BaseTable.metadata.create_all(engine)

    session = sessionmaker(bind=engine)
    db_session = session()

    init_admin(db_session)
    init_publishers(db_session)
    init_departments(db_session)
    init_classes(db_session)

    db_session.commit()
    print("[*] Database successfully generated")


def gen_app_dirs():
    # Initialize all needed directories
    if not os.path.exists(app.instance_path):
        print("[*] Creating instance app directory...")
        os.makedirs(app.instance_path, exist_ok=True)
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        print("[*] Creating upload directory...")
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
