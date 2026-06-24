# Dependencies And Engineering Standards

## 1. Purpose

This document recommends the dependency categories and engineering standards for the future implementation. It is intentionally not a package manifest.

All package choices must also pass the dependency security process in [package-security-review.md](package-security-review.md). The default posture is to avoid packages unless they materially reduce risk or complexity.

## 2. Stack Decision

| Layer | Recommendation | Rationale |
|---|---|---|
| Frontend language | TypeScript | Strong contracts for API data, domain types, form state, and role-aware UI. |
| Frontend approach | Plain TypeScript, HTML, CSS, and browser DOM APIs | Keeps the client simple, dependency-light, and easy to audit. |
| Frontend build tool | Standard npm scripts using the TypeScript compiler | Avoids framework lock-in, bundler assumptions, and unnecessary client complexity. |
| Backend language | Python | Required by calculation engine and fits FastAPI/Pydantic validation. |
| Backend API | FastAPI | Python type-hint-based API framework with OpenAPI support. |
| API validation | Pydantic models | Request/response schemas, validation, and typed contracts. |
| Database | Oracle | System of record for application and calculation evidence. |
| Database access | SQLAlchemy with Oracle driver or disciplined repository layer | Centralized Oracle access and parameterized operations. |
| Calculation engine | Python package/module behind backend service layer | Keeps formulas isolated and testable. |
| Reports/exports | Backend-generated documents/files | Enforces permissions and audit around export activity. |

Primary-source references checked for stack direction:

