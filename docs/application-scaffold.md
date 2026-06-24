# Enterprise Calculation Workspace - Application Scaffold

## 1. Intent

Build a polished enterprise calculation workspace for external asset/security analysis. Business users should be able to create a calculation, enter or upload assumptions, run deterministic Python-backed calculations, compare scenarios, save outputs, share work, and generate governed reports. Admin/SME users should be able to control users, parameter sets, tax rates, assumptions, templates, output history, batch activity, and audit evidence.

This document describes what the application should look like structurally before implementation begins. It is not an implementation plan and does not create source code.

## 2. Product Shape

The product has two primary surfaces:

| Surface | Primary user | Purpose |
|---|---|---|
| Business Workspace | Business users, analysts, deal teams | Create, run, compare, save, share, and export calculations. |
| Admin / SME Console | Admins, model owners, tax/risk SMEs, support users | Manage governed inputs, users, parameters, templates, runs, batch jobs, and audit activity. |

The application should feel like a financial workbench rather than a dashboard gallery. It needs clear hierarchy, compact layouts, tables that are easy to scan, and action menus that make permissions obvious.

## 3. Core User Journeys

### 3.1 Business User: Start From Deals

1. Log in.
2. Land on a clean deals/workspace dashboard.
3. See recent deals, drafts, completed runs, shared calculations, assigned tasks, and recent notifications.
4. Start a new calculation from a primary action near the top of the page.
5. Select or create an asset/security.
6. Enter calculation assumptions manually or upload a supported file.
7. Review the applied parameter set, tax assumptions, and methodology version.
8. Run calculation.
9. Review key metrics and output tables.
10. Compare with scenarios.
11. Save, share, export values, or generate a report.

### 3.2 Admin/SME: Govern Inputs And Outputs

1. Log in.
2. Land on the admin console.
3. Review system status, failed runs, queue health, data freshness, and recent admin activity.
4. Manage users and pending approvals.
5. Create or update draft parameter sets.
6. Validate and publish parameter sets.
7. Review all calculation outputs and rerun selected calculations when permitted.
8. Inspect audit history for sensitive activity.
9. Manage templates for calculations, reports, and batch uploads.

### 3.3 Collaboration: Share Without Losing Control

1. Owner opens a calculation.
2. Owner opens the share pop-out.
3. Owner grants view, edit, or export-values permission to another user.
4. Grantee receives a notification and sees the object in "Shared With Me."
5. Comments, tasks, and history remain attached to the calculation.
6. Export and edit actions are always backend-authorized.

## 4. Role-Specific Landing Pages

### Business Landing Page

The business landing page should focus on deals and work needing attention.

Recommended first viewport:

- Header row: page title, global search, notification icon, user menu.
- Primary action: "New Calculation" with a plus/calculator icon.
- Secondary action: "Batch Upload" with upload icon, visible only if permitted.
- Main table: deals/calculations with owner, asset, status, latest run, return metric, updated time, and quick actions.
- Right rail: tasks, notifications, and recent shared items.
- Lower section: recent outputs and saved scenario comparisons.

The layout should avoid a wall of same-sized cards. Use one dominant table, one compact activity rail, and one or two small summary strips.

### Admin Landing Page

The admin landing page should be operational and dense without feeling heavy.

Recommended first viewport:

- Header row: console title, environment badge, global search, notification icon, user menu.
- Status strip: queue state, failed runs, published parameter set, data freshness, pending users.
- Main table: recent calculation runs with filter chips and status indicators.
- Right rail: pending approvals, failed batch rows, recent parameter changes.
- Lower section: audit highlights and template activity.

Admin controls should use clear labels and restrained badges, not oversized marketing-style tiles.

## 5. Navigation Model

### Global Shell

The app shell should be shared across authenticated areas:

- Left navigation rail with icons and labels.
- Top bar with search, notifications, help, and profile.
- Main content area with breadcrumbs where depth requires it.
- Slide-over or pop-out panels for comments, tasks, sharing, export options, and run details.

### Business Navigation

| Area | Purpose |
|---|---|
| Deals | Primary landing table for saved calculations and assets. |
| Workspace | Personal workspace and calculation folders/views. |
| New Calculation | Guided calculation setup. |
| Scenarios | Scenario list and comparison views. |
| Batch Upload | Upload, validate, run, and export batch jobs. |
| Reports | Generated reports and downloadable outputs. |
| Shared With Me | Objects shared by other users. |
| Tasks | Assigned workflow items. |
| Activity | User-scoped history and notifications. |

### Admin Navigation

