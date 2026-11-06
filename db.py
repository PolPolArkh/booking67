from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Твой Postgres
DBURL = "postgresql+psycopg://postgres:Mega5493257@127.0.0.1:5432/booking"
engine = create_engine(DBURL, client_encoding='utf8')
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()