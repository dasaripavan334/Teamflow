from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models import User, ProjectMember, UserRole
from auth import decode_token

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def get_project_member(project_id: str, current_user: User, db: Session):
    """Check if user is member or owner of a project"""
    member = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id,
        )
        .first()
    )
    return member


def require_project_access(project_id: str, current_user: User, db: Session):
    """User must be project member OR global admin"""
    if current_user.role == UserRole.admin:
        return True
    member = get_project_member(project_id, current_user, db)
    if not member:
        raise HTTPException(status_code=403, detail="Access denied to this project")
    return member


def require_project_admin(project_id: str, current_user: User, db: Session):
    """User must be project admin role OR global admin"""
    if current_user.role == UserRole.admin:
        return True
    member = get_project_member(project_id, current_user, db)
    if not member or member.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Project admin access required")
    return member
