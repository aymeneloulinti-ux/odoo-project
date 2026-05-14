from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()


class Base(DeclarativeBase, MappedAsDataclass):
    pass


db_url = os.getenv('DB_URL')
if not db_url:
    raise ValueError

engine = create_engine(db_url, echo=True)

SessionLocal = sessionmaker(bind=engine)


def get_session():
    return SessionLocal()
