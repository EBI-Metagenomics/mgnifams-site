# mgnifams-site

## Dev setup
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
python manage.py runserver 8000
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
- Make a secrets .env file at `k8s-hl/secrets.env` with the database connection config (env vars read by `settings.py) and the `DJANGO_SECRET_KEY`.
	- Push it with e.g.: `kubectl --kubeconfig ~/mgnify-k8s-team-admin-hh.conf --namespace mgnifams-hl-exp create secret generic mgnifams-secret --from-env-file=deployment/secrets.env`
- Get authentication credentials for quay.io (the built image is private). You can get a Kubernetes secrets yaml file from your Quay.io user settings, in the "CLI Password" section.
	- Download the secrets yaml and name the secret `name: quay-pull-secret` in the metadata section. Put this into the `k8s-hl` folder as `secrets-quayio.yml`.

To redeploy with a manual build, or having changed the kubernetes config:
```shell
docker build -f Dockerfile -t quay.io/microbiome-informatics/mgnifams_site:ebi-wp-k8s-hl --load .
docker push quay.io/microbiome-informatics/mgnifams_site:ebi-wp-k8s-hl
kubectl --kubeconfig ~/mgnify-k8s-team-admin-hh.conf apply -f deployment/ebi-wp-k8s-hl.yaml
```
