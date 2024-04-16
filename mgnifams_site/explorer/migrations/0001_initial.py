# Generated by Django 4.2.3 on 2024-04-16 09:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Mgnifam",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("family_size", models.IntegerField()),
                ("protein_rep", models.IntegerField()),
                ("rep_region", models.TextField()),
                ("converged", models.BooleanField()),
                ("cif_file", models.TextField()),
                ("seed_msa_file", models.TextField()),
                ("msa_file", models.TextField()),
                ("hmm_file", models.TextField()),
                ("biomes_file", models.TextField()),
                ("domain_architecture_file", models.TextField()),
            ],
            options={
                "db_table": "mgnifam",
            },
        ),
        migrations.CreateModel(
            name="MgnifamProteins",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("protein", models.IntegerField()),
                ("region", models.TextField()),
                (
                    "mgnifam_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="explorer.mgnifam",
                    ),
                ),
            ],
            options={
                "db_table": "mgnifam_proteins",
            },
        ),
        migrations.CreateModel(
            name="MgnifamPfams",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("rank", models.IntegerField()),
                ("pfam_id", models.CharField(max_length=8)),
                ("pfam_hit", models.TextField()),
                ("query_hmm_range", models.TextField()),
                ("template_hmm_range", models.TextField()),
                ("e_value", models.FloatField()),
                (
                    "mgnifam_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="explorer.mgnifam",
                    ),
                ),
            ],
            options={
                "db_table": "mgnifam_pfams",
            },
        ),
        migrations.CreateModel(
            name="MgnifamFolds",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("target_structure", models.TextField()),
                ("aligned_length", models.IntegerField()),
                ("query_start", models.IntegerField()),
                ("query_end", models.IntegerField()),
                ("target_start", models.IntegerField()),
                ("target_end", models.IntegerField()),
                ("e_value", models.FloatField()),
                (
                    "mgnifam_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="explorer.mgnifam",
                    ),
                ),
            ],
            options={
                "db_table": "mgnifam_folds",
            },
        ),
    ]
