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

## bin scripts to produce data

extract_rf.py

Only used to produce earlier version rf files to link HMM to MSA. Now it is incorporated in the family generation pipeline.

### Biome distribution

1. python3 bin/get_biome_distribution.py bin/db_config.ini data/families/updated_refined_families.tsv tmp/ data/biome_sunburst/tmp/

Query the PostgreSQL proteins database for biome data relative to the sequences in each family

Arguments:

config_file: Path to the configuration file for the database secrets

edge_list_file: Path to the edge list file with two columns (family-sequence)

tmp_dir: Path to the tmp directory  (intermediate)

result_dir: Path to the result directory  (intermediate)

2. python3 bin/parse_biome_sunburst.py bin/db_config.ini data/biome_sunburst/tmp/ data/biome_sunburst/result/

Query the PostgreSQL proteins database for biome names and parse into the final sunburst format

config_file: Path to the configuration file for the database secrets

counts_dir: Path to the folder with biomes ids and counts per family

out_dir: Path to the results directory (final)

### Domain architecture

1. python3 bin/get_pfams.py bin/db_config.ini data/families/updated_refined_families.tsv data/pfams/tmp

Query the PostgreSQL proteins database for for each family to get the pfam domains for all of its underlying sequences

config_file: Path to the configuration file for the database secrets

edge_list_file: Path to the edge list file with two columns (family-sequence)

result_dir: Path to the result directory  (intermediate)

2. python3 bin/parse_pfams.py data/families/updated_refined_families.tsv data/pfams/tmp/ data/pfams/result/

Parse pfam ids into domain architecture format

edge_list_file: Path to the edge list file with two columns  (family-sequence)

read_dir: Path to the folder with pfam ids per family and sequence

out_dir: Path to the results directory  (intermediate)

3. python3 bin/translate_pfams.py bin/db_config.ini data/pfams/result/ data/pfams/translated/

Query a PostgreSQL database and translate pfam ids into clickable names

config_file: Path to the configuration file for the database secrets

read_dir: Path to the folder with the domain architecture json files

out_dir: Path to the translated results directory (final)
