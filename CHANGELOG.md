# Changelog

## [Unreleased] - 2026-03-17

### Added
- `CLAUDE.md` — developer guide covering build commands, architecture, and deployment
- `explorer/tests.py` — initial test suite (21 tests) covering views, ID conversion, blob decoding, and security
- `pyproject.toml` — Ruff configuration (linting rules E, F, I, UP; single-quote formatter; migrations excluded from line-length)
- `.pre-commit-config.yaml` — pre-commit hooks running `ruff` (lint + auto-fix) and `ruff-format` on every commit
- `ruff==0.9.10` added to `requirements.txt`

### Performance

**`DEBUG` now reads from environment variable** (`settings.py`, `CLAUDE.md`)
`DEBUG = True` was hardcoded, causing Django to accumulate every SQL query in memory and disable template caching in all environments. Changed to `DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'`. Defaults to `True` so local development is unaffected; production must set `DJANGO_DEBUG=False`. Updated `CLAUDE.md` dev server command and production env vars list accordingly. *(M1)*

**Configured explicit file-based cache backend** (`settings.py`)
Django was previously using the implicit `LocMemCache` default (in-process, lost on every gunicorn worker restart). Added an explicit `FileBasedCache` configuration that persists to disk across restarts. The cache directory defaults to `/tmp/mgnifams_cache` and can be overridden with the `DJANGO_CACHE_DIR` environment variable. *(H4)*

**Cache Skylign logo JSON per family to avoid blocking HTTP calls on every page load** (`views.py`)
The `details` view previously made two sequential blocking HTTP calls to `skylign.org` (POST + GET, up to 10 s worst-case) on every visit. Results are now cached in Django's cache backend under the key `skylign_logo_json_<id>` for 1 week. On a cache hit the external calls are skipped entirely. Failed fetches (`None`) are deliberately not cached so that the next request retries. *(H1)*

**Avoid loading blob columns where they are not needed** (`views.py`)

- `mgnifams_list` view: now just renders the template — data is fetched by DataTables via the new `mgnifams_data` AJAX endpoint. *(C2)*
- `mgnifams_data` endpoint (`GET /mgnifams_data/`): new JSON view supporting DataTables server-side mode. Accepts `draw`, `start`, `length`, `order[0][column]`, `order[0][dir]`, `search[value]`, and range-filter params for all 10 numeric columns. Issues a single `SELECT … LIMIT … OFFSET` query instead of loading the whole table. *(C2)*
- `all_mgnifams.js`: switched DataTables to `serverSide: true`; filter inputs are forwarded as extra AJAX params so the server applies them via ORM range lookups. *(C2)*
- `mgnifams_list` view (previously): replaced `Mgnifam.objects.all()` with `.only()` listing the 12 scalar columns actually rendered in the table. All 8 binary blob fields are now excluded from the list-page query. *(C1)*
- `serve_blob_as_file` view: replaced `get_object_or_404(Mgnifam, pk=pk)` with `Mgnifam.objects.only(column_name)` so each of the 6+ per-page blob-serve requests loads only the single requested column instead of the full row. *(H2)*
- `index` view: replaced `Mgnifam.objects.first()` (which loaded all columns including all 8 blobs) with `Mgnifam.objects.only('id').first()`. *(H3)*
- `details` view: `biome_blob`, `domain_blob`, and `s4pred_blob` are now deferred from the main `Mgnifam` query and no longer decoded or passed to the template context, since the browser fetches them lazily via `/serve_blob/` endpoints. `tm_blob` is no longer decoded to a full string — its presence is communicated to the template as a boolean. *(H5)*

### Fixed

**Bug: `serve_blob_as_file` returned empty 200 for NULL blobs** (`views.py`)
When a blob column is `NULL` in the database, the view was returning `HttpResponse(None)` — an empty 200 response. Browser JS calling `response.json()` on the empty body raised `SyntaxError: Unexpected end of JSON input`. Now raises `Http404` instead, which the JS `response.ok` check handles gracefully.

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
