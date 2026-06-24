# Enterprise Calculation Workspace

Polished enterprise calculation workspace for external asset/security calculations.

This repository currently contains:

- `backend/`: Python FastAPI MVP API with local SQLite persistence, auth, users, parameter sets, calculations, runs, sharing, and audit events.
- `frontend/`: plain TypeScript, HTML, and CSS frontend. No React, no TanStack, no frontend framework.
- `docs/`: product, architecture, UI mockup, data model, dependency security, and implementation planning docs.

## Local Development

### Backend

```powershell
cd backend
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The backend seeds local demo accounts on startup:

| Role | SOEID | Password |
|---|---|---|
| Admin | `admin` | `Admin123!` |
| Base user | `lgoblirsch` | `Demo123!` |
| Base user | `apatel` | `Demo123!` |

### Frontend

```powershell
cd frontend
npm install
npm run build
npm run dev
```

Open `http://127.0.0.1:5177`.

The frontend expects the API at `http://127.0.0.1:8000`.

## Validation

```powershell
cd backend
pytest
```

```powershell
cd frontend
npm run typecheck
npm run build
```

## Implementation Notes

- Frontend uses plain TypeScript modules and browser APIs.
- Backend enforces permissions; frontend route/action checks are UX only.
- Completed calculation runs preserve input version, parameter set, engine version, and audit events.
- Sharing supports view, edit, and export-values grants with owner/admin revocation.
- SQLite is the local development store. Oracle integration is intentionally isolated behind backend persistence boundaries for a later production adapter.
