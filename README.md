# TeamFlow — Team Task Manager

A full-stack project and task management web application with role-based access control, built with FastAPI, MySQL (Aiven Cloud), and vanilla HTML/Tailwind CSS.

---

## Live URLs

| Service | URL |
|---------|-----|
| App | https://teamflow-s3c8.onrender.com |
| API Docs | https://teamflow-s3c8.onrender.com/docs |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5 + Tailwind CSS (CDN) + Vanilla JS |
| Backend | FastAPI (Python 3.11+) |
| Database | MySQL 8.0 — Aiven Cloud |
| Authentication | JWT (python-jose) + bcrypt |
| Deploy | Render (full stack — backend + frontend) |

---

## Project Structure

```
teamflow/
├── backend/
│   ├── main.py                  # FastAPI app entry + admin seeding + static file serving
│   ├── database.py              # Aiven MySQL connection with SSL
│   ├── models.py                # SQLAlchemy ORM models
│   ├── schemas.py               # Pydantic request/response schemas
│   ├── auth.py                  # JWT creation + bcrypt password hashing
│   ├── dependencies.py          # Auth guards (get_current_user, require_admin)
│   ├── routers/
│   │   ├── auth.py              # Register, Login, Me, List Users, Promote/Demote
│   │   ├── projects.py          # Project CRUD + member listing
│   │   └── tasks.py             # Task CRUD + dashboard stats
│   ├── requirements.txt
│   ├── render.yaml              # Render deployment config
│   ├── .env.example             # Environment variable template
│   └── ca.pem                   # Aiven SSL certificate (do not commit)
│
├── frontend/
│   ├── index.html               # Login / Sign Up page
│   ├── dashboard.html           # Stats + My Tasks + User Management (admin)
│   ├── projects.html            # Projects grid with member assignment
│   ├── project-detail.html      # Kanban board + Members tab
│   └── js/
│       ├── env.js               # API base URL config
│       ├── api.js               # Fetch wrapper + Toast + Confirm modal
│       └── navbar.js            # Shared navigation with user dropdown
│
├── README.md
└── .gitignore
```

---

## Database Schema

### users
| Column | Type | Description |
|--------|------|-------------|
| id | VARCHAR(36) | UUID primary key |
| name | VARCHAR(100) | Full name |
| email | VARCHAR(255) | Unique email |
| password_hash | VARCHAR(255) | bcrypt hash |
| role | ENUM | admin / member |
| created_at | DATETIME | Auto timestamp |

### projects
| Column | Type | Description |
|--------|------|-------------|
| id | VARCHAR(36) | UUID primary key |
| name | VARCHAR(150) | Project name |
| description | TEXT | Optional description |
| owner_id | VARCHAR(36) | FK → users.id |
| created_at | DATETIME | Auto timestamp |

### project_members
| Column | Type | Description |
|--------|------|-------------|
| id | VARCHAR(36) | UUID primary key |
| project_id | VARCHAR(36) | FK → projects.id |
| user_id | VARCHAR(36) | FK → users.id |
| role | ENUM | admin / member |
| joined_at | DATETIME | Auto timestamp |

### tasks
| Column | Type | Description |
|--------|------|-------------|
| id | VARCHAR(36) | UUID primary key |
| title | VARCHAR(200) | Task title |
| description | TEXT | Optional details |
| status | ENUM | todo / in_progress / done |
| priority | ENUM | low / medium / high |
| project_id | VARCHAR(36) | FK → projects.id |
| assignee_id | VARCHAR(36) | FK → users.id (nullable) |
| created_by | VARCHAR(36) | FK → users.id |
| due_date | DATETIME | Optional due date |
| created_at | DATETIME | Auto timestamp |
| updated_at | DATETIME | Auto update |

---

## Role-Based Access Control

### Global Roles

| Action | Admin | Member |
|--------|-------|--------|
| Create / Edit / Delete projects | ✅ | ❌ |
| Assign members to projects | ✅ | ❌ |
| Create / Assign / Delete tasks | ✅ | ❌ |
| Update status of own tasks | ✅ | ✅ |
| View assigned projects | ✅ | ✅ |
| View all projects | ✅ | ❌ |
| Promote / Demote users | ✅ | ❌ |
| View all users (dashboard) | ✅ | ❌ |

### Important Rules
- Only **one default admin** exists on first startup (`admin@gmail.com`)
- All new registrations are always **Member** — no role selection on signup
- Only the admin can promote a Member → Admin or demote Admin → Member
- The default admin (`admin@gmail.com`) cannot be demoted
- Members can only change the **status** of tasks **assigned to them**

