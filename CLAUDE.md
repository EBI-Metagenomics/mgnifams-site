# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**mgnifams-site** is a Django web application for exploring MGnifam (metagenomic protein families) data. It is part of the EBI Metagenomics infrastructure. The site allows browsing, searching, and visualizing protein family data including HMM profiles, multiple sequence alignments, structural predictions, and domain annotations.

## Commands

All Django management commands run from `mgnifams_site/`:

```bash
cd mgnifams_site

# Run development server
python manage.py runserver 8000

# Apply database migrations
python manage.py migrate

# Collect static files (required before deployment)
python manage.py collectstatic --noinput

# Run tests (SECRET_KEY must be set — it has no fallback value)
DJANGO_SECRET_KEY=test-secret-key python manage.py test
```

**Docker:**
```bash
docker build -f Dockerfile -t mgnifams_site:latest .
docker run -p 8000:8000 mgnifams_site:latest
```

**Environment variables required for production:**
- `DJANGO_SECRET_KEY` — Django secret key
- `ALLOWED_HOST` — Allowed host (e.g., `mgnifams-demo.mgnify.org`)

## Architecture

### Django App Structure

The project has a single Django app (`explorer`) inside `mgnifams_site/`:

```
mgnifams_site/
├── mgnifams_site/       # Project config (settings.py, root urls.py)
└── explorer/            # Main app
    ├── models.py        # All database models
    ├── views.py         # All view logic (~300 LOC)
    ├── urls.py          # App URL patterns
    ├── templates/       # Jinja-style Django templates
    └── static/          # JS, CSS, HMM/MSA viewer libraries
```

### Database

- **SQLite** at `mgnifams_site/dbs/mgnifams.sqlite3`
- The database is **pre-populated** with MGnifam data — not generated dynamically
- In production (Kubernetes), the DB is mounted from a 300Gi NFS volume at `/ifs/public/services/metagenomics/mgnifams/dbs`

**Key models in `explorer/models.py`:**
- `Mgnifam` — Core family record: size, representative protein, AlphaFold scores (pLDDT, pTM), secondary structure percentages, transmembrane/signal peptide info, and binary blobs (seed MSA, HMM, RF, CIF structure, biome data)
- `MgnifamPfams` — Pfam domain hits (via HMMsearch) with E-values and alignment positions
- `MgnifamFunfams` — CATH FunFam hits with E-values and alignment positions
- `MgnifamFolds` — Structural fold matches (AlphaFold/PDB)
- `MgnifamModelPfams` — Structure model-predicted Pfam domains with probabilities

### URL Routing

| URL | View | Purpose |
|-----|------|---------|
| `/` | `index` | Homepage with family count and search |
| `/mgnifams_list/` | `mgnifams_list` | Browse/filter all families |
| `/details/<mgyf_id>/` | `details` | Full detail page for one family |
| `/serve_blob/<pk>/<column>/` | `serve_blob_as_file` | Download binary data (HMM, MSA, etc.) |

### ID Conversion

MGnifam IDs are stored as integers internally but displayed as formatted strings (e.g., `MGYF00000001`). Helper functions in `views.py` handle conversion between these formats.

### External API Integrations

- **Skylign** (skylign.org) — Generates HMM logo visualizations; the `details` view POSTs HMM data to Skylign and receives a UUID for embedding
- **AlphaFold EBI** — Links for structure visualization
- **PDBe** — Links to PDB structure entries
- **CATH DB** (cathdb.info) — Links to FunFam classification

### Frontend

- Plain HTML templates with vanilla JavaScript
- Uses the **VF (Visual Framework) Design System** components from EBI
- `static/explorer/js/details.js` — Handles the details page (MSA viewer, structure viewer, topology diagram)
- `static/explorer/js/all_mgnifams.js` — Handles family listing and filtering
- `static/explorer/hmm/` — HMM logo viewer library
- `static/explorer/msa/` — Multiple sequence alignment viewer library

### Deployment

- **Production:** Kubernetes at EBI (`deployment/ebi-wp-k8s-hl.yaml`), namespace `mgnifams-hl-exp`
- **CI/CD:** Pushing to `main` branch triggers an auto-build on Quay.io (`quay.io/microbiome-informatics/mgnifams_site:ebi-wp-k8s-hl`)
- **Rolling restart after image update:** `kubectl rollout restart deployment mgnifams-hl-exp -n mgnifams-hl-exp`
- The container runs as non-root uid 7123, gid 1347
