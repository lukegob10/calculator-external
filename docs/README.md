# Enterprise Calculation Workspace Documentation Scaffold

This folder is a planning scaffold only. It intentionally contains no application source code, migrations, tests, package manifests, deployment scripts, or generated UI assets.

The attached product specification describes a polished enterprise calculation workspace for asset/security analysis, scenario comparison, reports, sharing, and admin-managed calculation parameters. These docs translate that specification into implementation-ready planning artifacts so the team can decide whether the product shape, data model, and delivery plan are strong enough before code is written.

## Document Map

| Document | Purpose |
|---|---|
| [application-scaffold.md](application-scaffold.md) | Product-level scaffold, role surfaces, navigation model, and expected application shape. |
| [ux-blueprint.md](ux-blueprint.md) | Screen-by-screen UX plan, visual language, interaction patterns, pop-out windows, tables, and states. |
| [ui-mockups.html](ui-mockups.html) | Static high-fidelity UI mockups for login, business dashboard, calculation portal, scenario comparison, admin, application access, sharing/revocation, parameters, and batch upload. |
| [data-model.md](data-model.md) | Domain entities, relationships, lifecycle rules, audit requirements, and Oracle persistence shape. |
| [technical-architecture.md](technical-architecture.md) | TypeScript/Python architecture, module boundaries, calculation engine ownership, and security boundaries. |
| [api-contract-scaffold.md](api-contract-scaffold.md) | Resource-oriented API surface, request/response conventions, and endpoint group responsibilities. |
| [dependencies-and-standards.md](dependencies-and-standards.md) | Recommended stack, dependency categories, engineering standards, and primary-source references. |
| [package-security-review.md](package-security-review.md) | Dependency approval, supply-chain security checks, lockfile rules, audit gates, and package rejection criteria. |
| [implementation-dependency-review.md](implementation-dependency-review.md) | Package review record for dependencies introduced in the first implementation slice. |
| [product-hardening-backlog.md](product-hardening-backlog.md) | Prioritized backlog for turning the working foundation into a polished enterprise product. |
| [phased-implementation-plan.md](phased-implementation-plan.md) | Sequenced project phases, deliverables, acceptance criteria, and validation focus. |
| [open-questions.md](open-questions.md) | Decisions required before production hardening and questions that affect scope or data design. |

## Product North Star

The application should feel like a light, precise enterprise workbench: clear tables, compact panels, restrained accent color, polished empty states, and focused workflows. The design target is closer to Apple or Linear than a heavy legacy admin portal, but it must still feel credible for finance, auditability, and controlled calculation work.

## Non-Implementation Boundary

The scaffold may describe future folders, modules, APIs, screens, data structures, and dependency choices. It must not create those folders as application code yet.

Do not add at this stage:

- Frontend source files.
- Backend source files.
- Python calculation engine files.
- Database migrations.
- Package manifests.
- Build, CI, deployment, or container configuration.
- Mock implementation services.

## Working Assumptions

- Frontend language: TypeScript.
- Frontend approach: plain TypeScript compiled with standard npm scripts, using browser DOM APIs, HTML, CSS, and `fetch`. No frontend application framework or client-side data library.
- Backend language: Python.
- Backend API framework: FastAPI.
- Database: Oracle, accessed only through backend APIs.
- Calculation engine: Python package owned by the backend application boundary, with formulas isolated from route handlers and UI code.
- First release uses local username/SOEID and password unless enterprise identity requirements supersede it.
- Admin/SME users manage parameter sets, templates, users, outputs, batch jobs, and audit views.
- Business users create calculations, run scenarios, compare outputs, share work, and export permitted results.

## Readiness Definition

The team is ready to implement when these docs answer, or explicitly defer, the following:

- What the first calculation object is.
- Which inputs are user-entered, admin-controlled, and system-derived.
- How runs are versioned and reproduced.
- Which roles can view, edit, export, share, approve, and rerun work.
- What the initial UI screens look like and how they connect.
- What is persisted in Oracle.
- What the first vertical implementation slice proves.
