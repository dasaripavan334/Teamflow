from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from database import get_db
from models import Project, ProjectMember, User, UserRole
from schemas import ProjectOut
from dependencies import get_current_user, require_admin, require_project_access

router = APIRouter(prefix="/projects", tags=["Projects"])


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    member_ids: List[str] = []  # user ids to add at creation


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


def build_project_out(project: Project) -> ProjectOut:
    return ProjectOut(
        id=project.id,
        name=project.name,
        description=project.description,
        owner_id=project.owner_id,
        owner_name=project.owner.name,
        created_at=project.created_at,
        member_count=len(project.members),
        task_count=len(project.tasks),
    )


@router.get("/", response_model=List[ProjectOut])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == UserRole.admin:
        projects = db.query(Project).all()
    else:
        memberships = db.query(ProjectMember).filter(ProjectMember.user_id == current_user.id).all()
        project_ids = [m.project_id for m in memberships]
        projects = db.query(Project).filter(Project.id.in_(project_ids)).all()
    return [build_project_out(p) for p in projects]


@router.post("/", response_model=ProjectOut, status_code=201)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if not payload.name.strip():
        raise HTTPException(status_code=400, detail="Project name cannot be empty")

    project = Project(
        name=payload.name.strip(),
        description=payload.description,
        owner_id=current_user.id,
    )
    db.add(project)
    db.flush()

    # Add admin as member
    db.add(ProjectMember(project_id=project.id, user_id=current_user.id, role=UserRole.admin))

    # Add selected members
    for uid in payload.member_ids:
        if uid == current_user.id:
            continue
        user = db.query(User).filter(User.id == uid).first()
        if user:
            db.add(ProjectMember(project_id=project.id, user_id=uid, role=UserRole.member))

    db.commit()
    db.refresh(project)
    return build_project_out(project)


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    require_project_access(project_id, current_user, db)
    return build_project_out(project)


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: str,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description
    db.commit()
    db.refresh(project)
    return build_project_out(project)


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()


@router.get("/{project_id}/members", response_model=List[dict])
def get_project_members(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    require_project_access(project_id, current_user, db)
    return [
        {"id": m.user.id, "name": m.user.name, "email": m.user.email, "role": m.role}
        for m in project.members
    ]