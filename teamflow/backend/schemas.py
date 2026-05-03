from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    admin = "admin"
    member = "member"


class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


# Auth
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: str
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


# Projects
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Project name cannot be empty")
        return v.strip()


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class MemberOut(BaseModel):
    id: str
    user_id: str
    name: str
    email: str
    role: UserRole
    joined_at: datetime

    class Config:
        from_attributes = True


class ProjectOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    owner_id: str
    owner_name: str
    created_at: datetime
    member_count: int
    task_count: int

    class Config:
        from_attributes = True


# Members
class MemberAdd(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.member


class MemberRoleUpdate(BaseModel):
    role: UserRole


# Tasks
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.todo
    priority: TaskPriority = TaskPriority.medium
    assignee_id: Optional[str] = None
    due_date: Optional[datetime] = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Task title cannot be empty")
        return v.strip()


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee_id: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskOut(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    project_id: str
    project_name: str
    assignee_id: Optional[str]
    assignee_name: Optional[str]
    created_by: str
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    is_overdue: bool

    class Config:
        from_attributes = True


# Dashboard
class DashboardStats(BaseModel):
    total_projects: int
    total_tasks: int
    todo_count: int
    in_progress_count: int
    done_count: int
    overdue_count: int
    my_tasks: List[TaskOut]