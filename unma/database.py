# database.py
# Created by abdularis on 08/10/17

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from unma.unmaapp import app

engine = create_engine(app.config['DATABASE'])
session = sessionmaker(bind=engine)
db_session = session()
