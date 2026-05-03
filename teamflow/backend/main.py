import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from database import engine, Base, SessionLocal
from models import User, UserRole
from auth import hash_password
from routers import auth, projects, tasks

load_dotenv()

Base.metadata.create_all(bind=engine)


def seed_admin():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@gmail.com").first()
        if not admin:
            admin = User(
                name="Admin",
                email="admin@gmail.com",
                password_hash=hash_password("123"),
                role=UserRole.admin,
            )
            db.add(admin)
            db.commit()
            print("✅ Default admin created: admin@gmail.com / 123")
        else:
            print("✅ Admin already exists")
    finally:
        db.close()


seed_admin()

app = FastAPI(
    title="TeamFlow API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

frontend_url = os.getenv("FRONTEND_URL", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    frontend_url,
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5500",
    "http://0.0.0.0:8000",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# members router removed — member endpoints now in projects router
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)


@app.get("/health")
def health():
    return {"status": "ok"}


frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")