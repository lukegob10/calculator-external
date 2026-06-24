# Phased Implementation Plan

## 1. Purpose

This plan sequences the future implementation after the documentation scaffold is approved. It is intentionally phased so the team proves architecture, permissions, calculation reproducibility, and UI quality before expanding into the full enterprise feature set.

No implementation is included in this document.

## 2. Delivery Strategy

Build a narrow but real vertical slice first:

1. Local auth and role-aware landing.
2. Business deal dashboard.
3. Admin user approval and parameter set publication.
4. Calculation creation with placeholder asset inputs.
5. Python calculation engine execution.
6. Oracle-backed run persistence.
7. Output review with engine version, parameter version, input version, and audit event.

This proves the critical architecture before adding broad collaboration, batch, and reporting features.

## 3. Phase 0 - Project Skeleton

### Goal

Establish the future frontend/backend shape without domain depth.

### Deliverables

- TypeScript frontend skeleton.
- Python/FastAPI backend skeleton.
- Health endpoint.
- Oracle connection abstraction.
- Shared domain enums.
- Initial README and developer setup notes.

### Acceptance Criteria

- Frontend runs locally.
- Backend runs locally.
- Backend exposes API docs.
- Code structure reflects frontend/backend split.
- No calculation formulas are embedded in frontend or route handlers.

### Validation Focus

- Build/test commands run.
- Lint/type checks configured.
- App shell can render placeholder routes.

## 4. Phase 1 - Auth, Users, Roles

### Goal

Enable secure login and role-aware application entry.

### Deliverables

- Login screen.
- Account creation screen.
- Password hashing.
- Session/token handling.
- Current-user API.
- User persistence.
- Pending account flow.
- Admin user approval and role assignment basics.
- Business/admin landing redirect.

### Acceptance Criteria

- Business user lands on business dashboard.
- Admin user lands on admin console.
- Pending users cannot access app until approved if enabled.
- Users cannot assign themselves admin role.
- Disabled users cannot log in.

### Validation Focus

- Auth tests.
- Account validation tests.
- Role restriction tests.
- Permission-denied UI.

## 5. Phase 2 - Workspace, Deals, Core Calculation Records

### Goal

Create the core deal/calculation object model before running calculations.

### Deliverables

- Workspace model.
- Asset/security model.
- Calculation model.
- Calculation input version model.
- Business deals dashboard.
- Calculation list/detail.
- Create/edit/archive calculation.
- Save and reopen calculation inputs.

### Acceptance Criteria

- Business user can create and save a calculation.
- User can reopen saved calculation.
- Editing inputs creates a new input version.
- User cannot access another user's private calculation.
- Admin can inspect calculation metadata where authorized.

### Validation Focus

- Ownership tests.
- Input version immutability tests.
- Deals table usability and filtering.

## 6. Phase 3 - Parameter Sets And Calculation Engine Integration

### Goal

Prove reproducible, parameterized Python calculation runs.

### Deliverables

- Python calculation engine package/module.
- Placeholder external asset return formula.
- Engine version exposure.
- Admin parameter set model.
- Draft/publish/deprecate workflow.
- Run execution endpoint.
- Run status model.
- Output display.
- Rerun support.
- Audit event for run/rerun.

### Acceptance Criteria

- Admin can create and publish parameter set.
- Published parameter set is immutable.
- Business user can run a calculation.
- Run stores engine version, parameter set, input version, input hash, actor, and timestamp.
- Rerun creates a new run.
- Output view shows key metrics, warnings, and provenance.

### Validation Focus

- Calculation deterministic tests.
- Parameter immutability tests.
- Run persistence tests.
- Output UI state tests.

## 7. Phase 4 - Calculation Portal Polish

### Goal

Turn the calculation detail into the polished workbench experience.

### Deliverables

- Guided setup sections.
- Validation summary.
- Metric band.
- Output tables.
- Run history drawer.
- Parameter set detail drawer.
- Permission-aware action bar.
- Save/run/compare/share/export action placement.
- Empty, warning, failed, running, and completed states.

### Acceptance Criteria

- Users understand what to do next on draft, ready, running, failed, and complete calculations.
- Output provenance is visible without cluttering the main view.
- Tables are readable and compact.
- No overlapping controls or unclear action groups.

### Validation Focus

- UX review.
- Frontend TypeScript module and view-state tests.
- Manual visual QA across standard desktop/laptop widths.

