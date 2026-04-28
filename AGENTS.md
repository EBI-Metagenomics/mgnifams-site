# Repository Guidelines

## Project Structure & Module Organization

This is a Python 3.12+ Django application. The Django project lives in `mgnifams_site/mgnifams_site/`, and the main app is `mgnifams_site/explorer/`. Core app files include `models.py`, `views.py`, `urls.py`, `storage.py`, and `templatetags/custom_filters.py`. Templates are under `mgnifams_site/explorer/templates/`, static CSS and JavaScript under `mgnifams_site/explorer/static/`, and migrations under `mgnifams_site/explorer/migrations/`. Tests currently live in `mgnifams_site/explorer/tests.py`. Deployment assets are in `deployment/`, with container setup in `Dockerfile`.

## Build, Test, and Development Commands

Install dependencies from the repository root:

```bash
python -m pip install -r requirements.txt
```

Run Django commands from `mgnifams_site/`:

```bash
DJANGO_SECRET_KEY=local-secret python manage.py migrate
DJANGO_SECRET_KEY=local-secret python manage.py collectstatic --noinput
DJANGO_SECRET_KEY=local-secret DJANGO_DEBUG=True python manage.py runserver 8000
DJANGO_SECRET_KEY=test-secret-key python manage.py test
```

Quality checks from the repository root:

```bash
ruff check mgnifams_site
ruff check --fix mgnifams_site
ruff format mgnifams_site
pre-commit run --all-files
```

Build the container with `docker build -f Dockerfile -t mgnifams_site:latest .`.

## Coding Style & Naming Conventions

Use Ruff for linting and formatting. The configured line length is 120, formatter quote style is single quotes, and linting enables `E`, `F`, `I`, and `UP` rules. Keep Django code idiomatic: model classes in `PascalCase`, functions and view helpers in `snake_case`, and tests named `test_*`. Avoid unrelated rewrites in generated migrations.

## Testing Guidelines

Use Django `TestCase` tests in `explorer/tests.py` or split into `test_*.py` files if the suite grows. Add focused tests for new views, URL behavior, model helpers, template context, and external API failure paths. CI runs `pre-commit run --all-files` and `python manage.py test` on pull requests and pushes to `main`.

## Commit & Pull Request Guidelines

Recent commits use short, lowercase, imperative or descriptive summaries, for example `changelog updated` or `added ci.yml with 2 test`. Keep the first line concise and mention the user-facing change or infrastructure area. Pull requests should include a short description, linked issue or ticket when relevant, test evidence, and screenshots for template or static asset changes.

## Security & Configuration Tips

Do not commit secrets or production database files. `DJANGO_SECRET_KEY` is required, `DJANGO_DEBUG` should be false in production, and `ALLOWED_HOST` must be set for deployed hosts. Treat Kubernetes credentials, registry tokens, and `deployment/secrets.env` as local-only material.
