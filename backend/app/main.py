from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from .calc_engine import run_external_asset_calculation
from .config import get_settings
from .db import create_all, get_db
from .models import (
    AssetSecurity,
    AuditEvent,
    Calculation,
    CalculationInputVersion,
    CalculationRun,
    CalculationStatus,
    ParameterSet,
    ParameterStatus,
    PermissionLevel,
    RunStatus,
    SessionToken,
    ShareGrant,
    User,
    UserRole,
    UserStatus,
    utcnow,
)
from .schemas import (
    APIResponse,
    AuditOut,
    CalculationCreate,
    CalculationOut,
    CalculationUpdate,
    LoginOut,
    LoginRequest,
    ParameterSetCreate,
    ParameterSetOut,
    ParameterSetUpdate,
    RegisterRequest,
    RunOut,
    ShareCreate,
    ShareOut,
    UserOut,
    UserUpdateRequest,
)
from .security import canonical_hash, hash_password, new_token, verify_password
from .seed import seed_demo_data
from .services import (
    accessible_calculation_filter,
    as_json,
    audit,
    current_user,
    from_json,
    permission_for,
    require_admin,
    require_calculation_permission,
    touch_user,
)

settings = get_settings()


def bootstrap_database() -> None:
    create_all()
    from .db import SessionLocal

    with SessionLocal() as db:
        seed_demo_data(db)
        db.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    bootstrap_database()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5177", "http://localhost:5177"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def ok(data: Any) -> APIResponse:
    return APIResponse(data=data, metadata={"request_id": "local-dev"})


def user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        full_name=user.full_name,
        soeid=user.soeid,
        role=user.role,
        status=user.status,
        created_at=user.created_at,
        last_login_at=user.last_login_at,
    )


def parameter_out(parameter: ParameterSet) -> ParameterSetOut:
    return ParameterSetOut(
        id=parameter.id,
        name=parameter.name,
        version=parameter.version,
        status=parameter.status,
        effective_date=parameter.effective_date,
        payload=from_json(parameter.payload_json),
        created_by_user_id=parameter.created_by_user_id,
        published_by_user_id=parameter.published_by_user_id,
        created_at=parameter.created_at,
        published_at=parameter.published_at,
    )


def calculation_out(db: Session, calculation: Calculation, user: User) -> CalculationOut:
    asset = db.get(AssetSecurity, calculation.asset_security_id)
    return CalculationOut(
        id=calculation.id,
        name=calculation.name,
        description=calculation.description,
        status=calculation.status,
        owner_user_id=calculation.owner_user_id,
        asset={
            "id": asset.id if asset else None,
            "identifier": asset.identifier if asset else "",
            "identifier_type": asset.identifier_type if asset else "",
            "name": asset.name if asset else "",
            "asset_type": asset.asset_type if asset else "",
        },
        current_input_version_id=calculation.current_input_version_id,
        current_run_id=calculation.current_run_id,
        created_at=calculation.created_at,
        updated_at=calculation.updated_at,
        permission=permission_for(db, calculation, user) or "NONE",
    )


def run_out(run: CalculationRun) -> RunOut:
    return RunOut(
        id=run.id,
        calculation_id=run.calculation_id,
        input_version_id=run.input_version_id,
        parameter_set_id=run.parameter_set_id,
        engine_version=run.engine_version,
        status=run.status,
        result=from_json(run.result_payload_json),
        warnings=from_json(run.warning_payload_json),
        errors=from_json(run.error_payload_json),
        executed_by_user_id=run.executed_by_user_id,
        started_at=run.started_at,
        completed_at=run.completed_at,
    )


@app.get("/api/health")
def health() -> APIResponse:
    return ok({"status": "ok", "app": settings.app_name})


