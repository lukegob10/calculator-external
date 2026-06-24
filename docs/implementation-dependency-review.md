# Implementation Dependency Review

This records the packages introduced for the initial implementation. It follows the package gate in [package-security-review.md](package-security-review.md).

## npm

### `typescript==5.5.4`

- Purpose: Compile and type-check the plain TypeScript frontend.
- Runtime scope: Development/build only.
- Native/first-party alternative: None practical; TypeScript compiler is the selected language toolchain.
- Install scripts: None expected.
- Transitive dependency posture: Low; TypeScript is a direct compiler dependency.
- Decision: Approved for initial implementation.

## Python

### `fastapi==0.115.14`

- Purpose: Backend API framework with typed request/response contracts and OpenAPI documentation.
- Runtime scope: Backend runtime.
- Native/first-party alternative: Python standard library HTTP server is not appropriate for this API surface.
- Decision: Approved.

### `uvicorn[standard]==0.35.0`

- Purpose: Local ASGI server for FastAPI.
- Runtime scope: Backend runtime/local development.
- Decision: Approved.

### `SQLAlchemy==2.0.41`

- Purpose: Repository/persistence layer for local SQLite now and Oracle adapter path later.
- Runtime scope: Backend runtime.
- Decision: Approved.

### `pydantic==2.11.7`

- Purpose: Explicit request/response validation and schema modeling.
- Runtime scope: Backend runtime.
- Decision: Approved.

### `pytest==8.4.1`

- Purpose: Backend test runner.
- Runtime scope: Development/test only.
- Decision: Approved.

### `httpx==0.28.1`

- Purpose: Required by FastAPI TestClient-based tests.
- Runtime scope: Development/test only.
- Decision: Approved.

## Security Notes

- The frontend uses no application framework and no client-side data library.
- Password hashing currently uses Python standard library PBKDF2-HMAC to avoid adding a password hashing package before enterprise package review. Production should revisit Argon2id or bcrypt with a reviewed dependency.
- Lockfiles should be reviewed when generated or updated.
