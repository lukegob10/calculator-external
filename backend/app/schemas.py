from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field
from .models import PermissionLevel, UserRole, UserStatus


class APIResponse(BaseModel):
    data: Any
    metadata: dict[str, Any] = Field(default_factory=dict)


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=1)
    soeid: str = Field(min_length=2)
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    soeid: str
    password: str


class UserOut(BaseModel):
    id: int
    full_name: str
    soeid: str
    role: str
    status: str
    created_at: datetime
    last_login_at: datetime | None = None


class LoginOut(BaseModel):
    token: str
    user: UserOut


class UserUpdateRequest(BaseModel):
    role: UserRole | None = None
    status: UserStatus | None = None


class ParameterSetCreate(BaseModel):
    name: str = "Tax Methodology"
    version: str
    effective_date: str
    payload: dict[str, Any]


class ParameterSetUpdate(BaseModel):
    effective_date: str | None = None
    payload: dict[str, Any] | None = None


class ParameterSetOut(BaseModel):
    id: int
    name: str
    version: str
    status: str
    effective_date: str
    payload: dict[str, Any]
    created_by_user_id: int
    published_by_user_id: int | None
    created_at: datetime
    published_at: datetime | None


class AssetInput(BaseModel):
    identifier: str
    identifier_type: str = "INTERNAL"
    name: str
    asset_type: str = "External Asset"


class CalculationInputPayload(BaseModel):
    asset_value: float = Field(gt=0)
    balance: float = Field(gt=0)
    price: float = Field(gt=0)
    spread_bps: float
    rate_percent: float
    capital_allocation: float = Field(gt=0)
    tax_jurisdiction: str = "DEFAULT"


class CalculationCreate(BaseModel):
    name: str
    description: str = ""
    asset: AssetInput
    input_payload: CalculationInputPayload


class CalculationUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    input_payload: CalculationInputPayload | None = None


class CalculationOut(BaseModel):
    id: int
    name: str
    description: str
    status: str
    owner_user_id: int
    asset: dict[str, Any]
    current_input_version_id: int | None
    current_run_id: int | None
    created_at: datetime
    updated_at: datetime
    permission: str


class RunOut(BaseModel):
    id: int
    calculation_id: int
    input_version_id: int
    parameter_set_id: int
    engine_version: str
    status: str
    result: dict[str, Any]
    warnings: list[dict[str, Any]]
    errors: dict[str, Any]
    executed_by_user_id: int
    started_at: datetime
    completed_at: datetime


class ShareCreate(BaseModel):
    resource_type: str = "CALCULATION"
    resource_id: int
    grantee_soeid: str
    permission_level: PermissionLevel


class ShareOut(BaseModel):
    id: int
    resource_type: str
    resource_id: int
    grantee_user_id: int
    grantee_name: str
    grantee_soeid: str
    permission_level: str
    granted_by_user_id: int
    created_at: datetime
    revoked_at: datetime | None


class AuditOut(BaseModel):
    id: int
    actor_user_id: int | None
    event_type: str
    resource_type: str
    resource_id: int | None
    metadata: dict[str, Any]
    created_at: datetime
