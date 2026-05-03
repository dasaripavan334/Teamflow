import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")
SSL_CA_CERT_PATH = os.getenv("SSL_CA_CERT_PATH", "./ca.pem")

connect_args = {}
if os.path.exists(SSL_CA_CERT_PATH):
    connect_args["ssl"] = {"ca": os.path.abspath(SSL_CA_CERT_PATH)}
    print(f"✅ PEM file found: {SSL_CA_CERT_PATH}")
else:
    print("⚠️  PEM not found")

try:
    from sqlalchemy import create_engine, text
    engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT VERSION()"))
        print(f"✅ Connected! MySQL version: {result.fetchone()[0]}")

    import sys
    sys.path.insert(0, '.')
    from database import Base
    import models
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created!")

    with engine.connect() as conn:
        result = conn.execute(text("SHOW TABLES"))
        tables = [r[0] for r in result]
        print(f"   Tables: {', '.join(tables)}")

except Exception as e:
    print(f"❌ Connection failed: {e}")