## 8. Phase 5 - Scenarios And Comparison

### Goal

Support base and alternate scenario work.

### Deliverables

- Scenario model.
- Create/copy/edit/delete scenario.
- Scenario-specific input overrides.
- Scenario run endpoint.
- Scenario comparison view.
- Scenario export/report linkage.

### Acceptance Criteria

- User can create multiple scenarios for one calculation.
- User can run each scenario.
- Comparison view shows metrics and deltas.
- Scenario runs preserve exact inputs, parameters, engine version, and timestamp.

### Validation Focus

- Scenario override tests.
- Comparison accuracy tests.
- UX review for dense comparison table.

## 9. Phase 6 - Reports And Exports

### Goal

Provide governed output artifacts.

### Deliverables

- Report model.
- Report generation workflow.
- Values-only export.
- Full report export where permitted.
- Report list screen.
- Download endpoint.
- Export audit events.

### Acceptance Criteria

- User can generate a permitted report from a run.
- User with only view permission cannot export if not granted.
- Values-only export is clearly distinguished from full output export.
- Download activity is audited.

### Validation Focus

- Export permission tests.
- Report metadata tests.
- Download audit tests.

## 10. Phase 7 - Sharing, Comments, Tasks, Notifications

### Goal

Enable controlled collaboration.

### Deliverables

- Share grants.
- Share modal.
- Shared with me screen.
- Comment panel.
- Task panel.
- Notification drawer/list.
- Object-level permission checks across shared resources.

### Acceptance Criteria

- Owner can share a calculation with view access.
- Owner can grant edit/collaboration access.
- Export permissions remain explicit.
- Comments and tasks are visible only to authorized users.
- Comments/tasks trigger notifications.

### Validation Focus

- Object-level permission tests.
- Share revoke tests.
- Notification access tests.

## 11. Phase 8 - Batch Processing

### Goal

Support uploaded bulk calculations with row-level validation and results.

### Deliverables

- Batch upload screen.
- Upload template download.
- CSV/XLSX parsing decision.
- Batch job model.
- Row validation.
- Valid/invalid row preview.
- Batch execution.
- Row-level result/error view.
- Batch result export.

### Acceptance Criteria

- User can upload a batch file.
- Invalid rows are shown with row-level errors.
- Valid rows can be run.
- Batch produces row-level results and errors.
- Batch export respects permissions.

### Validation Focus

- Parser tests.
- Mixed valid/invalid row tests.
- Batch permission tests.
- Large table UX review.

## 12. Phase 9 - Admin Output Explorer, Audit, Hardening

### Goal

Complete enterprise oversight and hardening.

### Deliverables

- Admin output explorer.
- Admin audit log search.
- Resource history timeline.
- Run monitor.
- Batch monitor.
- Permission test expansion.
- Calculation reproducibility test suite.
- Performance pass for lists and filters.
- Error and empty-state pass.

### Acceptance Criteria

- Admin can search/filter outputs.
- Admin can inspect run provenance and failures.
- Business users see only relevant history.
- Sensitive actions create audit records.
- Permission tests cover owner, shared view, shared edit, export, admin, disabled user, and pending user paths.

### Validation Focus

- Authorization regression suite.
- Audit completeness review.
- Query/index review.
- UX pass for admin density.

## 13. Risk-Based Sequencing Notes

| Risk | Mitigation |
|---|---|
| Calculation formula remains undefined | Use replaceable placeholder model, but freeze input/output contract shape early. |
| UI becomes cluttered | Keep one dominant table or work surface per screen and move secondary detail into drawers. |
| Permission model becomes inconsistent | Centralize authorization and test every role/resource/action combination. |
| Runs are not reproducible | Store input version, parameter set, engine version, hashes, timestamps, and actor for every run. |
| Oracle schema becomes too rigid | Use relational structure for governance fields and JSON payloads for flexible calculation inputs/outputs. |
| Batch scope expands too early | Build single-run path first; batch later reuses validated calculation contract. |

## 14. Implementation Readiness Checklist

Implementation should not begin until the team has decided:

- First placeholder calculation fields.
- Required asset/security identifier types.
- Initial parameter set fields.
- Account approval policy.
- Initial export formats.
- Batch upload template columns.
- Whether admin and SME are one role or separate roles.
- Whether local auth is acceptable for the first build.
- Oracle schema ownership and migration process.
