from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./hotel.db"     # через лайт потому что с постгресом запарнее из-за гитхаба
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():    
    db = SessionLocal()       #функция для подключения к бд во время работы сервиса, после того как все сделали, то закрывает все 
    try:
        yield db
    finally:
        db.close()