from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from database import get_db
from models import Task, Project, ProjectMember, User, UserRole, TaskStatus
from schemas import TaskCreate, TaskUpdate, TaskOut, DashboardStats
from dependencies import get_current_user, require_project_access, require_project_admin

router = APIRouter(tags=["Tasks"])


def build_task_out(task: Task) -> TaskOut:
    now = datetime.utcnow()
    is_overdue = (
        task.due_date is not None
        and task.due_date.replace(tzinfo=None) < now
        and task.status != TaskStatus.done
    )
    return TaskOut(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        project_id=task.project_id,
        project_name=task.project.name,
        assignee_id=task.assignee_id,
        assignee_name=task.assignee.name if task.assignee else None,
        created_by=task.created_by,
        due_date=task.due_date,
        created_at=task.created_at,
        updated_at=task.updated_at,
        is_overdue=is_overdue,
    )


# Dashboard
@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == UserRole.admin:
        all_tasks = db.query(Task).all()
        projects_count = db.query(Project).count()
    else:
        memberships = (
            db.query(ProjectMember)
            .filter(ProjectMember.user_id == current_user.id)
            .all()
        )
        project_ids = [m.project_id for m in memberships]
        all_tasks = db.query(Task).filter(Task.project_id.in_(project_ids)).all()
        projects_count = len(project_ids)

    now = datetime.utcnow()
    todo = sum(1 for t in all_tasks if t.status == TaskStatus.todo)
    in_progress = sum(1 for t in all_tasks if t.status == TaskStatus.in_progress)
    done = sum(1 for t in all_tasks if t.status == TaskStatus.done)
    overdue = sum(
        1 for t in all_tasks
        if t.due_date and t.due_date.replace(tzinfo=None) < now and t.status != TaskStatus.done
    )
    my_tasks = [t for t in all_tasks if t.assignee_id == current_user.id]

    return DashboardStats(
        total_projects=projects_count,
        total_tasks=len(all_tasks),
        todo_count=todo,
        in_progress_count=in_progress,
        done_count=done,
        overdue_count=overdue,
        my_tasks=[build_task_out(t) for t in my_tasks[:10]],
    )


# Project tasks
@router.get("/projects/{project_id}/tasks", response_model=List[TaskOut])
def list_project_tasks(
    project_id: str,
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    assignee_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    require_project_access(project_id, current_user, db)

    query = db.query(Task).filter(Task.project_id == project_id)
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)

    return [build_task_out(t) for t in query.all()]


@router.post("/projects/{project_id}/tasks", response_model=TaskOut, status_code=201)
def create_task(
    project_id: str,
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    require_project_access(project_id, current_user, db)

    if payload.assignee_id:
        assignee = db.query(User).filter(User.id == payload.assignee_id).first()
        if not assignee:
            raise HTTPException(status_code=404, detail="Assignee not found")

    task = Task(
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        project_id=project_id,
        assignee_id=payload.assignee_id,
        created_by=current_user.id,
        due_date=payload.due_date,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return build_task_out(task)


@router.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    require_project_access(task.project_id, current_user, db)
    return build_task_out(task)


@router.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(
    task_id: str,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    require_project_access(task.project_id, current_user, db)

    # Members can only update status of their own tasks
    member = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == current_user.id,
        )
        .first()
    )
    is_project_admin = current_user.role == UserRole.admin or (
        member and member.role == UserRole.admin
    )

    if not is_project_admin:
        if task.assignee_id != current_user.id:
            raise HTTPException(status_code=403, detail="You can only update your own tasks")
        # Members can only change status
        allowed = TaskUpdate(status=payload.status)
        payload = allowed

    if payload.title is not None:
        task.title = payload.title
    if payload.description is not None:
        task.description = payload.description
    if payload.status is not None:
        task.status = payload.status
    if payload.priority is not None:
        task.priority = payload.priority
    if payload.assignee_id is not None:
        task.assignee_id = payload.assignee_id
    if payload.due_date is not None:
        task.due_date = payload.due_date

    db.commit()
    db.refresh(task)
    return build_task_out(task)


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    require_project_admin(task.project_id, current_user, db)
    db.delete(task)
    db.commit()
