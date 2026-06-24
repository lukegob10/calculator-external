# Open Questions

## 1. Product Decisions

1. What is the exact first calculation domain?

   The scaffold assumes an external asset/security return calculator with ROTCE-like analysis, tax rates, asset values, pricing assumptions, and scenario comparison. The first build needs a concrete placeholder field set even if the final formula arrives later.

2. What should the primary business object be called in the UI?

   Options: deal, calculation, asset analysis, security analysis, return case. The dashboard can show "Deals" while the backend uses "calculation," but the product language should be intentional.

3. Which users are included in the first release?

   Current assumption: BUSINESS_USER and ADMIN. A separate SME, reviewer, or read-only role can be added later if needed.

4. Should the first screen after login be a deals dashboard or a workspace dashboard?

   Current recommendation: business users land on a deals dashboard because it directly answers "what am I working on?"

5. What does success look like for a completed calculation?

   The app should distinguish a technically completed run from a business-clean result with no warnings, current data, approved parameters, and valid inputs.

## 2. Calculation Decisions

1. What is the exact external return formula?

   The placeholder can model asset value, tax rate, balance, price, spread, and capital assumptions, but production requires the authoritative formula.

2. Which fields are required?

   Candidate groups: asset identifier, asset value, balance, price, spread/rate, tax rate, capital allocation, maturity date, scenario label.

3. Which fields are user-entered versus admin-controlled?

   Admin-controlled values should live in parameter sets. User-entered values should live in input versions. System-derived values need source metadata.

4. Are tax rates simple scalar values or structured by jurisdiction, asset type, date, and treatment?

   This affects both parameter set design and the UI editor.

5. Are calculations expected to run instantly?

   The plan supports asynchronous status even if first runs are fast. Confirm whether users need live polling, queued jobs, or immediate responses.

6. Should partial results be displayed when some components fail?

   Options: fail the full run, show component-level failures, or allow completed-with-warnings.

## 3. Data And Oracle Decisions

1. Who owns the Oracle schema?

   The implementation plan depends on whether the project can create and migrate tables or must submit DDL through an enterprise process.

2. Are JSON payload columns acceptable in Oracle for calculation inputs and outputs?

   JSON payloads are recommended for flexible calculation structures, while relational columns should be used for searchable governance fields.

3. Which data must be snapshotted for reproducibility?

   Full input and output payloads should be persisted. Source-derived data may need full snapshotting, source timestamps, query hashes, or source record references.

4. What are retention requirements?

   Runs, reports, audit events, uploads, and comments may have different retention policies.

5. Which fields must be indexed for reporting and admin search?

   Likely filters: user, asset identifier, status, run timestamp, parameter set, engine version, batch job, and event type.

## 4. UX Decisions

1. What should the first dashboard table columns be?

   Current recommendation: deal/calculation, asset, status, latest external return, tax impact, parameter set, updated time, and actions.

2. What metrics belong in the calculation output band?

   Candidate metrics: external return, ROTCE-like metric, net tax impact, projected value, sensitivity delta, warnings count.

3. Which actions deserve primary placement?

   Recommended calculation action bar: Run, Save, Compare, Share, Export, More.

4. Should advanced inputs be hidden by default?

   Current recommendation: yes. Use progressive disclosure to keep the portal clean.

5. What should be handled in pop-outs versus full pages?

   Recommended pop-outs: share, export, run detail, parameter detail, comments/tasks. Full pages: calculation setup/output, batch upload, admin tables.

## 5. Admin Decisions

1. Are Admin and SME the same role in the first release?

   The scaffold treats them as one privileged role. Splitting later may be necessary if SMEs can manage parameters but not users.

2. Who can publish parameter sets?

   Publishing changes calculation behavior and should be restricted to admin/SME users.

3. Should parameter publication require approval?

   The first release can support direct publish by admin, but production may need draft/review/approve workflow.

4. What can admins do with user calculations?

   Options include view-only support access, full rerun access, export access, or restricted access with audit.

5. What should the admin output explorer expose?

   It should at least expose calculation run, user, asset, parameter set, status, timestamps, warnings, errors, and report links.

## 6. Security And Governance Decisions

1. Is local username/SOEID and password acceptable for the first release?

   The source spec allows local auth initially, but enterprise SSO may supersede this.

2. Should new accounts default to pending?

   Current recommendation: yes, unless enterprise policy explicitly allows auto-activation.

3. Are exports allowed for all owners?

   Export policy should distinguish values-only export from full report/export.

4. Which events must be audited?

   Minimum: login, account approval, role changes, parameter publishing, calculation run/rerun, export/download, share grant/revoke, batch upload/run, admin inspection.

5. Are calculation outputs sensitive?

   If yes, sharing, exports, audit logs, and reports need stricter handling.

## 7. Reporting And Batch Decisions

1. What output formats are required?

   Options: CSV, XLSX, PDF, HTML, JSON. Values-only export may be CSV/XLSX while full reports may be PDF/HTML.

2. What columns belong in the batch upload template?

   The batch template should match the first calculation input contract.

3. Should invalid batch rows block the full batch?

   Recommended: show row-level validation, allow valid rows to run only after user confirmation.

4. Should batch jobs support reruns?

   If yes, reruns should create new run records per row and preserve original batch evidence.

## 8. Implementation Sequencing Decisions

1. Should scenarios be included before reports?

   Current plan adds scenarios before reports because scenario comparison is core to understanding asset performance.

2. Should batch upload come before sharing?

   Current plan adds sharing before batch because object-level permissions affect exports, reports, and collaboration broadly.

3. How polished should Phase 1 be visually?

   Even early phases should establish the final shell, navigation, table, form, and modal patterns. Avoid throwaway UI that must be fully redesigned later.

4. What is the first vertical slice demo?

   Recommended demo: admin publishes a parameter set, business user creates an asset calculation, runs it, reviews output/provenance, reruns it, and sees both run records.

## 9. Decisions Needed Before Coding Starts

These decisions are most important before implementation:

1. Confirm plain TypeScript frontend with standard npm scripts and Python/FastAPI backend.
2. Confirm Oracle persistence approach and schema ownership.
3. Confirm local auth versus enterprise SSO for first release.
4. Confirm first calculation input field set.
5. Confirm first parameter set fields.
6. Confirm business dashboard language: deals versus calculations.
7. Confirm export formats for first release.
8. Confirm admin versus SME role split.
9. Confirm account approval default.
10. Confirm whether batch upload is included in the first milestone or deferred.
