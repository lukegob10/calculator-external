from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import ParameterSet, User, UserRole, UserStatus, Workspace
from .security import hash_password
from .services import as_json


def ensure_user(db: Session, full_name: str, soeid: str, password: str, role: UserRole, status: UserStatus) -> User:
    user = db.scalar(select(User).where(User.soeid == soeid))
    if user:
        return user
    user = User(full_name=full_name, soeid=soeid, password_hash=hash_password(password), role=role.value, status=status.value)
    db.add(user)
    db.flush()
    db.add(Workspace(owner_user_id=user.id, name=f"{full_name} Workspace"))
    return user


def seed_demo_data(db: Session) -> None:
    admin = ensure_user(db, "Admin User", "admin", "Admin123!", UserRole.ADMIN, UserStatus.ACTIVE)
    ensure_user(db, "Luke Goblirsch", "lgoblirsch", "Demo123!", UserRole.BUSINESS_USER, UserStatus.ACTIVE)
    ensure_user(db, "Aarav Patel", "apatel", "Demo123!", UserRole.BUSINESS_USER, UserStatus.ACTIVE)
    ensure_user(db, "Maya Chen", "mchen", "Demo123!", UserRole.BUSINESS_USER, UserStatus.PENDING)

    existing = db.scalar(select(ParameterSet).where(ParameterSet.name == "Tax Methodology", ParameterSet.version == "v3.2"))
    if existing is None:
        parameter = ParameterSet(
            name="Tax Methodology",
            version="v3.2",
            status="PUBLISHED",
            effective_date="2026-06-17",
            payload_json=as_json({"default_tax_rate": 0.21, "capital_charge_rate": 0.08, "methodology": "standardized_allocation"}),
            created_by_user_id=admin.id,
            published_by_user_id=admin.id,
        )
        db.add(parameter)
