# Changelog

## [Unreleased] - 2026-03-16

### Added
- `CLAUDE.md` — developer guide covering build commands, architecture, and deployment
- `explorer/tests.py` — initial test suite (21 tests) covering views, ID conversion, blob decoding, and security

### Fixed

**Bug: unconditional `.decode()` on nullable blob fields** (`views.py`)
`cif_blob`, `seed_msa_blob`, `rf_blob`, `hmm_blob`, `biome_blob`, `domain_blob`, and `s4pred_blob` were all decoded without a `None` guard, causing `AttributeError` crashes for families with missing blobs. Replaced with a `decode_blob()` helper that handles `None`, `bytes`, `memoryview`, and `str` (the real DB stores blobs as plain strings, having been populated outside the Django ORM).

**Bug: dead `except Mgnifam.DoesNotExist` block** (`views.py`)
`get_object_or_404` raises `Http404`, not `DoesNotExist`, so the error handler and redirect in `details()` were unreachable. Removed the try/except.

**Bug: duplicate `t_end` key drops `t_start` from structural annotations** (`views.py`)
A copy-paste error meant the fold annotation dict contained `t_end` twice and `t_start` never. Fixed to include `t_start`.

**Bug: arbitrary attribute access in `serve_blob_as_file`** (`views.py`)
The `column_name` URL parameter was passed directly to `getattr()` with no validation, allowing any model attribute to be downloaded. Added a `BLOB_COLUMNS` allowlist; anything outside it returns 404.

**Bug: all-zeros MGYF ID crashed with `ValueError`** (`views.py`)
`MGYF0000000000` stripped to an empty string by the regex, causing `int("")` to raise `ValueError`. Changed the regex from `MGYF0+` to `MGYF0*` and handled the empty-string case as ID 0, deferring 404 to the database lookup.

**Bug: `fetch_skylign_logo_json` had no timeout or error handling** (`views.py`)
Unlike the first Skylign call, the logo-fetch GET request had no timeout, meaning a slow response would hang the entire page load. Added `timeout=5` and a `try/except RequestException`.

**Bug: `converged` BooleanField compared to string `"True"`** (`views.py`)
`converged = (mgnifam.converged == "True")` always evaluated to `False` because Django returns an actual `bool` from a `BooleanField`. Replaced with `converged = mgnifam.converged`.

---

## Earlier history

See git log for changes prior to this session.
