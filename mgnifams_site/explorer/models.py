from django.db import models

class Mgnifam(models.Model):
    id = models.IntegerField(primary_key=True)
    family_size = models.IntegerField()
    protein_rep = models.IntegerField()
    rep_region = models.TextField()
    rep_length = models.IntegerField()
    plddt = models.FloatField()
    ptm = models.FloatField()
    converged = models.BooleanField()
    cif_file = models.TextField()
    seed_msa_file = models.TextField()
    msa_file = models.TextField()
    hmm_file = models.TextField()
    rf_file = models.TextField()
    biomes_file = models.TextField()
    domain_architecture_file = models.TextField()
    pred_secondary_structure_file = models.TextField(null=True)

    quality_rank = models.IntegerField(default=0)
    novelty_rank = models.IntegerField(default=0)

    cif_blob = models.BinaryField(null=True)
    seed_msa_blob = models.BinaryField(null=True)
    msa_blob = models.BinaryField(null=True)
    hmm_blob = models.BinaryField(null=True)
    rf_blob = models.BinaryField(null=True)
    biomes_blob = models.BinaryField(null=True)
    domain_architecture_blob = models.BinaryField(null=True)
    pred_secondary_structure_blob = models.BinaryField(null=True)
    
    def __str__(self):
        return f"Mgnifam ID: {self.id}"

    class Meta:
        db_table = 'mgnifam'

class MgnifamProteins(models.Model):
    id = models.AutoField(primary_key=True)
    mgnifam = models.ForeignKey(Mgnifam, on_delete=models.CASCADE)
    protein = models.IntegerField()
    region = models.TextField()

    def __str__(self):
        return f"MgnifamProteins ID: {self.id}"

    class Meta:
        db_table = 'mgnifam_proteins'

class MgnifamPfams(models.Model):
    id = models.AutoField(primary_key=True)
    mgnifam = models.ForeignKey(Mgnifam, on_delete=models.CASCADE)
    rank = models.IntegerField()
    pfam_id = models.CharField(max_length=8)
    pfam_hit = models.TextField()
    query_hmm_range = models.TextField()
    template_hmm_range = models.TextField()
    e_value = models.FloatField()

    def __str__(self):
        return f"MgnifamPfams ID: {self.id}"

    class Meta:
        db_table = 'mgnifam_pfams'

class MgnifamFolds(models.Model):
    id = models.AutoField(primary_key=True)
    mgnifam = models.ForeignKey(Mgnifam, on_delete=models.CASCADE)
    target_structure = models.TextField()
    aligned_length = models.IntegerField()
    query_start = models.IntegerField()
    query_end = models.IntegerField()
    target_start = models.IntegerField()
    target_end = models.IntegerField()
    e_value = models.FloatField()

    def __str__(self):
        return f"MgnifamFolds ID: {self.id}"

    class Meta:
        db_table = 'mgnifam_folds'
        