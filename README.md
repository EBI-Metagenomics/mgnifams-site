# mgnifams-site

## Dev setup
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
python manage.py runserver 8000
```

## Demo deployment (Kubernetes)
There is a basic Kubernetes configuration for deploying this to EBI's Web Production K8s clusters:

A quay.io "pull secret" is required (as a K8s secret YAML), along with a K8s cluster admin configuration.

With those in place:

```bash
docker build -f Dockerfile -t quay.io/microbiome-informatics/mgnifams_site:ebi-wp-k8s-hl --load .
docker push quay.io/microbiome-informatics/mgnifams_site:ebi-wp-k8s-hl
kubectl apply -f deployment/ebi-wp-k8s-hl.yaml
```
