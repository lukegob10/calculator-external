# Package Security Review

## 1. Purpose

This application should use as few third-party packages as practical. Every package creates supply-chain risk, transitive dependency risk, update risk, license risk, and operational review burden. The project should prefer standard library features, browser-native APIs, and small first-party modules before adding dependencies.

This document defines the security gate for any future npm or Python package.

## 2. Default Policy

The default answer to a new package is "no" until it passes review.

Allowed dependency reasons:

- It provides security-critical behavior that should not be handwritten, such as password hashing.
- It provides a required database, API, or file-format integration.
- It materially reduces complex, high-risk implementation code.
- It is required by the chosen backend framework or runtime.

Not enough by itself:

- Convenience.
- Styling preference.
- Trendiness.
- Saving a few lines of straightforward TypeScript or Python.
- Adding an abstraction that can be written safely in first-party code.

## 3. Frontend Package Policy

The frontend should stay minimal:

- Plain TypeScript.
- HTML.
- CSS.
- Browser DOM APIs.
- Standard `fetch`.
- Standard npm scripts.
- TypeScript compiler.

Do not add:

- Frontend application framework.
- Client-side data/query/cache library.
- Heavy component library.
- General-purpose state management library.
- Utility package for trivial browser or language features.
- Large icon package unless explicitly approved.

Preferred frontend dependency posture:

| Need | Preferred answer |
|---|---|
| DOM updates | First-party TypeScript modules. |
| API calls | First-party typed `fetch` helpers. |
| Tables | First-party table module unless requirements become too complex. |
| Forms | Native forms plus first-party validation helpers. |
| Modals/drawers | First-party accessible DOM modules. |
| Icons | Inline approved SVG assets or a tiny vetted icon set. |
| Date/number formatting | Browser `Intl` APIs where possible. |

## 4. Backend Package Policy

Python backend dependencies are expected but still reviewed.

Likely acceptable categories:

- FastAPI and its required runtime dependencies.
- Pydantic validation dependencies.
- Oracle database driver.
- SQLAlchemy if selected for the repository layer.
- Password hashing library supporting Argon2id or bcrypt.
- Test runner and coverage tools.
- Report/export generation libraries only when output formats are confirmed.

Reject backend packages used only for convenience when Python standard library or small first-party code is enough.

## 5. Required Review Before Adding Any Package

Every new direct dependency must have a short review record before it is added.

Required fields:

| Field | Required answer |
|---|---|
| Package name | Exact package name. |
| Ecosystem | npm, PyPI, or other. |
| Purpose | What problem it solves. |
| Owner | Who requested and who approves it. |
| Direct alternatives | Standard library/native option and at least one package alternative. |
| Why first-party code is insufficient | Specific reason. |
| Version | Exact approved version or range policy. |
| Transitive dependency count | Count and notable risky transitive packages. |
| License | License and compatibility status. |
| Vulnerability status | Audit result and known advisories. |
| Maintenance health | Release recency, issue activity, maintainer count, repo status. |
| Security posture | 2FA/provenance/signing/Scorecard/SLSA signals where available. |
| Install behavior | Whether it runs install/postinstall scripts. |
| Runtime privilege | Browser, backend, build-only, test-only, or dev-only. |
| Removal plan | What first-party boundary wraps it so it can be replaced. |

No review record, no package.

## 6. npm Security Gate

Before adding an npm package:

1. Confirm the package is necessary.
2. Confirm the package name to avoid typosquatting.
3. Review the npm package page and linked repository.
4. Check maintainers, ownership changes, and publish history.
5. Check release recency and changelog quality.
6. Check direct and transitive dependency count.
7. Reject packages with unexpected `preinstall`, `install`, or `postinstall` scripts unless explicitly justified.
8. Check license compatibility.
9. Run `npm view <package> version dependencies peerDependencies optionalDependencies scripts repository license`.
10. Run `npm audit` after install.
11. Commit `package-lock.json`.
12. Use `npm ci` for reproducible installs once a lockfile exists.
13. Prefer exact pins for security-sensitive packages.
14. Do not use dependency URLs, GitHub tarballs, or unpublished sources without explicit approval.
15. Do not use `npm audit fix --force` blindly because it can introduce breaking upgrades.

Automated checks should fail for:

- Critical vulnerabilities.
- High vulnerabilities without written risk acceptance.
- Missing lockfile.
- Unexpected package manager lockfile drift.
- Non-HTTPS package resolution.
- Unapproved registry.
- Lifecycle scripts in unapproved packages.

## 7. Python Package Security Gate

Before adding a Python package:

1. Confirm the package is necessary.
2. Verify the package name to avoid typosquatting.
3. Review PyPI metadata and linked repository.
4. Check release recency, maintainer activity, and issue health.
5. Check license compatibility.
6. Check dependency tree.
7. Check for native extensions or build-time code execution.
8. Pin versions through the selected dependency management approach.
9. Generate or update the lockfile/constraints file once the implementation chooses the Python package manager.
10. Run vulnerability scanning using the selected enterprise-approved tool.
11. Prefer packages with clear changelogs and security advisories.

Reject packages that require arbitrary build steps unless the need is clear and reviewed.

## 8. Lockfile And Reproducibility Rules

Required:

- Lockfiles are committed.
- CI or local validation uses clean installs from lockfiles.
- Dependency updates are separate changes from feature work unless unavoidable.
- Lockfile diffs are reviewed.
- Package additions are reviewed more strictly than patch updates.

For npm:

- Use `package-lock.json`.
- Use `npm ci` for clean reproducible installs after lockfile creation.
- Review `resolved` and `integrity` fields.

For Python:

- Use the chosen lock or constraints mechanism consistently.
- Avoid unpinned production dependencies.
- Keep dev/test dependencies separate from runtime dependencies.

## 9. Transitive Dependency Review

Transitive dependencies can be the actual risk. For each new direct dependency, review:

- Number of transitive packages.
- Packages with install scripts.
- Packages with native binaries.
- Packages maintained by unknown or inactive owners.
- Packages with recent ownership transfer.
- Packages with broad filesystem/network behavior.
- Packages with known malware/advisory history.
- Packages that duplicate platform features.

High transitive dependency count is a reason to reject a dependency even when the direct package appears clean.

## 10. Provenance, Publishing, And Maintainer Signals

When consuming packages, prefer projects that show stronger supply-chain posture:

- Provenance attestations where available.
- Trusted publishing or equivalent OIDC-based publishing.
- Signed releases where available.
- Two-factor authentication expectations for maintainers.
- Active security policy.
- Clear vulnerability disclosure process.
- OpenSSF Scorecard results when available.
- SLSA provenance or build integrity posture where available.

When this project publishes any internal package in the future:

- Prefer trusted publishing/OIDC over long-lived tokens.
- Do not store long-lived registry publish tokens in repositories or local docs.
- Generate provenance if supported by the publishing flow.
- Restrict publish rights.
- Require review for release workflows.

## 11. Runtime And Build Isolation

Package risk depends on where the code runs.

| Scope | Risk treatment |
|---|---|
| Browser runtime | Avoid unless essential; all users load it. |
| Backend runtime | Strict review; may access data, filesystem, network, secrets. |
| Build-time | Strict review; can tamper with artifacts. |
| Test-only | Still reviewed; may run in developer/CI environments. |
| Dev-only | Still reviewed; supply-chain attacks often target developer machines. |

Do not treat dev dependencies as harmless.

## 12. Update Policy

Dependency updates should be deliberate.

Recommended cadence:

- Security updates: review promptly, with critical/high issues prioritized.
- Routine patch updates: batch on a regular cadence.
- Minor/major updates: separate review, changelog read, focused testing.
- Emergency updates: document risk, mitigation, and rollback path.

Automated dependency tools can open pull requests, but humans still review:

- Package identity.
- Diff size.
- Changelog.
- Transitive dependency changes.
- New lifecycle scripts.
- New permissions or runtime behavior.
- Test results.

## 13. SBOM And Inventory

The implementation should maintain a dependency inventory. Before production hardening, generate an SBOM or equivalent package inventory for:

- Frontend npm dependencies.
- Backend Python dependencies.
- Runtime dependencies.
- Dev/test/build dependencies.

The inventory should support vulnerability response: identify affected package, version, location, and owning application area.

## 14. Red Flags

Reject or escalate packages with:

- Very recent creation for a mature problem.
- Name similar to a popular package.
- New maintainer or ownership transfer without clear explanation.
- Obfuscated code.
- Minified source as the only distributed artifact.
- Unexpected network calls.
- Unexpected filesystem access.
- Install scripts.
- Native binaries without clear need.
- Large dependency tree for simple functionality.
- Missing repository link.
- Missing license.
- Dormant project with open critical issues.
- Unexplained major version jumps.
- Security advisories without patched release.

## 15. Package Approval Template

Use this template before adding a dependency:

```text
Package:
Ecosystem:
Requested by:
Approved by:
Purpose:
Runtime scope:
Version:
Alternatives considered:
Why native/first-party code is not sufficient:
Direct dependency count:
Transitive dependency count:
Install scripts:
Native binaries:
License:
Vulnerability scan result:
Maintenance/release health:
Repository:
Security policy/advisory process:
Provenance/trusted publishing/signing signals:
OpenSSF Scorecard/SLSA signals:
Risk rating:
Mitigations:
Removal/replacement boundary:
Decision:
```

## 16. Minimum Acceptance Criteria

Package use is acceptable only when:

- The package is necessary.
- A review record exists.
- The version is pinned or controlled by an approved range policy.
- Lockfiles are updated and reviewed.
- Known critical/high vulnerabilities are absent or explicitly risk-accepted.
- License is acceptable.
- Transitive dependency risk is understood.
- Install scripts are absent or approved.
- The package is wrapped behind a first-party boundary where practical.

## 17. Primary References

- [npm audit documentation](https://docs.npmjs.com/auditing-package-dependencies-for-security-vulnerabilities/)
- [npm trusted publishing documentation](https://docs.npmjs.com/trusted-publishers/)
- [npm provenance documentation](https://docs.npmjs.com/generating-provenance-statements/)
- [OpenSSF Scorecard](https://scorecard.dev/)
- [SLSA framework](https://slsa.dev/)
- [SLSA dependency threats](https://slsa.dev/spec/v1.0/threats)
- [GitHub Dependabot security updates](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-security-updates)
- [GitHub dependency review](https://docs.github.com/code-security/supply-chain-security/understanding-your-software-supply-chain/about-dependency-review)