- [FastAPI documentation](https://fastapi.tiangolo.com/) describes FastAPI as a Python API framework based on standard type hints.
- [TypeScript documentation](https://www.typescriptlang.org/docs/handbook/2/basic-types.html) covers the `tsc` compiler and npm-based setup.
- [MDN DOM documentation](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model) documents browser DOM APIs for page structure and behavior.
- [MDN Fetch API documentation](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API) documents browser-native HTTP requests.
- [npm audit documentation](https://docs.npmjs.com/auditing-package-dependencies-for-security-vulnerabilities/) documents dependency vulnerability auditing.
- [npm trusted publishing documentation](https://docs.npmjs.com/trusted-publishers/) documents OIDC-based publishing without long-lived tokens.
- [OpenSSF Scorecard](https://scorecard.dev/) documents automated supply-chain security checks.
- [SLSA](https://slsa.dev/) documents supply-chain integrity controls and provenance.
- [GitHub Dependabot security updates](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-security-updates) documents automated vulnerability update pull requests.
- [SQLAlchemy Oracle dialect documentation](https://docs.sqlalchemy.org/en/latest/dialects/oracle.html) documents Oracle support and dialect behavior.

## 3. Frontend Dependency Categories

| Category | Recommendation |
|---|---|
| Routing | Simple TypeScript route/view modules backed by server authorization. |
| Server calls | Small typed `fetch` helpers; no client-side data library. |
| Forms | Native HTML forms and TypeScript validation/display helpers. |
| Tables | Reusable plain TypeScript table module with sorting, filtering, pagination, column visibility, and row actions. |
| Icons | Simple approved icon approach for upload, download, share, compare, filter, rerun, history, comments, and tasks. Prefer inline SVG assets or a very small icon package only if approved. |
| Styling | Design-token-driven CSS with reusable classes and layout primitives. |
| Testing | TypeScript unit tests for utility/view modules plus integration/e2e tests for critical flows. |
| Accessibility | Tooling for focus states, keyboard coverage, contrast, and semantic UI checks. |

Frontend standards:

- Enable strict TypeScript.
- Do not use a frontend framework or client-side data library.
- Prefer standard npm scripts: `typecheck`, `build`, `test`, and `dev` if needed.
- Use native DOM APIs and standard `fetch`.
- Keep domain types centralized.
- Keep API clients centralized.
- Keep business and admin route modules separated.
- Use reusable table/form/modal/drawer primitives.
- Show explicit loading, empty, validation, permission denied, warning, and error states.
- Do not put financial logic or permission enforcement in frontend view modules.

## 4. Backend Dependency Categories

| Category | Recommendation |
|---|---|
| API framework | FastAPI. |
| Runtime server | Uvicorn or enterprise-approved ASGI server setup. |
| Validation | Pydantic request/response schemas. |
| Database | Oracle driver and SQLAlchemy/repository layer. |
| Auth | Password hashing library supporting Argon2id or bcrypt. |
| Authorization | Central permission module invoked by services/endpoints. |
| Audit | Central audit service writing append-only events. |
| Background work | Start with run status model; add worker/queue only when calculation duration requires it. |
| Reports | Backend report generation utilities selected by required output formats. |
| Testing | Pytest or enterprise-approved Python test runner. |

Backend standards:

- Use type hints.
- Keep route, schema, service, repository, model, and calculation engine boundaries separate.
- Validate every request.
- Return structured errors.
- Use parameterized SQL or ORM-safe operations.
- Never expose password hashes.
- Never log passwords or session tokens.
- Audit sensitive events.
- Keep calculation formulas out of route handlers.

## 5. Database Standards

Oracle should persist:

- Users and roles.
- Workspaces.
- Assets/securities.
- Calculations.
- Input versions.
- Scenarios.
- Parameter sets.
- Calculation runs.
- Reports/exports.
- Share grants.
- Comments/tasks/notifications.
- Batch jobs and row-level items.
- Audit events.
- Templates.

Database standards:

- Use relational columns for identifiers, statuses, timestamps, ownership, and filterable fields.
- Use JSON payloads for flexible calculation inputs, outputs, warnings, errors, and parameter payloads.
- Add indexes for common search/filter paths.
- Treat published parameter sets and completed runs as immutable evidence.
- Avoid direct frontend database access.

## 6. Security Standards

| Area | Standard |
|---|---|
| Authentication | Secure password hashing; no plaintext passwords; session expiration. |
| Authorization | RBAC plus object-level permissions on every protected endpoint. |
| Account creation | New users default to pending unless enterprise policy allows auto-activation. |
| Admin privileges | Users cannot self-assign elevated roles. |
| Exports | Permission checked and audited. |
| Audit logs | Append-only and free of secrets. |
| Validation | Backend validates all payloads; frontend validation is UX only. |

## 7. Calculation Standards

The calculation engine must be:

- Deterministic for fixed inputs and parameters.
- Versioned.
- Isolated from API route handlers.
- Unit-tested separately.
- Able to return warnings for unusual but valid inputs.
- Able to return structured errors for invalid or failed calculations.
- Able to expose the exact parameter set and engine version used for a run.

## 8. UI Quality Standards

The implementation should provide:

- Compact enterprise layouts.
- Strong data tables.
- Slide-over panels for contextual detail.
- Modals for focused actions.
- Clear upload/download/share/compare/rerun icons.
- Consistent status badges.
- Design tokens for spacing, radius, color, type, and elevation.
- Responsive laptop/desktop layouts.
- No overlapping text or controls.
- No decorative visual clutter that weakens trust.

## 9. Testing Standards

### Backend

- Auth success/failure.
- Account creation validation.
- Role assignment restrictions.
- Object-level authorization.
- Calculation input validation.
- Run persistence and rerun behavior.
- Parameter set publish/deprecate behavior.
- Export permission enforcement.
- Audit event creation.

### Calculation Engine

- Deterministic output.
- Invalid input rejection.
- Scenario override application.
- Warning generation.
- Engine version exposure.

### Frontend

- Login/account creation validation.
- Role-based navigation.
- Business dashboard sections.
- Admin dashboard sections.
- Calculation setup validation.
- Permission denied states.
- Table filtering and action visibility.

### Integration

- Business user creates, runs, saves, and exports a calculation.
- Owner shares a calculation view-only.
- Shared user cannot edit without edit permission.
- Admin publishes a parameter set and runs reference the exact version.
- Batch upload reports row-level mixed success/failure.

## 10. Dependency Decision Criteria

When selecting exact packages during implementation, prefer dependencies that:

- Are actively maintained.
- Support strict typing or clear schemas.
- Fit plain TypeScript and FastAPI idioms.
- Support accessible UI patterns without forcing a heavy framework.
- Do not force a heavy visual style incompatible with the desired product.
- Work cleanly with enterprise security review.
- Can be tested without elaborate infrastructure.

Reject dependencies that:

- Are not clearly necessary.
- Have a small maintainer base and broad transitive dependency tree.
- Require install scripts without a strong reason.
- Have unresolved critical/high vulnerabilities.
- Have suspicious ownership, recent unexplained maintainer changes, or poor release hygiene.
- Cannot be pinned and reproduced through lockfiles.
