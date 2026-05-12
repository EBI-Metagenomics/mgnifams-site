# mgnifams-site

## Dev setup

Requires **Python 3.12+**.

```bash
uv python install 3.12
uv sync
cd mgnifams_site
uv run python manage.py migrate
DJANGO_SECRET_KEY=any-local-secret uv run python manage.py collectstatic --noinput
DJANGO_SECRET_KEY=any-local-secret uv run python manage.py runserver 8000
```

## Testing and checks

Run the full backend test suite:

```bash
cd mgnifams_site
DJANGO_SECRET_KEY=test-secret-key uv run python manage.py test
```

Run frontend JavaScript tests from the repository root:

```bash
node tests/test_details_translate_to_msa_pos.js
```

Run dependency and quality checks from the repository root:

```bash
uv lock --check
uv sync --frozen
uv audit
uv run ruff check mgnifams_site
uv run ruff format --check mgnifams_site
uv run prek run --all-files --show-diff-on-failure
```

Build the Docker image:

```bash
docker build -f Dockerfile -t mgnifams_site:latest .
```

Prepare a release version bump:

```bash
uv version 2.2.0
uv lock --check
```

# Deployment to EBI WebProd Kubernetes
Pre-requisites:
* Permission to push to a docker registry. We currently use a [team quay.io](quay.io/microbiome-informatics).
* A kubeconfig that allows you to manage the EBI WebProd K8s cluster (e.g. in `~/mgnify-k8s-team-admin-hh.conf` below)

**Normal usage**: Push to the `main` branch, and Quay.io will automatically build and tag the `:latest` container.
Wait a few minutes for the build, and then restart the deployment to pull the image again:
```shell
 kubectl --kubeconfig ~/mgnify-k8s-team-admin-hh.conf rollout restart deployment mgnifams-site -n mgnifams-hl-exp
```

**Non-normal usage**:
Secrets setup (one-time):
- Make a secrets .env file at `k8s-hl/secrets.env` with the database connection config (env vars read by `settings.py`) and the `DJANGO_SECRET_KEY`.
	- Push it with e.g.: `kubectl --kubeconfig ~/mgnify-k8s-team-admin-hh.conf --namespace mgnifams-hl-exp create secret generic mgnifams-secret --from-env-file=deployment/secrets.env`
- Get authentication credentials for quay.io (the built image is private). You can get a Kubernetes secrets yaml file from your Quay.io user settings, in the "CLI Password" section.
	- Download the secrets yaml and name the secret `name: quay-pull-secret` in the metadata section. Put this into the `k8s-hl` folder as `secrets-quayio.yml`.

To redeploy with a manual build, or having changed the kubernetes config:
```shell
docker build -f Dockerfile -t quay.io/microbiome-informatics/mgnifams_site:ebi-wp-k8s-hl --load .
docker push quay.io/microbiome-informatics/mgnifams_site:ebi-wp-k8s-hl
kubectl --kubeconfig ~/mgnify-k8s-team-admin-hh.conf apply -f deployment/ebi-wp-k8s-hl.yaml
```
