from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('explorer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mgnifam',
            name='has_pfam',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='mgnifam',
            name='has_funfam',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='mgnifam',
            name='has_model_pfam',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='mgnifam',
            name='has_structure',
            field=models.BooleanField(default=False),
        ),
        migrations.AddIndex(
            model_name='mgnifam',
            index=models.Index(fields=['has_pfam'], name='idx_mgnifam_has_pfam'),
        ),
        migrations.AddIndex(
            model_name='mgnifam',
            index=models.Index(fields=['has_funfam'], name='idx_mgnifam_has_funfam'),
        ),
        migrations.AddIndex(
            model_name='mgnifam',
            index=models.Index(fields=['has_model_pfam'], name='idx_mgnifam_has_model_pfam'),
        ),
        migrations.AddIndex(
            model_name='mgnifam',
            index=models.Index(fields=['has_structure'], name='idx_mgnifam_has_structure'),
        ),
    ]
