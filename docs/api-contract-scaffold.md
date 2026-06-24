# API Contract Scaffold

## 1. Purpose

This document describes the intended backend API shape for a TypeScript frontend. It is a scaffold, not an OpenAPI implementation. The final API should be generated or documented from the Python backend when implementation begins.

## 2. API Principles

- All protected endpoints require an authenticated active user.
- Authorization is enforced on the backend for every protected resource.
- API responses use consistent success, error, and metadata patterns.
- List endpoints support pagination and filtering.
- Mutating endpoints create audit events where relevant.
- Calculation runs, reports, and exports are never silently overwritten.
- The frontend should be able to rely on typed response models.

## 3. Standard Response Shapes

### Success

```json
{
  "data": {},
  "metadata": {
    "request_id": "REQ-..."
  }
}
```

### List

```json
{
  "data": [],
  "metadata": {
    "request_id": "REQ-...",
    "page": 1,
    "page_size": 25,
    "total_count": 120
  }
}
```

### Validation Error

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "One or more fields are invalid.",
    "fields": [
      {
        "field": "pricing.spread",
        "message": "Spread is required and must be numeric."
      }
    ]
  },
  "metadata": {
    "request_id": "REQ-..."
  }
}
```

### Authorization Error

```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "You do not have permission to perform this action."
  },
  "metadata": {
    "request_id": "REQ-..."
  }
}
```

### Calculation Error

```json
{
  "error": {
    "code": "CALCULATION_FAILED",
    "message": "Calculation failed.",
    "details": []
  },
  "metadata": {
    "request_id": "REQ-...",
    "run_id": "RUN-..."
  }
}
```

## 4. Endpoint Groups

### 4.1 Authentication

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/auth/login` | Authenticate user and create session/token. |
| POST | `/api/auth/logout` | End current session/token. |
| GET | `/api/auth/me` | Return current user profile and capabilities. |
| POST | `/api/auth/register` | Create pending account request. |

### 4.2 Users And Admin User Management

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/admin/users` | Search users. |
| GET | `/api/admin/users/{user_id}` | View user detail and activity summary. |
| PATCH | `/api/admin/users/{user_id}` | Update status or role. |
| POST | `/api/admin/users/{user_id}/approve` | Approve pending user. |
| POST | `/api/admin/users/{user_id}/disable` | Disable user. |

### 4.3 Dashboard

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/dashboard/business` | Business landing data for current user. |
| GET | `/api/dashboard/admin` | Admin console status and activity. |

### 4.4 Workspaces

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/workspaces/me` | Get current user's workspace. |
| GET | `/api/workspaces/{workspace_id}` | View workspace if authorized. |
| PATCH | `/api/workspaces/{workspace_id}` | Update workspace metadata. |

### 4.5 Assets / Securities

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/assets` | Search assets/securities. |
| POST | `/api/assets` | Create asset/security. |
| GET | `/api/assets/{asset_security_id}` | View asset/security. |
| PATCH | `/api/assets/{asset_security_id}` | Update allowed metadata. |

### 4.6 Calculations

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/calculations` | List accessible calculations/deals. |
| POST | `/api/calculations` | Create calculation. |
| GET | `/api/calculations/{calculation_id}` | View calculation detail. |
| PATCH | `/api/calculations/{calculation_id}` | Update calculation metadata or current input. |
| DELETE | `/api/calculations/{calculation_id}` | Archive/delete calculation if permitted. |
| POST | `/api/calculations/{calculation_id}/input-versions` | Create immutable input version. |
| GET | `/api/calculations/{calculation_id}/input-versions` | List input versions. |
| GET | `/api/calculations/{calculation_id}/history` | Resource history timeline. |

### 4.7 Runs

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/calculations/{calculation_id}/runs` | Run or rerun calculation. |
| GET | `/api/calculation-runs/{run_id}` | View run status/result/provenance. |
| GET | `/api/calculations/{calculation_id}/runs` | List runs for calculation. |
| POST | `/api/calculation-runs/{run_id}/cancel` | Cancel queued/running run if supported. |

