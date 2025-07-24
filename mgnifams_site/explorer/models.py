from django.db import models

class Mgnifam(models.Model):
    id = models.IntegerField(primary_key=True)
    full_size = models.IntegerField()
    protein_rep = models.IntegerField()
    rep_region = models.TextField()
    rep_length = models.IntegerField()
    converged = models.BooleanField()
    plddt = models.FloatField()
    ptm = models.FloatField()
    helix_percent = models.FloatField()
    strand_percent = models.FloatField()
    coil_percent = models.FloatField()
    rep_sequence = models.TextField()
    consensus = models.TextField()

    seed_msa_blob = models.BinaryField(null=True, default=None)
    hmm_blob = models.BinaryField(null=True, default=None)
    rf_blob = models.BinaryField(null=True, default=None)
    cif_blob = models.BinaryField(null=True, default=None)
    biome_blob = models.BinaryField(null=True, default=None)
    domain_blob = models.BinaryField(null=True, default=None)
    s4pred_blob = models.BinaryField(null=True, default=None)

    def __str__(self):
        return f"Mgnifam ID: {self.id}"

    class Meta:
        db_table = 'mgnifam'


class MgnifamFunfams(models.Model):
    id = models.AutoField(primary_key=True)
    mgnifam = models.ForeignKey(Mgnifam, on_delete=models.CASCADE)
    funfam = models.TextField()
    e_value = models.FloatField()
    score = models.FloatField()
    hmm_from = models.IntegerField()
    hmm_to = models.IntegerField()
    ali_from = models.IntegerField()
    ali_to = models.IntegerField()
    env_from = models.IntegerField()
    env_to = models.IntegerField()
    acc = models.FloatField()

    def __str__(self):
        return f"MgnifamFunfams ID: {self.id}"

    class Meta:
        db_table = 'mgnifam_funfams'


class MgnifamFolds(models.Model):
    id = models.AutoField(primary_key=True)
    mgnifam = models.ForeignKey(Mgnifam, on_delete=models.CASCADE)
    fold = models.TextField()
    aligned_length = models.IntegerField()
    q_start = models.IntegerField()
    q_end = models.IntegerField()
    t_start = models.IntegerField()
    t_end = models.IntegerField()
    e_value = models.FloatField()

    def __str__(self):
        return f"MgnifamFolds ID: {self.id}"

    class Meta:
        db_table = 'mgnifam_folds'


class MgnifamPfams(models.Model):
    id = models.AutoField(primary_key=True)
    mgnifam = models.ForeignKey(Mgnifam, on_delete=models.CASCADE)
    pfam = models.CharField(max_length=16)
    name = models.TextField()
    description = models.TextField()
    prob = models.FloatField()
    e_value = models.FloatField()
    length = models.IntegerField()
    query_hmm = models.TextField()
    template_hmm = models.TextField()

    def __str__(self):
        return f"MgnifamPfams ID: {self.id}"

    class Meta:
        db_table = 'mgnifam_pfams'
