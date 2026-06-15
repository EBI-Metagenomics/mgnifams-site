# Repository Guidelines

## Project Snapshot

`mgnifams-site` is a Python 3.12 Django app for browsing MGnifam protein family data. The Django project is in `mgnifams_site/mgnifams_site/`, and the main app is `mgnifams_site/explorer/`.

Important paths:
- App code: `mgnifams_site/explorer/`
- Templates: `mgnifams_site/explorer/templates/`
- Static assets: `mgnifams_site/explorer/static/`
- Tests: `mgnifams_site/explorer/tests.py`
- Deployment assets: `deployment/`
- Container config: `Dockerfile`

## Dependencies And Tooling

Use uv. Dependencies are declared in `pyproject.toml` and locked in `uv.lock`; do not reintroduce `requirements.txt`.

From the repository root:

```bash
uv python install 3.12
uv sync
```

Run prek hooks with:

```bash
uv run prek run --all-files --show-diff-on-failure
```

`.pre-commit-config.yaml` is intentionally kept for hook compatibility, but `prek` is the runner.

## Common Commands

Run Django commands from `mgnifams_site/`:

```bash
DJANGO_SECRET_KEY=local-secret uv run python manage.py migrate
DJANGO_SECRET_KEY=local-secret uv run python manage.py collectstatic --noinput
DJANGO_SECRET_KEY=local-secret DJANGO_DEBUG=True uv run python manage.py runserver 8000
DJANGO_SECRET_KEY=test-secret-key uv run python manage.py test
```

Run quality checks from the repository root:

```bash
uv lock --check
uv sync --frozen
uv audit
uv run ruff check mgnifams_site
uv run ruff format --check mgnifams_site
uv run prek run --all-files --show-diff-on-failure
```

Run frontend JavaScript tests from the repository root:

```bash
node tests/test_details_translate_to_msa_pos.js
```

Build the container with:

```bash
docker build -f Dockerfile -t mgnifams_site:latest .
```

Prepare a release version bump with:

```bash
uv version 2.2.0
uv lock --check
```

## Architecture Notes

- The project has one Django app, `explorer`.
- SQLite data lives under `mgnifams_site/dbs/`; the production database is mounted externally.
- MGnifam IDs are stored as integers and displayed as formatted strings such as `MGYF00000001`.
- External integrations include Skylign, AlphaFold EBI, PDBe, and CATH DB.
- Frontend code is plain Django templates plus vanilla JavaScript, using EBI Visual Framework assets.

## Coding Style

Use Ruff for linting and formatting. The configured line length is 120, formatter quote style is single quotes, and linting enables `E`, `F`, `I`, and `UP`.

Keep Django code idiomatic:
- Model classes use `PascalCase`.
- Functions, helpers, and tests use `snake_case`.
- Tests should be named `test_*`.
- Avoid unrelated rewrites in generated migrations.

## Testing Guidance

Use Django `TestCase` tests in `explorer/tests.py` or split into `test_*.py` files if the suite grows. Add focused tests for new views, URL behavior, model helpers, template context, and external API failure paths.

CI runs prek hooks and Django tests on pull requests and pushes to `main`.

## Security And Configuration

Do not commit secrets, production database files, Kubernetes credentials, registry tokens, or `deployment/secrets.env`.

Important environment variables:
- `DJANGO_SECRET_KEY` is required.
- `DJANGO_DEBUG` should be false in production.
- `ALLOWED_HOST` must be set for deployed hosts.
- `DJANGO_CACHE_DIR` controls the writable file cache path and defaults to `/tmp/mgnifams_cache`.

## Commit And PR Notes

Add a one-liner in `CHANGELOG.md` for every implemented task.
**NEVER** execute `git commit` commands; let the user handle those.
