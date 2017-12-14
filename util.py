# util.py
# Created by abdularis on 08/10/17

import os
import csv

from unma import app
from unma.models import BaseTable, Admin, Department


CSV_ADMIN = 'data/admin.csv'
CSV_PUBLISHERS = 'data/publishers.csv'
CSV_DEPARTMENTS = 'data/departments.csv'


def get_admin():
    with open(CSV_ADMIN) as csv_file:
        data = csv.reader(csv_file)
        for row in data:
            admin = Admin()
            admin.name = row[0]
            admin.username = row[1]
            admin.password = row[2]
            admin.role = 'ADM'
            return admin


def get_publishers():
    publisher_list = []
    with open(CSV_PUBLISHERS) as csv_file:
        data = csv.reader(csv_file)
        for row in data:
            publisher = Admin()
            publisher.name = row[0]
            publisher.username = row[1]
            publisher.password = row[2]
            publisher.role = 'PUB'
            publisher_list.append(publisher)
    return publisher_list


def get_departments():
    departments = []
    with open(CSV_DEPARTMENTS) as csv_file:
        data = csv.reader(csv_file)
        for row in data:
            dep = Department()
            dep.name = row[0]
            departments.append(dep)
    return departments


def gen_db():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    print("[*] Creating database tables...")
    engine = create_engine(app.config['DATABASE'])
    BaseTable.metadata.create_all(engine)

    session = sessionmaker(bind=engine)
    db_session = session()

    # initialize admin
    print("[*] Initialize admin account...")
    db_session.add(get_admin())

    # initialize publishers
    print("[*] Initialize publisher accounts...")
    for pub in get_publishers():
        db_session.add(pub)

    # initialize departments
    print("[*] Initialize departments table...")
    for dept in get_departments():
        db_session.add(dept)

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
