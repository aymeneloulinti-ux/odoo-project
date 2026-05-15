import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv('DB_URL')
if not db_url:
    raise ValueError

engine = create_engine(db_url, echo=True)

SessionLocal = sessionmaker(bind=engine)


def get_session():
    return SessionLocal()
