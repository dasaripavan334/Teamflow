from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Project, ProjectMember, User
from schemas import MemberAdd, MemberRoleUpdate, MemberOut
from dependencies import get_current_user, require_project_access, require_project_admin

router = APIRouter(prefix="/projects/{project_id}/members", tags=["Members"])


def build_member_out(member: ProjectMember) -> MemberOut:
    return MemberOut(
        id=member.id,
        user_id=member.user_id,
        name=member.user.name,
        email=member.user.email,
        role=member.role,
        joined_at=member.joined_at,
    )


@router.get("/", response_model=List[MemberOut])
def list_members(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    require_project_access(project_id, current_user, db)
    return [build_member_out(m) for m in project.members]


@router.post("/", response_model=MemberOut, status_code=201)
def add_member(
    project_id: str,
    payload: MemberAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    require_project_admin(project_id, current_user, db)

    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found with that email")

    existing = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="User already a member")

    member = ProjectMember(project_id=project_id, user_id=user.id, role=payload.role)
    db.add(member)
    db.commit()
    db.refresh(member)
    return build_member_out(member)


@router.put("/{member_id}", response_model=MemberOut)
def update_member_role(
    project_id: str,
    member_id: str,
    payload: MemberRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_project_admin(project_id, current_user, db)
    member = (
        db.query(ProjectMember)
        .filter(ProjectMember.id == member_id, ProjectMember.project_id == project_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    member.role = payload.role
    db.commit()
    db.refresh(member)
    return build_member_out(member)


@router.delete("/{member_id}", status_code=204)
def remove_member(
    project_id: str,
    member_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_project_admin(project_id, current_user, db)
    member = (
        db.query(ProjectMember)
        .filter(ProjectMember.id == member_id, ProjectMember.project_id == project_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    db.delete(member)
    db.commit()
