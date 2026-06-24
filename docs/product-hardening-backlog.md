# Product Hardening Backlog

The first implementation is a working vertical foundation. It is not yet the polished enterprise product described by the specification. This backlog captures the remaining work needed to bring the application to that quality bar.

## 1. Product Gaps

| Priority | Area | Required work |
|---|---|---|
| P0 | Authorization | Expand permission tests across every endpoint and UI action: owner, view, edit, export-values, admin, pending, disabled. |
| P0 | Data persistence | Replace local SQLite adapter with Oracle repository configuration, migrations, indexes, and environment-specific connection handling. |
| P0 | Password security | Replace PBKDF2 standard-library placeholder with reviewed Argon2id or bcrypt package after dependency approval. |
| P0 | Error handling | Add consistent frontend error surfaces, backend error codes, and request IDs. |
| P0 | Audit | Make audit coverage exhaustive for account, role, share, revoke, run, rerun, export, parameter publish, and admin inspection events. |
| P1 | Calculation portal | Add true input edit workflow, input version history, validation summary, scenario tabs, run comparison, and parameter drawer. |
| P1 | Admin console | Add output explorer, run monitor, failed-run detail, user profile drawer, access-grant explorer, and admin audit search filters. |
| P1 | Sharing | Add share modal, grant expiry/reason, group support, export-specific controls, revoke confirmation, and grant history drill-in. |
| P1 | Parameter management | Add draft editor, validation, publish confirmation, diff view, deprecate flow, and immutable published detail page. |
| P1 | Batch processing | Add upload template, CSV/XLSX parser decision, row validation, batch run execution, row results, and batch export. |
| P2 | Reports | Add report generation, values-only export, full report export, report list, download permissions, and export audit trail. |
| P2 | Collaboration | Add comments, tasks, notifications, resource activity timeline, and task assignment permissions. |
| P2 | UI polish | Add skeleton loading states, pop-out panels, keyboard states, responsive table behavior, and visual QA for each screen. |

## 2. Next Recommended Build Slices

### Slice A - Access And Administration Hardening

- User detail drawer.
- Role-change confirmation.
- Active grant explorer.
- Owner/admin revoke confirmation.
- Backend permission matrix tests.
- Admin audit search filters.

Status after the second implementation pass:

- Done: admin access grant explorer API/UI.
- Done: admin user detail API/UI with owned calculation and grant counts.
- Done: admin-only tests for grant explorer and user detail.
- Remaining: role-change confirmation, revoke confirmation, export-specific admin workflows, and richer audit search filters.

### Slice B - Calculation Portal Completion

- Edit inputs and create new input versions from the UI.
- Show input hash, parameter set, engine version, and run timestamp.
- Add run history drawer and warnings panel.
- Add scenario placeholder route and comparison table.

### Slice C - Parameter Governance

- Admin draft parameter editor.
- Validate/publish/deprecate actions.
- Published version immutability tests.
- Parameter diff view.

### Slice D - Batch And Reports

- Upload template.
- Batch validation preview.
- Row-level error model.
- Values-only export.
- Export audit events.

## 3. Definition Of Polished

The product should not be considered polished until:

- A new user can understand what access they have and how to request more.
- An owner can share and revoke access without admin help.
- An admin can answer who has access to what and why.
- A calculation run always shows its exact input, parameter set, engine version, and warnings.
- Every table has useful empty, loading, error, and filtered states.
- The UI matches the high-fidelity mockup direction in spacing, density, alignment, and hierarchy.
- The dependency review gate is enforced for every added package.
- Tests cover the security-sensitive workflows, not just the happy path.
