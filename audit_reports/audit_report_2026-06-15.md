# Dependency Audit Report - 2026-06-15

## Summary

| Category | Found | Resolved |
|----------|-------|----------|
| Security vulnerabilities | 6 advisories across 2 packages | 6 |
| Outdated packages | 6 | 6 |
| Dependency conflicts | 0 | 0 |
| Tests | 91 total | 91 passed / 0 failed |

## Security Vulnerabilities

| Package | Before | After | ID | Description |
|---------|--------|-------|----|-------------|
| django | 6.0.5 | 6.0.6 | PYSEC-2026-197 | No summary provided by `uv audit`; fixed in 6.0.6. |
| django | 6.0.5 | 6.0.6 | PYSEC-2026-198 | No summary provided by `uv audit`; fixed in 6.0.6. |
| django | 6.0.5 | 6.0.6 | PYSEC-2026-199 | No summary provided by `uv audit`; fixed in 6.0.6. |
| django | 6.0.5 | 6.0.6 | PYSEC-2026-200 | No summary provided by `uv audit`; fixed in 6.0.6. |
| django | 6.0.5 | 6.0.6 | PYSEC-2026-201 | No summary provided by `uv audit`; fixed in 6.0.6. |
| idna | 3.14 | 3.18 | GHSA-65pc-fj4g-8rjx | Specially crafted inputs to `idna.encode()` can bypass the CVE-2024-3651 fix; fixed in 3.15 and updated to latest 3.18. |

Post-update `uv audit --preview-features audit` result: no known vulnerabilities and no adverse project statuses in 14 packages.

## Package Updates

| Package | Before | After | Notes |
|---------|--------|-------|-------|
| certifi | 2026.4.22 | 2026.5.20 | Transitive Requests dependency; latest version. |
| django | 6.0.5 | 6.0.6 | Direct runtime dependency; security fix. |
| idna | 3.14 | 3.18 | Transitive Requests dependency; security fix and latest version. |
| prek | 0.3.13 | 0.4.4 | Dev dependency; latest version in `uv.lock`. |
| requests | 2.34.0 | 2.34.2 | Direct runtime dependency; latest version. |
| ruff | 0.15.12 | 0.15.17 | Dev dependency; latest version in `uv.lock`. |

Post-update `uv pip list --outdated --format json` result: `[]`.

## Dependency Conflicts

| Package | Pinned To | Blocked By | Notes |
|---------|-----------|------------|-------|
| None | N/A | N/A | The resolver found latest compatible versions without conflicts. |

## Test Results

**Status**: PASS

<details>
<summary>Test output</summary>

```text
Creating test database for alias 'default'...
.......................Skylign error: err
..Skylign request timed out
....................Skylign logo fetch error: 
..............................................
----------------------------------------------------------------------
Ran 91 tests in 0.342s

OK
Destroying test database for alias 'default'...
Found 91 test(s).
System check identified no issues (0 silenced).
```

</details>

## Verification Commands

```bash
UV_CACHE_DIR=/tmp/uv-cache uv lock --check
UV_CACHE_DIR=/tmp/uv-cache uv audit --preview-features audit
UV_CACHE_DIR=/tmp/uv-cache uv pip list --outdated --format json
DJANGO_SECRET_KEY=test-secret-key UV_CACHE_DIR=/tmp/uv-cache uv run python manage.py test -v 1
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check mgnifams_site
UV_CACHE_DIR=/tmp/uv-cache uv run ruff format --check mgnifams_site
```

## Remaining Issues

No known vulnerabilities, outdated packages, dependency conflicts, or test failures remain.
