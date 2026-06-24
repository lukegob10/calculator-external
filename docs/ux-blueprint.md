# UX Blueprint

## 1. Design Direction

The product should feel modern, light, and precise: a professional calculation workspace with enough polish to feel premium, but not a decorative consumer app. The visual reference should be closer to Apple and Linear: calm surfaces, clean type, restrained depth, crisp icons, careful spacing, and a few confident accent colors.

Avoid:

- Large walls of identical cards.
- Oversized hero sections after login.
- Decorative bubbles, gradients, or color blocks that compete with data.
- Low-density dashboards where important work is pushed below the fold.
- Flat tables with no hierarchy, grouping, or action clarity.

Use:

- One primary work surface per screen.
- Compact status strips.
- Tables with strong scanning affordances.
- Slide-over panels for secondary detail.
- Modal pop-outs for focused actions.
- Subtle elevation, hairline borders, and restrained shadows.
- Icon-led controls for upload, download, share, compare, rerun, filter, and history.

## 2. Visual System

### 2.1 Color

Use a mostly neutral light interface with a small number of accent colors.

| Token | Intent | Example direction |
|---|---|---|
| Background | Main app surface | warm white or near-white neutral. |
| Panel | Tables, drawers, grouped inputs | white with subtle border. |
| Raised panel | Pop-outs and modals | white, light shadow, 8px radius. |
| Primary accent | Main actions and selected states | refined blue or graphite-blue. |
| Positive | Successful runs and favorable deltas | restrained green. |
| Warning | Warnings, stale data, unusual inputs | amber. |
| Critical | Failed runs, blocked tasks, permission errors | red. |
| Informational | Shared state, pending state, draft state | blue or slate. |

Do not let the product become a one-note blue dashboard. Use neutrals for structure and color only for meaning.

### 2.2 Typography

- Use a system font stack or enterprise-approved sans serif.
- Keep headings tight and readable.
- Use tabular numbers for metrics and tables.
- Avoid viewport-scaled type.
- Use regular and medium weights; reserve bold for key labels and important values.

### 2.3 Shape And Depth

- Cards and panels should use 6px to 8px radius.
- Buttons and inputs can use 6px to 8px radius.
- Avoid pill-shaped everything.
- Use subtle shadows only for pop-outs, menus, and active drag/hover states.
- Use borders for normal information density and shadows for layered UI.

### 2.4 Icons

Use recognizable icons for repeated commands:

| Action | Icon direction |
|---|---|
| New calculation | plus or calculator. |
| Upload | upload cloud or arrow-up tray. |
| Download/export | download or arrow-down tray. |
| Share | share nodes or user-plus. |
| Compare | columns, split view, or diff. |
| Rerun | rotate/refresh. |
| Filter | funnel. |
| History/audit | clock or list timeline. |
| Comments | message bubble. |
| Tasks | check-square. |

Buttons with unfamiliar icons should have tooltips. Primary actions should usually include icon plus text.

## 3. Layout Principles

### 3.1 Business Dashboard

Primary layout:

```text
Top bar
Left nav | Page header + actions
         | Status strip
         | Deals table                         | Right activity rail
         | Recent outputs / scenario comparisons
```

The deals table should be the dominant surface. Summary metrics should support the table, not replace it.

Recommended table columns:

| Column | Notes |
|---|---|
| Deal / calculation | Name, asset identifier, small secondary description. |
| Asset type | Badge or compact text. |
| Status | Draft, ready, running, complete, failed, shared. |
| Latest metric | External return or ROTCE-like value. |
| Delta | Change from base or last run where applicable. |
| Parameter set | Published version label. |
| Updated | Relative and exact on hover. |
| Actions | Open, run/rerun, share, export menu. |

### 3.2 Calculation Portal

The calculation portal should feel like a controlled cockpit, not a form dump.

```text
Title row: Calculation name, asset, status, owner, sharing
Action row: Run | Save | Compare | Share | Export | More

Left column:       Main work area:                 Right drawer:
- Scenario selector - Key metric band              - Parameters
- Input sections   - Output tables/charts          - Run history
- Validation       - Warnings and notes            - Comments/tasks
```

Input sections:

- Asset details.
- Pricing assumptions.
- Tax assumptions.
- Capital/ROTCE assumptions.
- Scenario overrides.
- Advanced settings, collapsed by default.

Output sections:

- Key metrics band.
- Return decomposition.
- Tax impact table.
- Value sensitivity table.
- Applied assumptions.
- Warnings and validation notes.
- Run provenance.

### 3.3 Admin Console

The admin console should be compact and operational.

```text
Top bar
Left nav | Admin header + environment/status
         | System status strip
         | Recent runs / failures table           | Pending work rail
         | Parameter activity + audit highlights
```

Admin users need dense tables, saved filters, and fast drill-in. Use pop-out detail panels for:

- Run detail.
- User profile/activity.
- Parameter set diff.
- Audit event detail.
- Batch row error detail.

## 4. Pop-Out Windows And Panels

Use pop-outs for focused, reversible tasks:

| Pop-out | Type | Contents |
|---|---|---|
| Share calculation | Modal | Grantee search, permission level, expiration/revocation, message. |
| Export output | Modal/menu | Values-only, report, permitted formats, audit note. |
| Run details | Slide-over | Input hash, parameter set, engine version, warnings, errors. |
| Parameter set detail | Slide-over | Version, status, payload summary, publish history. |
| Comments/tasks | Slide-over | Thread, task list, assignment, due dates. |
| Upload validation | Modal or full page | File summary, row errors, valid row count, run action. |

