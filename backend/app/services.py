from __future__ import annotations

import json
from typing import Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from .db import get_db
from .models import AuditEvent, Calculation, PermissionLevel, SessionToken, ShareGrant, User, UserRole, UserStatus, utcnow

bearer = HTTPBearer(auto_error=False)


def as_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def from_json(value: str) -> Any:
    return json.loads(value)


def audit(
    db: Session,
    actor: User | None,
    event_type: str,
    resource_type: str,
    resource_id: int | None,
    metadata: dict[str, Any] | None = None,
) -> None:
    db.add(
        AuditEvent(
            actor_user_id=actor.id if actor else None,
            event_type=event_type,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata_json=as_json(metadata or {}),
        )
    )


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")
    token = db.scalar(select(SessionToken).where(SessionToken.token == credentials.credentials, SessionToken.revoked.is_(False)))
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session.")
    user = db.get(User, token.user_id)
    if user is None or user.status != UserStatus.ACTIVE.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not active.")
    return user


def require_admin(user: User = Depends(current_user)) -> User:
    if user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    return user


def active_share(db: Session, calculation_id: int, user_id: int) -> ShareGrant | None:
    return db.scalar(
        select(ShareGrant).where(
            ShareGrant.resource_type == "CALCULATION",
            ShareGrant.resource_id == calculation_id,
            ShareGrant.grantee_user_id == user_id,
            ShareGrant.revoked_at.is_(None),
        )
    )


def permission_for(db: Session, calculation: Calculation, user: User) -> str | None:
    if user.role == UserRole.ADMIN.value:
        return PermissionLevel.ADMIN_FULL.value
    if calculation.owner_user_id == user.id:
        return "OWNER"
    grant = active_share(db, calculation.id, user.id)
    return grant.permission_level if grant else None


def require_calculation_permission(db: Session, calculation_id: int, user: User, required: str) -> tuple[Calculation, str]:
    calculation = db.get(Calculation, calculation_id)
    if calculation is None or calculation.status == "ARCHIVED":
        raise HTTPException(status_code=404, detail="Calculation not found.")
    permission = permission_for(db, calculation, user)
    if permission is None:
        raise HTTPException(status_code=403, detail="You do not have access to this calculation.")
    if required == "VIEW":
        return calculation, permission
    if required == "EDIT" and permission not in {"OWNER", PermissionLevel.EDIT.value, PermissionLevel.ADMIN_FULL.value}:
        raise HTTPException(status_code=403, detail="Edit permission required.")
    if required == "OWNER" and permission not in {"OWNER", PermissionLevel.ADMIN_FULL.value}:
        raise HTTPException(status_code=403, detail="Owner or admin permission required.")
    return calculation, permission


def accessible_calculation_filter(user: User):
    if user.role == UserRole.ADMIN.value:
        return True
    return or_(
        Calculation.owner_user_id == user.id,
        Calculation.id.in_(
            select(ShareGrant.resource_id).where(
                ShareGrant.resource_type == "CALCULATION",
                ShareGrant.grantee_user_id == user.id,
                ShareGrant.revoked_at.is_(None),
            )
        ),
    )


def touch_user(user: User) -> None:
    user.updated_at = utcnow()