@app.post("/api/auth/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> APIResponse:
    existing = db.scalar(select(User).where(User.soeid == payload.soeid))
    if existing:
        raise HTTPException(status_code=409, detail="SOEID already exists.")
    user = User(
        full_name=payload.full_name,
        soeid=payload.soeid,
        password_hash=hash_password(payload.password),
        role=UserRole.BUSINESS_USER.value,
        status=UserStatus.PENDING.value,
    )
    db.add(user)
    db.flush()
    audit(db, user, "account_registered", "USER", user.id, {"status": user.status})
    db.commit()
    return ok(user_out(user))


@app.post("/api/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> APIResponse:
    user = db.scalar(select(User).where(User.soeid == payload.soeid))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    if user.status != UserStatus.ACTIVE.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is not active.")
    token = SessionToken(token=new_token(), user_id=user.id)
    user.last_login_at = utcnow()
    db.add(token)
    audit(db, user, "login_success", "USER", user.id)
    db.commit()
    return ok(LoginOut(token=token.token, user=user_out(user)))


@app.post("/api/auth/logout")
def logout(user: User = Depends(current_user), db: Session = Depends(get_db)) -> APIResponse:
    for token in db.scalars(select(SessionToken).where(SessionToken.user_id == user.id, SessionToken.revoked.is_(False))).all():
        token.revoked = True
    audit(db, user, "logout", "USER", user.id)
    db.commit()
    return ok({"logged_out": True})


@app.get("/api/auth/me")
def me(user: User = Depends(current_user)) -> APIResponse:
    return ok(user_out(user))


@app.get("/api/dashboard/business")
def business_dashboard(user: User = Depends(current_user), db: Session = Depends(get_db)) -> APIResponse:
    calculations = db.scalars(
        select(Calculation).where(accessible_calculation_filter(user)).order_by(desc(Calculation.updated_at)).limit(8)
    ).all()
    tasks_due = 3 if user.role == UserRole.BUSINESS_USER.value else 0
    return ok(
        {
            "stats": {
                "open_drafts": sum(1 for c in calculations if c.status == CalculationStatus.DRAFT.value),
                "accessible_calculations": len(calculations),
                "shared_with_me": db.scalar(
                    select(func.count(ShareGrant.id)).where(
                        ShareGrant.grantee_user_id == user.id,
                        ShareGrant.revoked_at.is_(None),
                    )
                ),
                "tasks_due": tasks_due,
            },
            "calculations": [calculation_out(db, c, user).model_dump(mode="json") for c in calculations],
        }
    )


@app.get("/api/dashboard/admin")
def admin_dashboard(admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> APIResponse:
    return ok(
        {
            "stats": {
                "active_users": db.scalar(select(func.count(User.id)).where(User.status == UserStatus.ACTIVE.value)),
                "pending_users": db.scalar(select(func.count(User.id)).where(User.status == UserStatus.PENDING.value)),
                "calculations": db.scalar(select(func.count(Calculation.id))),
                "active_grants": db.scalar(select(func.count(ShareGrant.id)).where(ShareGrant.revoked_at.is_(None))),
                "published_parameters": db.scalar(select(func.count(ParameterSet.id)).where(ParameterSet.status == ParameterStatus.PUBLISHED.value)),
            }
        }
    )


@app.get("/api/admin/users")
def list_users(admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> APIResponse:
    users = db.scalars(select(User).order_by(User.status, User.full_name)).all()
    return ok([user_out(user).model_dump(mode="json") for user in users])


@app.patch("/api/admin/users/{user_id}")
def update_user(user_id: int, payload: UserUpdateRequest, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> APIResponse:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    if payload.role is not None:
        user.role = payload.role.value
    if payload.status is not None:
        user.status = payload.status.value
    touch_user(user)
    audit(db, admin, "user_updated", "USER", user.id, {"role": user.role, "status": user.status})
    db.commit()
    return ok(user_out(user))


@app.get("/api/admin/parameter-sets")
def list_parameter_sets(admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> APIResponse:
    parameters = db.scalars(select(ParameterSet).order_by(desc(ParameterSet.created_at))).all()
    return ok([parameter_out(p).model_dump(mode="json") for p in parameters])


@app.post("/api/admin/parameter-sets")
def create_parameter_set(payload: ParameterSetCreate, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> APIResponse:
    parameter = ParameterSet(
        name=payload.name,
        version=payload.version,
        effective_date=payload.effective_date,
        payload_json=as_json(payload.payload),
        created_by_user_id=admin.id,
    )
    db.add(parameter)
    db.flush()
    audit(db, admin, "parameter_set_created", "PARAMETER_SET", parameter.id, {"version": parameter.version})
    db.commit()
    return ok(parameter_out(parameter))


@app.patch("/api/admin/parameter-sets/{parameter_id}")
def update_parameter_set(parameter_id: int, payload: ParameterSetUpdate, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> APIResponse:
    parameter = db.get(ParameterSet, parameter_id)
    if parameter is None:
        raise HTTPException(status_code=404, detail="Parameter set not found.")
    if parameter.status != ParameterStatus.DRAFT.value:
        raise HTTPException(status_code=409, detail="Only draft parameter sets can be edited.")
    if payload.effective_date is not None:
        parameter.effective_date = payload.effective_date
    if payload.payload is not None:
        parameter.payload_json = as_json(payload.payload)
    audit(db, admin, "parameter_set_updated", "PARAMETER_SET", parameter.id)
    db.commit()
    return ok(parameter_out(parameter))


@app.post("/api/admin/parameter-sets/{parameter_id}/publish")
def publish_parameter_set(parameter_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> APIResponse:
    parameter = db.get(ParameterSet, parameter_id)
    if parameter is None:
        raise HTTPException(status_code=404, detail="Parameter set not found.")
    if parameter.status != ParameterStatus.DRAFT.value:
        raise HTTPException(status_code=409, detail="Only draft parameter sets can be published.")
    parameter.status = ParameterStatus.PUBLISHED.value
    parameter.published_by_user_id = admin.id
    parameter.published_at = utcnow()
    audit(db, admin, "parameter_set_published", "PARAMETER_SET", parameter.id, {"version": parameter.version})
    db.commit()
    return ok(parameter_out(parameter))


@app.get("/api/calculations")
def list_calculations(user: User = Depends(current_user), db: Session = Depends(get_db)) -> APIResponse:
    calculations = db.scalars(
        select(Calculation).where(accessible_calculation_filter(user), Calculation.status != CalculationStatus.ARCHIVED.value).order_by(desc(Calculation.updated_at))
    ).all()
    return ok([calculation_out(db, calculation, user).model_dump(mode="json") for calculation in calculations])


@app.post("/api/calculations")
def create_calculation(payload: CalculationCreate, user: User = Depends(current_user), db: Session = Depends(get_db)) -> APIResponse:
    asset = AssetSecurity(**payload.asset.model_dump())
    db.add(asset)
    db.flush()
    calculation = Calculation(owner_user_id=user.id, asset_security_id=asset.id, name=payload.name, description=payload.description)
    db.add(calculation)
    db.flush()
    input_json = as_json(payload.input_payload.model_dump())
    version = CalculationInputVersion(
        calculation_id=calculation.id,
        version_number=1,
        input_payload_json=input_json,
        input_hash=canonical_hash(input_json),
        created_by_user_id=user.id,
    )
    db.add(version)
    db.flush()
    calculation.current_input_version_id = version.id
    calculation.status = CalculationStatus.READY.value
    audit(db, user, "calculation_created", "CALCULATION", calculation.id, {"input_version": version.id})
    db.commit()
    return ok(calculation_out(db, calculation, user))


@app.get("/api/calculations/{calculation_id}")
def get_calculation(calculation_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> APIResponse:
    calculation, _ = require_calculation_permission(db, calculation_id, user, "VIEW")
    return ok(calculation_out(db, calculation, user))


@app.patch("/api/calculations/{calculation_id}")
def update_calculation(calculation_id: int, payload: CalculationUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)) -> APIResponse:
    calculation, _ = require_calculation_permission(db, calculation_id, user, "EDIT")
    if payload.name is not None:
        calculation.name = payload.name
    if payload.description is not None:
        calculation.description = payload.description
    if payload.input_payload is not None:
        next_number = db.scalar(select(func.count(CalculationInputVersion.id)).where(CalculationInputVersion.calculation_id == calculation.id)) + 1
        input_json = as_json(payload.input_payload.model_dump())
        version = CalculationInputVersion(
            calculation_id=calculation.id,
            version_number=next_number,
            input_payload_json=input_json,
            input_hash=canonical_hash(input_json),
            created_by_user_id=user.id,
        )
        db.add(version)
        db.flush()
        calculation.current_input_version_id = version.id
        calculation.status = CalculationStatus.READY.value
    calculation.updated_at = utcnow()
    audit(db, user, "calculation_updated", "CALCULATION", calculation.id)
    db.commit()
    return ok(calculation_out(db, calculation, user))


@app.post("/api/calculations/{calculation_id}/runs")
def run_calculation(
    calculation_id: int,
    parameter_set_id: int | None = Query(default=None),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> APIResponse:
    calculation, _ = require_calculation_permission(db, calculation_id, user, "EDIT")
    input_version = db.get(CalculationInputVersion, calculation.current_input_version_id)
    if input_version is None:
        raise HTTPException(status_code=409, detail="Calculation has no input version.")
    if parameter_set_id is None:
        parameter = db.scalar(select(ParameterSet).where(ParameterSet.status == ParameterStatus.PUBLISHED.value).order_by(desc(ParameterSet.published_at)))
    else:
        parameter = db.get(ParameterSet, parameter_set_id)
    if parameter is None or parameter.status != ParameterStatus.PUBLISHED.value:
        raise HTTPException(status_code=409, detail="A published parameter set is required.")

    try:
        engine_output = run_external_asset_calculation(from_json(input_version.input_payload_json), from_json(parameter.payload_json), settings.engine_version)
        status_value = RunStatus.COMPLETED_WITH_WARNINGS.value if engine_output["warnings"] else RunStatus.COMPLETED.value
        result_json = as_json(engine_output["result"])
        warning_json = as_json(engine_output["warnings"])
        error_json = "{}"
        calculation.status = CalculationStatus.WARNING.value if engine_output["warnings"] else CalculationStatus.COMPLETE.value
    except Exception as exc:
        status_value = RunStatus.FAILED.value
        result_json = "{}"
        warning_json = "[]"
        error_json = as_json({"message": str(exc)})
        calculation.status = CalculationStatus.FAILED.value

    run = CalculationRun(
        calculation_id=calculation.id,
        input_version_id=input_version.id,
        parameter_set_id=parameter.id,
        engine_version=settings.engine_version,
        status=status_value,
        result_payload_json=result_json,
        warning_payload_json=warning_json,
        error_payload_json=error_json,
        executed_by_user_id=user.id,
    )
    db.add(run)
    db.flush()
    calculation.current_run_id = run.id
    calculation.updated_at = utcnow()
    audit(db, user, "calculation_run", "CALCULATION", calculation.id, {"run_id": run.id, "parameter_set_id": parameter.id})
    db.commit()
    return ok(run_out(run))


@app.get("/api/calculations/{calculation_id}/runs")
def list_runs(calculation_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> APIResponse:
    require_calculation_permission(db, calculation_id, user, "VIEW")
    runs = db.scalars(select(CalculationRun).where(CalculationRun.calculation_id == calculation_id).order_by(desc(CalculationRun.started_at))).all()
    return ok([run_out(run).model_dump(mode="json") for run in runs])


@app.post("/api/shares")
def create_share(payload: ShareCreate, user: User = Depends(current_user), db: Session = Depends(get_db)) -> APIResponse:
    if payload.resource_type != "CALCULATION":
        raise HTTPException(status_code=400, detail="Only calculation sharing is supported in this slice.")
    calculation, _ = require_calculation_permission(db, payload.resource_id, user, "OWNER")
    grantee = db.scalar(select(User).where(User.soeid == payload.grantee_soeid, User.status == UserStatus.ACTIVE.value))
    if grantee is None:
        raise HTTPException(status_code=404, detail="Active grantee user not found.")
    if grantee.id == calculation.owner_user_id:
        raise HTTPException(status_code=409, detail="Owner already has access.")
    grant = ShareGrant(
        resource_type="CALCULATION",
        resource_id=calculation.id,
        grantee_user_id=grantee.id,
        permission_level=payload.permission_level.value,
        granted_by_user_id=user.id,
    )
    db.add(grant)
    db.flush()
    audit(db, user, "share_grant_created", "CALCULATION", calculation.id, {"grantee": grantee.soeid, "permission": grant.permission_level})
    db.commit()
    return ok(share_out(db, grant))


def share_out(db: Session, grant: ShareGrant) -> ShareOut:
    grantee = db.get(User, grant.grantee_user_id)
    return ShareOut(
        id=grant.id,
        resource_type=grant.resource_type,
        resource_id=grant.resource_id,
        grantee_user_id=grant.grantee_user_id,
        grantee_name=grantee.full_name if grantee else "Unknown",
        grantee_soeid=grantee.soeid if grantee else "unknown",
        permission_level=grant.permission_level,
        granted_by_user_id=grant.granted_by_user_id,
        created_at=grant.created_at,
        revoked_at=grant.revoked_at,
    )


@app.get("/api/shares")
def list_shares(user: User = Depends(current_user), db: Session = Depends(get_db)) -> APIResponse:
    if user.role == UserRole.ADMIN.value:
        grants = db.scalars(select(ShareGrant).order_by(desc(ShareGrant.created_at))).all()
    else:
        owned_ids = select(Calculation.id).where(Calculation.owner_user_id == user.id)
        grants = db.scalars(
            select(ShareGrant).where((ShareGrant.grantee_user_id == user.id) | (ShareGrant.resource_id.in_(owned_ids))).order_by(desc(ShareGrant.created_at))
        ).all()
    return ok([share_out(db, grant).model_dump(mode="json") for grant in grants])


@app.delete("/api/shares/{share_id}")
def revoke_share(share_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> APIResponse:
    grant = db.get(ShareGrant, share_id)
    if grant is None:
        raise HTTPException(status_code=404, detail="Share grant not found.")
    calculation = db.get(Calculation, grant.resource_id)
    if calculation is None:
        raise HTTPException(status_code=404, detail="Shared calculation not found.")
    permission = permission_for(db, calculation, user)
    if permission not in {"OWNER", PermissionLevel.ADMIN_FULL.value}:
        raise HTTPException(status_code=403, detail="Owner or admin permission required.")
    grant.revoked_at = utcnow()
    audit(db, user, "share_grant_revoked", "CALCULATION", grant.resource_id, {"grant_id": grant.id})
    db.commit()
    return ok(share_out(db, grant))


@app.get("/api/audit-events")
def list_audit_events(user: User = Depends(current_user), db: Session = Depends(get_db)) -> APIResponse:
    if user.role == UserRole.ADMIN.value:
        events = db.scalars(select(AuditEvent).order_by(desc(AuditEvent.created_at)).limit(100)).all()
    else:
        events = db.scalars(select(AuditEvent).where(AuditEvent.actor_user_id == user.id).order_by(desc(AuditEvent.created_at)).limit(100)).all()
    return ok(
        [
            AuditOut(
                id=e.id,
                actor_user_id=e.actor_user_id,
                event_type=e.event_type,
                resource_type=e.resource_type,
                resource_id=e.resource_id,
                metadata=from_json(e.metadata_json),
                created_at=e.created_at,
            ).model_dump(mode="json")
            for e in events
        ]
    )


if settings.frontend_dist.exists():
    app.mount("/", StaticFiles(directory=settings.frontend_dist, html=True), name="frontend")