### 4.8 Scenarios

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/calculations/{calculation_id}/scenarios` | List scenarios. |
| POST | `/api/calculations/{calculation_id}/scenarios` | Create scenario. |
| GET | `/api/scenarios/{scenario_id}` | View scenario. |
| PATCH | `/api/scenarios/{scenario_id}` | Edit scenario metadata or overrides. |
| DELETE | `/api/scenarios/{scenario_id}` | Delete/archive scenario if permitted. |
| POST | `/api/scenarios/{scenario_id}/runs` | Run scenario. |
| GET | `/api/calculations/{calculation_id}/scenario-comparison` | Compare selected scenario runs. |

### 4.9 Sharing

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/shares` | List objects shared with current user. |
| POST | `/api/shares` | Create share grant. |
| PATCH | `/api/shares/{share_grant_id}` | Update permission level. |
| DELETE | `/api/shares/{share_grant_id}` | Revoke share grant. |

### 4.10 Comments, Tasks, Notifications

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/comments` | List comments for a resource. |
| POST | `/api/comments` | Add comment. |
| PATCH | `/api/comments/{comment_id}` | Edit comment. |
| DELETE | `/api/comments/{comment_id}` | Delete comment if permitted. |
| GET | `/api/tasks` | List current user's tasks or admin-scoped tasks. |
| POST | `/api/tasks` | Create task. |
| PATCH | `/api/tasks/{task_id}` | Update task. |
| GET | `/api/notifications` | List notifications. |
| POST | `/api/notifications/{notification_id}/read` | Mark notification read. |

### 4.11 Admin Parameter Sets

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/admin/parameter-sets` | List parameter sets. |
| POST | `/api/admin/parameter-sets` | Create draft parameter set. |
| GET | `/api/admin/parameter-sets/{parameter_set_id}` | View parameter set. |
| PATCH | `/api/admin/parameter-sets/{parameter_set_id}` | Edit draft parameter set. |
| POST | `/api/admin/parameter-sets/{parameter_set_id}/validate` | Validate parameter set payload. |
| POST | `/api/admin/parameter-sets/{parameter_set_id}/publish` | Publish parameter set. |
| POST | `/api/admin/parameter-sets/{parameter_set_id}/deprecate` | Deprecate parameter set. |
| GET | `/api/admin/parameter-sets/{parameter_set_id}/diff` | Compare versions. |

### 4.12 Templates

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/templates` | List active templates available to current user. |
| GET | `/api/admin/templates` | Admin template management list. |
| POST | `/api/admin/templates` | Create template. |
| PATCH | `/api/admin/templates/{template_id}` | Update template. |
| POST | `/api/admin/templates/{template_id}/activate` | Activate template. |
| POST | `/api/admin/templates/{template_id}/deactivate` | Deactivate template. |

### 4.13 Batch Jobs

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/batch-jobs/upload` | Upload batch file. |
| POST | `/api/batch-jobs/{batch_job_id}/validate` | Validate uploaded rows. |
| POST | `/api/batch-jobs/{batch_job_id}/run` | Run valid rows. |
| GET | `/api/batch-jobs` | List accessible batch jobs. |
| GET | `/api/batch-jobs/{batch_job_id}` | View batch detail. |
| GET | `/api/batch-jobs/{batch_job_id}/items` | View row-level status. |
| GET | `/api/batch-jobs/{batch_job_id}/export` | Export permitted batch results. |

### 4.14 Reports And Exports

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/reports` | Generate report from run. |
| GET | `/api/reports` | List accessible reports. |
| GET | `/api/reports/{report_id}` | View report metadata. |
| GET | `/api/reports/{report_id}/download` | Download report. |
| GET | `/api/calculation-runs/{run_id}/export` | Export permitted run output. |

### 4.15 Audit

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/audit-events` | Search audit events, scoped by role. |
| GET | `/api/resources/{resource_type}/{resource_id}/history` | View resource history. |

## 5. Important Request Contracts

### Create Calculation

The frontend should send calculation metadata, asset reference or creation payload, optional template selection, and initial input payload. The backend creates the calculation and the first input version.

### Run Calculation

The frontend should identify the calculation, selected input version or current draft payload, optional scenario, and requested parameter set policy. The backend resolves the exact parameter set and persists the run.

### Publish Parameter Set

The backend must validate the draft payload, ensure the actor is admin/SME, create audit evidence, and make the published version immutable.

### Share Resource

The backend must validate that the grantor can share the target object and that the grantee exists and is active. The resulting grant should be explicit about permission level.

## 6. API Acceptance Criteria

The API scaffold is ready when:

- Every product surface has an endpoint group.
- Authorization-sensitive actions are clear.
- Standard response patterns are defined.
- Run, export, share, publish, and batch actions are auditable.
- The frontend can be typed against stable resource contracts once implementation begins.