| Area | Purpose |
|---|---|
| Console | Admin landing page and system status. |
| Users | Account approvals, role management, disabled users. |
| Application Access | User activation, role assignment, active grants, revocation, and access audit. |
| Parameters | Tax rates, assumptions, methodology parameters, reference data. |
| Templates | Calculation, report, scenario, and batch templates. |
| Output Explorer | Search all calculations, runs, outputs, and reports. |
| Batch Monitor | Batch job status, row errors, and rerun controls. |
| Audit Log | System-wide audit search. |
| System Activity | Operational activity, failures, and health indicators. |

## 6. Calculation Portal Shape

The calculation detail should be the most refined workflow in the app.

Recommended layout:

- Title block: calculation name, asset/security, status, owner, sharing state.
- Action bar: Run, Save, Compare, Share, Export, More.
- Left panel: input groups and scenario selector.
- Center panel: output summary, result metrics, and charts/tables.
- Right slide-over: contextual details such as parameter set, run history, comments, tasks, or audit history.
- Bottom area: run history and scenario comparison table.

The portal should support three modes:

| Mode | Use |
|---|---|
| Setup | Enter asset details, assumptions, overrides, template selection, and validation review. |
| Output | Review completed metrics, warnings, parameter set, engine version, and export/report actions. |
| Compare | Compare base and alternate scenarios side-by-side with metric deltas. |

## 7. Example Calculation Domain Placeholder

The first implementation should use a placeholder calculation model that is business-like but replaceable.

Example input groups:

| Group | Example fields |
|---|---|
| Asset | Asset identifier, asset name, asset type, balance, currency, maturity date. |
| Pricing | price, spread, coupon/rate, expected sale price, mark date. |
| Tax | tax treatment, jurisdiction, admin-controlled tax rate, user override if permitted. |
| Capital / ROTCE | capital allocation, risk-weighted asset estimate, equity charge, target return. |
| Scenario | base case, upside, downside, custom overrides. |

Example output groups:

| Group | Example metrics |
|---|---|
| Return | external return, net return, annualized return, ROTCE-like metric. |
| Tax impact | tax-adjusted income, tax drag, effective tax rate. |
| Value impact | projected value, gain/loss, sensitivity to spread/rate/price. |
| Risk/context | warnings, validation notes, applied parameter set, engine version. |

This placeholder should be isolated later in the calculation engine so final formulas can replace it without changing the product contract.

## 8. Feature Inventory

### Business Features

| Feature | First-release expectation |
|---|---|
| Login/account creation | Local account flow with pending approval unless policy says otherwise. |
| Deals dashboard | Main landing table for calculations and assets. |
| Calculation setup | Guided, grouped, validated inputs. |
| Manual input | Structured fields with validation and help text. |
| Upload | CSV/XLSX-style batch upload path, with row validation later. |
| Save/reopen | Saved calculation metadata, inputs, runs, outputs, scenarios, reports. |
| Scenario comparison | Base versus alternate scenario metrics and deltas. |
| Sharing | View, edit, and export-values permissions. |
| Comments/tasks | Collaboration attached to resources. |
| Reports/exports | Permission-aware output generation and download. |

### Admin Features

| Feature | First-release expectation |
|---|---|
| User management | Approve, disable, assign role, inspect user activity. |
| Parameter management | Draft, validate, publish, deprecate parameter sets. |
| Tax/reference data | Managed as parameter payloads or reference tables. |
| Templates | Calculation, scenario, report, and batch upload templates. |
| Output explorer | Search/filter all runs, reports, assets, users, statuses. |
| Batch monitor | Inspect job and row-level failures. |
| Audit log | Search significant events and resource history. |
| System status | Run queue, failures, data freshness, parameter state. |

## 9. Scaffolding View

The eventual project structure should be understandable before it exists. The shape below is a planning reference only.

```text
external-calculator/
  docs/
    README.md
    application-scaffold.md
    ux-blueprint.md
    data-model.md
    technical-architecture.md
    api-contract-scaffold.md
    dependencies-and-standards.md
    phased-implementation-plan.md
    open-questions.md
  frontend/                 # future TypeScript application boundary
  backend/                  # future Python API and calculation engine boundary
  database/                 # future Oracle migration/design boundary
  tests/                    # future cross-surface test boundary
```

Future source folders are listed for orientation only. They should not be created until implementation is explicitly approved.

## 10. Quality Bar

The finished application should meet these standards:

- Role-specific screens with no irrelevant admin clutter in business workflows.
- Backend-authorized permissions for every protected action.
- Versioned input payloads, parameter sets, calculation runs, reports, and audit events.
- Deterministic calculation behavior for fixed inputs and parameters.
- Tables with filtering, saved views, pagination, sorting, status badges, and clear empty states.
- Slide-over panels and pop-out dialogs for secondary work, not disruptive page changes.
- Clear visual hierarchy with restrained accent colors.
- No redundant export/report concepts.
- No hidden recalculation or overwritten historical run outputs.
- No direct Oracle access from the frontend.
