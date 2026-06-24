from __future__ import annotations

import json
from sqlalchemy import select
from sqlalchemy.orm import Session
from .calc_engine import run_external_asset_calculation
from .config import get_settings
from .models import (
    AssetSecurity,
    Calculation,
    CalculationInputVersion,
    CalculationRun,
    CalculationStatus,
    ParameterSet,
    PermissionLevel,
    RunStatus,
    ShareGrant,
    User,
    UserRole,
    UserStatus,
    Workspace,
)
from .security import canonical_hash, hash_password
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
    luke = ensure_user(db, "Luke Goblirsch", "lgoblirsch", "Demo123!", UserRole.BUSINESS_USER, UserStatus.ACTIVE)
    aarav = ensure_user(db, "Aarav Patel", "apatel", "Demo123!", UserRole.BUSINESS_USER, UserStatus.ACTIVE)
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
        db.flush()
    else:
        parameter = existing

    if db.scalar(select(Calculation).where(Calculation.name == "Alpha Credit Base", Calculation.owner_user_id == luke.id)) is None:
        asset = AssetSecurity(
            identifier="CUSIP 123456AB",
            identifier_type="CUSIP",
            name="Alpha Credit",
            asset_type="External Asset",
        )
        db.add(asset)
        db.flush()
        calculation = Calculation(
            owner_user_id=luke.id,
            asset_security_id=asset.id,
            name="Alpha Credit Base",
            description="Seeded demo calculation with completed run evidence.",
            status=CalculationStatus.READY.value,
        )
        db.add(calculation)
        db.flush()
        input_payload = {
            "asset_value": 84200000,
            "balance": 76000000,
            "price": 102.625,
            "spread_bps": 245,
            "rate_percent": 6.4,
            "capital_allocation": 11400000,
            "tax_jurisdiction": "DEFAULT",
        }
        input_json = as_json(input_payload)
        input_version = CalculationInputVersion(
            calculation_id=calculation.id,
            version_number=1,
            input_payload_json=input_json,
            input_hash=canonical_hash(input_json),
            created_by_user_id=luke.id,
        )
        db.add(input_version)
        db.flush()
        calculation.current_input_version_id = input_version.id

        engine_version = get_settings().engine_version
        output = run_external_asset_calculation(input_payload, json.loads(parameter.payload_json), engine_version)
        status = RunStatus.COMPLETED_WITH_WARNINGS.value if output["warnings"] else RunStatus.COMPLETED.value
        run = CalculationRun(
            calculation_id=calculation.id,
            input_version_id=input_version.id,
            parameter_set_id=parameter.id,
            engine_version=engine_version,
            status=status,
            result_payload_json=as_json(output["result"]),
            warning_payload_json=as_json(output["warnings"]),
            error_payload_json="{}",
            executed_by_user_id=luke.id,
        )
        db.add(run)
        db.flush()
        calculation.current_run_id = run.id
        calculation.status = CalculationStatus.WARNING.value if output["warnings"] else CalculationStatus.COMPLETE.value
        db.add(
            ShareGrant(
                resource_type="CALCULATION",
                resource_id=calculation.id,
                grantee_user_id=aarav.id,
                permission_level=PermissionLevel.VIEW.value,
                granted_by_user_id=luke.id,
            )
        )