---

## Application Workflow

### Admin Workflow

```
1. Login
   └── admin@gmail.com / [your admin password]

2. Dashboard
   ├── View stats (projects, tasks, overdue)
   ├── View own assigned tasks
   └── Manage Users panel
       ├── See all registered users
       ├── Promote member → Admin
       └── Demote admin → Member

3. Projects Page
   ├── Create New Project
   │   ├── Enter project name + description
   │   └── Select members from checklist (multi-select)
   ├── Edit project (name/description)
   └── Delete project (with confirmation modal)

4. Project Detail Page
   ├── Board Tab (Kanban)
   │   ├── View tasks in 3 columns: To Do / In Progress / Done
   │   ├── Filter by status and priority
   │   ├── Click any task → Edit full details
   │   │   ├── Title, description, status, priority
   │   │   ├── Assign to a project member
   │   │   └── Set due date
   │   └── Delete task (hover → Delete button)
   └── Members Tab
       └── View all project members and their roles
```

### Member Workflow

```
1. Register
   └── Sign up with name, email, password
       └── Role is always "Member"

2. Wait to be added to a project
   └── Admin adds you during project creation

3. Login → Dashboard
   ├── View stats for your projects only
   └── View tasks assigned to you

4. Projects Page
   └── See only projects you are part of (read-only cards)

5. Project Detail Page
   ├── Board Tab
   │   ├── View all tasks in the project
   │   └── Click your assigned task → Status Picker Modal
   │       ├── Move to: To Do / In Progress / Done
   │       └── (Cannot edit title, priority, or assignee)
   └── Members Tab
       └── View project members (read-only)
```

---

## API Endpoints

### Authentication
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | /auth/register | Public | Register new member |
| POST | /auth/login | Public | Login, returns JWT |
| GET | /auth/me | Authenticated | Get current user |
| GET | /auth/users | Admin only | List all users |
| PUT | /auth/users/{id}/promote | Admin only | Promote to admin |
| PUT | /auth/users/{id}/demote | Admin only | Demote to member |

### Projects
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | /projects/ | Authenticated | List accessible projects |
| POST | /projects/ | Admin only | Create project with members |
| GET | /projects/{id} | Project member | Get project details |
| PUT | /projects/{id} | Admin only | Update project |
| DELETE | /projects/{id} | Admin only | Delete project + tasks |
| GET | /projects/{id}/members | Project member | List project members |

### Tasks
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | /dashboard | Authenticated | Get stats + my tasks |
| GET | /projects/{id}/tasks | Project member | List tasks (filterable) |
| POST | /projects/{id}/tasks | Admin only | Create task |
| GET | /tasks/{id} | Project member | Get task details |
| PUT | /tasks/{id} | Admin / Assignee | Update task |
| DELETE | /tasks/{id} | Admin only | Delete task |

---

## Local Setup

### Prerequisites
- Python 3.11+
- Aiven MySQL database
- `ca.pem` SSL certificate from Aiven

### Backend

```bash
cd teamflow/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env — fill in DATABASE_URL and SECRET_KEY

# Place ca.pem in backend/ folder

# Create database (run once)
python create_db.py

# Start server
uvicorn main:app --reload
```

Backend runs at: http://localhost:8000  
Swagger docs: http://localhost:8000/docs  
App: http://localhost:8000 (frontend served automatically)

---

## Environment Variables

```env
DATABASE_URL=mysql+pymysql://user:password@host:port/teamflow
SSL_CA_CERT_PATH=./ca.pem
SECRET_KEY=your-super-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
FRONTEND_URL=https://teamflow-s3c8.onrender.com
```

---

## Deployment — Render (Full Stack)

1. Push code to GitHub
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect `dasaripavan334/Teamflow` repository
4. Configure:

| Setting | Value |
|---------|-------|
| Root Directory | `teamflow/backend` |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

5. Add Environment Variables in Render dashboard
6. Add `ca.pem` as a **Secret File** at path `./ca.pem`
7. Deploy ✅

---

## Security Features

- Passwords hashed with **bcrypt**
- JWT tokens with configurable expiry
- SSL/TLS encrypted database connection (Aiven ca.pem)
- CORS restricted to frontend domain
- Role checks enforced at API level (not just UI)
- Environment variables for all secrets
- Members cannot access admin endpoints even via direct API calls

---

## Built By

**TeamFlow** — Built as a full-stack internship assignment.  
Stack: FastAPI + Aiven MySQL + HTML + Tailwind CSS | Deploy: Render
