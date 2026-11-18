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
    inside_percent = models.FloatField()
    membrane_alpha_percent = models.FloatField()
    outside_percent = models.FloatField()
    signal_percent = models.FloatField()
    membrane_beta_percent = models.FloatField()
    periplasm_percent = models.FloatField()
    has_pfam = models.BooleanField(default=False)
    has_funfam = models.BooleanField(default=False)
    has_model_pfam = models.BooleanField(default=False)
    has_structure = models.BooleanField(default=False)
    rep_sequence = models.TextField()
    consensus = models.TextField()

    seed_msa_blob = models.BinaryField(null=True, default=None)
    hmm_blob = models.BinaryField(null=True, default=None)
    rf_blob = models.BinaryField(null=True, default=None)
    cif_blob = models.BinaryField(null=True, default=None)
    biome_blob = models.BinaryField(null=True, default=None)
    domain_blob = models.BinaryField(null=True, default=None)
    s4pred_blob = models.BinaryField(null=True, default=None)
    tm_blob = models.BinaryField(null=True, default=None)

    # Provenance from the release's families.tsv.gz; NULL in DBs built before it was loaded.
    status = models.TextField(null=True, default=None)
    not_updated_reason = models.TextField(null=True, default=None)
    first_release = models.TextField(null=True, default=None)
    model_release = models.TextField(null=True, default=None)
    model_proteins_release = models.TextField(null=True, default=None)
    members_release = models.TextField(null=True, default=None)
    members_proteins_release = models.TextField(null=True, default=None)

    def __str__(self):
        return f'Mgnifam ID: {self.id}'

    class Meta:
        db_table = 'mgnifam'
        indexes = [
            models.Index(fields=['full_size'], name='idx_mgnifam_full_size'),
            models.Index(fields=['rep_length'], name='idx_mgnifam_rep_length'),
            models.Index(fields=['plddt'], name='idx_mgnifam_plddt'),
            models.Index(fields=['ptm'], name='idx_mgnifam_ptm'),
            models.Index(fields=['helix_percent'], name='idx_mgnifam_helix'),
            models.Index(fields=['strand_percent'], name='idx_mgnifam_strand'),
            models.Index(fields=['coil_percent'], name='idx_mgnifam_coil'),
            models.Index(fields=['inside_percent'], name='idx_mgnifam_inside'),
            models.Index(fields=['membrane_alpha_percent'], name='idx_mgnifam_membrane_alpha'),
            models.Index(fields=['outside_percent'], name='idx_mgnifam_outside'),
            models.Index(fields=['signal_percent'], name='idx_mgnifam_signal'),
            models.Index(fields=['membrane_beta_percent'], name='idx_mgnifam_membrane_beta'),
            models.Index(fields=['periplasm_percent'], name='idx_mgnifam_periplasm'),
            models.Index(fields=['has_pfam'], name='idx_mgnifam_has_pfam'),
            models.Index(fields=['has_funfam'], name='idx_mgnifam_has_funfam'),
            models.Index(fields=['has_model_pfam'], name='idx_mgnifam_has_model_pfam'),
            models.Index(fields=['has_structure'], name='idx_mgnifam_has_structure'),
        ]


class MgnifamPfams(models.Model):
    id = models.AutoField(primary_key=True)
    mgnifam = models.ForeignKey(Mgnifam, on_delete=models.CASCADE, related_name='pfams')
    pfam = models.TextField()
    name = models.TextField()
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
        return f'MgnifamPfams ID: {self.id}'

    class Meta:
        db_table = 'mgnifam_pfams'


class MgnifamFunfams(models.Model):
    id = models.AutoField(primary_key=True)
    mgnifam = models.ForeignKey(Mgnifam, on_delete=models.CASCADE, related_name='funfams')
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
        return f'MgnifamFunfams ID: {self.id}'

    class Meta:
        db_table = 'mgnifam_funfams'


class MgnifamFolds(models.Model):
    id = models.AutoField(primary_key=True)
    mgnifam = models.ForeignKey(Mgnifam, on_delete=models.CASCADE, related_name='folds')
    fold = models.TextField()
    aligned_length = models.IntegerField()
    q_start = models.IntegerField()
    q_end = models.IntegerField()
    t_start = models.IntegerField()
    t_end = models.IntegerField()
    e_value = models.FloatField()

    def __str__(self):
        return f'MgnifamFolds ID: {self.id}'

    class Meta:
        db_table = 'mgnifam_folds'


class MgnifamModelPfams(models.Model):
    id = models.AutoField(primary_key=True)
    mgnifam = models.ForeignKey(Mgnifam, on_delete=models.CASCADE, related_name='model_pfams')
    pfam = models.CharField(max_length=16)
    name = models.TextField()
    description = models.TextField()
    prob = models.FloatField()
    e_value = models.FloatField()
    length = models.IntegerField()
    query_hmm = models.TextField()
    template_hmm = models.TextField()

    def __str__(self):
        return f'MgnifamModelPfams ID: {self.id}'

    class Meta:
        db_table = 'mgnifam_model_pfams'


class ReleaseHistory(models.Model):
    release = models.TextField(primary_key=True)
    date = models.TextField()
    type = models.TextField()
    mgnify_proteins_release = models.TextField()
    pipeline_version = models.TextField(null=True)
    n_families = models.IntegerField(null=True)
    n_updated = models.IntegerField(null=True)
    n_not_updated = models.IntegerField(null=True)

    class Meta:
        db_table = 'release_history'


class ReleaseInfo(models.Model):
    # The release's FTP release_manifest.json flattened to dotted keys.
    pk = models.CompositePrimaryKey('release', 'key')
    release = models.ForeignKey(
        ReleaseHistory, on_delete=models.DO_NOTHING, db_column='release', to_field='release', related_name='info'
    )
    key = models.TextField()
    value = models.TextField(null=True)

    class Meta:
        db_table = 'release_info'


class MgnifamClan(models.Model):
    mgnifam = models.OneToOneField(
        Mgnifam, on_delete=models.DO_NOTHING, primary_key=True, db_column='mgnifam_id', related_name='clan'
    )
    clan_id = models.TextField()
    is_representative = models.BooleanField()

    class Meta:
        db_table = 'mgnifam_clans'


class MgnifamClanEdge(models.Model):
    pk = models.CompositePrimaryKey('family_1', 'family_2')
    family_1 = models.ForeignKey(Mgnifam, on_delete=models.DO_NOTHING, db_column='family_1', related_name='edges_as_1')
    family_2 = models.ForeignKey(Mgnifam, on_delete=models.DO_NOTHING, db_column='family_2', related_name='edges_as_2')
    shared_proteins = models.IntegerField(null=True)
    protein_jaccard = models.FloatField(null=True)
    residue_jaccard = models.FloatField(null=True)
    residue_containment = models.FloatField(null=True)

    class Meta:
        db_table = 'mgnifam_clan_edges'
