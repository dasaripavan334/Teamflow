import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")
SSL_CA_CERT_PATH = os.getenv("SSL_CA_CERT_PATH", "./ca.pem")

connect_args = {}
if SSL_CA_CERT_PATH and os.path.exists(SSL_CA_CERT_PATH):
    connect_args["ssl"] = {"ca": os.path.abspath(SSL_CA_CERT_PATH)}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()