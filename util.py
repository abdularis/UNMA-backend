# util.py
# Created by abdularis on 08/10/17


def gen_db():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from udas import app
    from udas.models import BaseTable, Admin

    engine = create_engine(app.config['DATABASE'])
    BaseTable.metadata.create_all(engine)

    session = sessionmaker(bind=engine)
    db_session = session()
    adm = Admin()
    adm.name = 'Admin'
    adm.username = 'admin'
    adm.password = '123'
    adm.role = 'ADM'

    pub = Admin()
    pub.name = 'Publisher one'
    pub.username = 'pub'
    pub.password = '123'
    pub.role = 'PUB'

    db_session.add(adm)
    db_session.add(pub)
    db_session.commit()