Pop-outs should never hide permission errors. If a user lacks export or edit rights, show the disabled action with a concise reason.

## 5. Table Standards

All high-value tables should support:

- Search.
- Column sorting.
- Filter chips.
- Pagination.
- Column visibility where tables are wide.
- Saved views for admin-heavy screens.
- Status badges.
- Row-level action menu.
- Empty state with next action.
- Loading skeleton.
- Permission-aware disabled actions.

Important tables:

- Deals/calculations.
- Scenario comparison.
- Calculation runs.
- Reports.
- Users.
- Parameter sets.
- Batch jobs and batch rows.
- Audit events.
- Output explorer.

## 6. Screen Inventory

### Public Screens

| Screen | Key UX requirement |
|---|---|
| Login | Clean, centered, enterprise-credible; username/SOEID and password; account creation link. |
| Create account | Full name, SOEID, password, confirm password; pending approval state. |
| Pending approval | Clear state, no app access, contact/admin guidance. |
| Auth error | Specific but secure error copy. |

### Business Screens

| Screen | Key UX requirement |
|---|---|
| Deals dashboard | Dominant deals table, quick create, batch upload, activity rail. |
| My workspace | Saved calculations, folders/views if needed, filters. |
| Calculation setup | Guided sections, validation summary, parameter visibility. |
| Calculation output | Metrics, tables, warnings, provenance, export/report actions. |
| Scenario comparison | Side-by-side scenarios, deltas, highlight best/worst. |
| Batch upload | Drag/drop, template download, validation preview, row errors. |
| Shared with me | Objects grouped by permission and owner. |
| Reports | Downloadable outputs, run linkage, permission labels. |
| Tasks | Assigned work, due state, linked resource. |
| Notifications | Actionable updates with resource links. |
| Resource history | Timeline of run, edit, share, export, and comment activity. |

### Admin Screens

| Screen | Key UX requirement |
|---|---|
| Admin console | Status strip, recent failures, pending approvals, recent activity. |
| Application access | Pending users, active/disabled users, role assignments, access grants, and access audit. |
| User management | Searchable table, approve/disable/role actions, profile drawer. |
| Sharing and revocation | Current resource grants, permission levels, share pop-out, revoke controls, grant history. |
| Parameter sets | Draft/published/deprecated tabs, version history, diff preview. |
| Parameter editor | Structured editor with validation and publish confirmation. |
| Templates | Calculation/report/batch templates with active/inactive status. |
| Output explorer | Deep filtering across user, asset, status, parameter, date, run. |
| Run monitor | Queue state, failures, rerun controls, engine/version context. |
| Batch monitor | Job status and row-level drill-in. |
| Audit log | Immutable event table with filters and resource drill-through. |

## 7. State Design

Every screen should define these states:

- Loading.
- Empty.
- Error.
- Permission denied.
- Validation failed.
- Unsaved changes.
- Running/queued.
- Completed with warnings.
- Completed cleanly.
- Failed/cancelled.

Calculation-specific states:

| State | UX treatment |
|---|---|
| Draft | Quiet badge, save prompt, run disabled until required inputs pass. |
| Ready | Primary run action enabled. |
| Queued/running | Progress indicator, run ID visible, avoid duplicate run. |
| Complete | Metric band and output tables visible. |
| Complete with warnings | Warning badge and expandable warnings. |
| Failed | Structured error panel and rerun/edit options where allowed. |
| Shared | Sharing badge and permission detail available. |

## 8. Example First-Release Landing Page Content

### Business Dashboard

Top status strip:

- Open drafts: 7.
- Completed this week: 23.
- Shared with me: 5.
- Tasks due: 3.
- Latest parameter set: Tax Methodology v3.2.

Main deals table examples:

| Deal | Asset | Status | External return | Tax impact | Updated | Actions |
|---|---|---:|---:|---:|---|---|
| Alpha Credit Base | CUSIP 123456AB | Complete | 12.4% | -1.8% | Today | Open, Compare, Export |
| June Downside Case | Internal SEC-44 | Warning | 8.1% | -2.6% | Yesterday | Open, Rerun |
| New Asset Draft | TBD | Draft | - | - | Jun 20 | Continue |

### Admin Console

Status strip examples:

- Queue: 2 running.
- Failed runs: 4 today.
- Pending users: 6.
- Current parameter set: Published v3.2.
- Data freshness: Tax rates current, market inputs stale warning.

Main admin table examples:

| Run | User | Asset | Status | Parameter set | Engine | Started | Actions |
|---|---|---|---|---|---|---|---|
| RUN-2026-00941 | A. Patel | CUSIP 123456AB | Complete | v3.2 | 1.0.0 | 09:41 | Inspect |
| RUN-2026-00942 | M. Chen | SEC-44 | Failed | v3.2 | 1.0.0 | 09:48 | Inspect, Rerun |

## 9. Accessibility And Usability Bar

- Keyboard navigation for forms, tables, pop-outs, menus, and drawers.
- Visible focus states.
- No color-only status communication.
- Clear validation text near the field and summary at the top.
- Compact but readable row heights.
- Touch-friendly minimums for critical controls, even though mobile-specific UI is out of scope.
- Download/upload actions labeled clearly and backed by icons.
- Tables should remain usable at laptop widths without horizontal chaos.
