from sqlalchemy import create_engine, URL
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

url = URL.create("postgresql+psycopg2", username="postgres", password="postgres", host="localhost", database="milidu_prod")
engine = create_engine(url)
db_session = scoped_session(sessionmaker(autocommit=False,
                           autoflush=False,
                           bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import models
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)