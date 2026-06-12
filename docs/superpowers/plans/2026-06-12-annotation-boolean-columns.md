# Annotation Boolean Columns Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace four correlated `NOT EXISTS` subqueries in `mgnifams_data` with pre-computed indexed boolean columns on `mgnifam`, eliminating the query hang caused by 13M-row `mgnifam_folds` table scans.

**Architecture:** Add `has_pfam`, `has_funfam`, `has_model_pfam`, `has_structure` as `BooleanField(default=False)` to the `Mgnifam` model. A one-time SQLite script populates and indexes these on the production DB. The Django view replaces `Exists(…)` subquery filters with direct field lookups. A Django migration keeps the test DB in sync.

**Tech Stack:** Django ORM, SQLite, pytest/Django TestCase

---

## SQLite Scripts (run directly on production DB — do NOT wait for code changes)

These are standalone scripts the developer runs against the production (and test) DB before or after deploying the code changes. The code change is backward-compatible: the old `Exists()` path is replaced, but the new columns are read-only from Django's perspective.

### Script A — Add columns, populate, index (`add_annotation_columns.sql`)

Save this file and run:
```bash
sqlite3 /path/to/production/mgnifams.sqlite3 < add_annotation_columns.sql
```

```sql
BEGIN;

ALTER TABLE mgnifam ADD COLUMN has_pfam INTEGER NOT NULL DEFAULT 0;
ALTER TABLE mgnifam ADD COLUMN has_funfam INTEGER NOT NULL DEFAULT 0;
ALTER TABLE mgnifam ADD COLUMN has_model_pfam INTEGER NOT NULL DEFAULT 0;
ALTER TABLE mgnifam ADD COLUMN has_structure INTEGER NOT NULL DEFAULT 0;

UPDATE mgnifam
SET has_pfam = CASE WHEN EXISTS (
    SELECT 1 FROM mgnifam_pfams WHERE mgnifam_id = mgnifam.id
) THEN 1 ELSE 0 END;

UPDATE mgnifam
SET has_funfam = CASE WHEN EXISTS (
    SELECT 1 FROM mgnifam_funfams WHERE mgnifam_id = mgnifam.id
) THEN 1 ELSE 0 END;

UPDATE mgnifam
SET has_model_pfam = CASE WHEN EXISTS (
    SELECT 1 FROM mgnifam_model_pfams WHERE mgnifam_id = mgnifam.id
) THEN 1 ELSE 0 END;

UPDATE mgnifam
SET has_structure = CASE WHEN EXISTS (
    SELECT 1 FROM mgnifam_folds WHERE mgnifam_id = mgnifam.id
) THEN 1 ELSE 0 END;

CREATE INDEX IF NOT EXISTS idx_mgnifam_has_pfam       ON mgnifam(has_pfam);
CREATE INDEX IF NOT EXISTS idx_mgnifam_has_funfam     ON mgnifam(has_funfam);
CREATE INDEX IF NOT EXISTS idx_mgnifam_has_model_pfam ON mgnifam(has_model_pfam);
CREATE INDEX IF NOT EXISTS idx_mgnifam_has_structure  ON mgnifam(has_structure);

COMMIT;
```

> Note: The `has_structure` UPDATE checks 35K rows against the 13M-row `mgnifam_folds` (index-assisted). Expect it to take 1–5 minutes on the production DB. Run in a screen/tmux session.

### Script B — Verify population

```sql
SELECT
    SUM(has_pfam)       AS families_with_pfam,
    SUM(has_funfam)     AS families_with_funfam,
    SUM(has_model_pfam) AS families_with_model_pfam,
    SUM(has_structure)  AS families_with_structure,
    COUNT(*)            AS total_families
FROM mgnifam;

-- Cross-check has_structure against actual folds table
SELECT COUNT(DISTINCT mgnifam_id) AS folds_families FROM mgnifam_folds;
-- Should equal families_with_structure above.
```

### Script C — Verify query plan after migration

```sql
EXPLAIN QUERY PLAN
SELECT id FROM mgnifam
WHERE full_size >= 100
  AND rep_length >= 150
  AND plddt >= 70
  AND strand_percent >= 10
  AND has_pfam = 0
  AND has_funfam = 0
  AND has_model_pfam = 0
  AND has_structure = 0
ORDER BY id;
```

Expected output — no `CORRELATED SCALAR SUBQUERY`, no `SCAN` on annotation tables:
```
QUERY PLAN
|--SEARCH mgnifam USING INDEX idx_mgnifam_has_structure (has_structure=?)
```

---

## File Map

| File | Change |
|---|---|
| `mgnifams_site/explorer/models.py` | Add 4 `BooleanField` fields to `Mgnifam` |
| `mgnifams_site/explorer/migrations/0002_add_annotation_boolean_columns.py` | New migration |
| `mgnifams_site/explorer/views.py` | Replace `_ANNOTATION_FILTER_MAP` + filter loop; remove unused imports |
| `mgnifams_site/explorer/tests.py` | Add `AnnotationPresenceFilterTests` class |

---

## Task 1: Write Failing Tests

**Files:**
- Modify: `mgnifams_site/explorer/tests.py`

- [ ] **Step 1: Add `AnnotationPresenceFilterTests` class at the end of `tests.py`**

```python
class AnnotationPresenceFilterTests(TestCase):
    def setUp(self):
        cache.clear()
        self.url = reverse('mgnifams_data')
        # f1 has pfam + funfam; no model_pfam, no structure
        make_mgnifam(id=1, has_pfam=True, has_funfam=True, has_model_pfam=False, has_structure=False)
        # f2 has model_pfam + structure; no pfam, no funfam
        make_mgnifam(id=2, has_pfam=False, has_funfam=False, has_model_pfam=True, has_structure=True)

    def _get(self, **params):
        defaults = {
            'draw': 1, 'start': 0, 'length': 50,
            'order[0][column]': 0, 'order[0][dir]': 'asc', 'search[value]': '',
        }
        defaults.update(params)
        return self.client.get(self.url, defaults)

    def _ids(self, r):
        return [row['mgnifam_id'] for row in r.json()['data']]

    def test_has_pfam_yes_returns_only_annotated(self):
        r = self._get(has_pfam='yes')
        self.assertEqual(r.json()['recordsFiltered'], 1)
        self.assertIn('MGYF0000000001', self._ids(r))

    def test_has_pfam_no_returns_only_unannotated(self):
        r = self._get(has_pfam='no')
        self.assertEqual(r.json()['recordsFiltered'], 1)
        self.assertIn('MGYF0000000002', self._ids(r))

    def test_has_funfam_yes_returns_only_annotated(self):
        r = self._get(has_funfam='yes')
        self.assertEqual(r.json()['recordsFiltered'], 1)
        self.assertIn('MGYF0000000001', self._ids(r))

    def test_has_funfam_no_returns_only_unannotated(self):
        r = self._get(has_funfam='no')
        self.assertEqual(r.json()['recordsFiltered'], 1)
        self.assertIn('MGYF0000000002', self._ids(r))

    def test_has_model_pfam_yes_returns_only_annotated(self):
        r = self._get(has_model_pfam='yes')
        self.assertEqual(r.json()['recordsFiltered'], 1)
        self.assertIn('MGYF0000000002', self._ids(r))

    def test_has_model_pfam_no_returns_only_unannotated(self):
        r = self._get(has_model_pfam='no')
        self.assertEqual(r.json()['recordsFiltered'], 1)
        self.assertIn('MGYF0000000001', self._ids(r))

    def test_has_structure_yes_returns_only_annotated(self):
        r = self._get(has_structure='yes')
        self.assertEqual(r.json()['recordsFiltered'], 1)
        self.assertIn('MGYF0000000002', self._ids(r))

    def test_has_structure_no_returns_only_unannotated(self):
        r = self._get(has_structure='no')
        self.assertEqual(r.json()['recordsFiltered'], 1)
        self.assertIn('MGYF0000000001', self._ids(r))

    def test_all_no_filters_return_fully_unannotated_families(self):
        # Add a third family with no annotations at all
        make_mgnifam(id=3, has_pfam=False, has_funfam=False, has_model_pfam=False, has_structure=False)
        r = self._get(has_pfam='no', has_funfam='no', has_model_pfam='no', has_structure='no')
        self.assertEqual(r.json()['recordsFiltered'], 1)
        self.assertIn('MGYF0000000003', self._ids(r))

    def test_annotation_filter_combined_with_range_filter(self):
        r = self._get(has_pfam='yes', full_size_min=100)
        self.assertEqual(r.json()['recordsFiltered'], 1)
        self.assertIn('MGYF0000000001', self._ids(r))

    def test_annotation_filter_any_value_applies_no_filter(self):
        r = self._get(has_pfam='any')
        self.assertEqual(r.json()['recordsFiltered'], 2)
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd /home/vangelis/Desktop/Projects/mgnifams-site
python -m pytest mgnifams_site/explorer/tests.py::AnnotationPresenceFilterTests -v 2>&1 | head -40
```

Expected: `TypeError: make_mgnifam() got an unexpected keyword argument 'has_pfam'`

---

## Task 2: Add Model Fields and Migration

**Files:**
- Modify: `mgnifams_site/explorer/models.py:36-53`
- Create: `mgnifams_site/explorer/migrations/0002_add_annotation_boolean_columns.py`

- [ ] **Step 1: Add 4 fields to `Mgnifam` model in `models.py`**

Insert after `periplasm_percent` (line 21) and before `rep_sequence` (line 22):

```python
    has_pfam = models.BooleanField(default=False)
    has_funfam = models.BooleanField(default=False)
    has_model_pfam = models.BooleanField(default=False)
    has_structure = models.BooleanField(default=False)
```

Also add the 4 indexes to the `Meta.indexes` list (after the existing `idx_mgnifam_periplasm` entry):

```python
            models.Index(fields=['has_pfam'],       name='idx_mgnifam_has_pfam'),
            models.Index(fields=['has_funfam'],     name='idx_mgnifam_has_funfam'),
            models.Index(fields=['has_model_pfam'], name='idx_mgnifam_has_model_pfam'),
            models.Index(fields=['has_structure'],  name='idx_mgnifam_has_structure'),
```

- [ ] **Step 2: Create the migration file**

Create `mgnifams_site/explorer/migrations/0002_add_annotation_boolean_columns.py`:

```python
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
```

- [ ] **Step 3: Run tests — should still fail (model fields exist now but view still uses Exists)**

```bash
python -m pytest mgnifams_site/explorer/tests.py::AnnotationPresenceFilterTests -v 2>&1 | head -40
```

Expected: Tests fail because `make_mgnifam(has_pfam=True, ...)` now works but the view's `Exists()` subqueries check the *related tables*, not the column — and the test setUp creates no related rows. Some tests may accidentally pass (if Exists returns False and `no` filter happens to match), but `has_pfam='yes'` tests will return 0 rows.

---

## Task 3: Update Views Filter Logic

**Files:**
- Modify: `mgnifams_site/explorer/views.py`

- [ ] **Step 1: Replace `_ANNOTATION_FILTER_MAP` (lines 346–351)**

Old:
```python
_ANNOTATION_FILTER_MAP = {
    'has_pfam': MgnifamPfams,
    'has_funfam': MgnifamFunfams,
    'has_model_pfam': MgnifamModelPfams,
    'has_structure': MgnifamFolds,
}
```

New:
```python
_ANNOTATION_FILTER_MAP = {
    'has_pfam': 'has_pfam',
    'has_funfam': 'has_funfam',
    'has_model_pfam': 'has_model_pfam',
    'has_structure': 'has_structure',
}
```

- [ ] **Step 2: Replace the annotation presence filter loop in `mgnifams_data` (lines 437–446)**

Old:
```python
    # Apply annotation presence filters (yes/no/any)
    active_annotation_filters = False
    for param, model in _ANNOTATION_FILTER_MAP.items():
        val = request.GET.get(param, '').strip()
        if val == 'yes':
            qs = qs.filter(Exists(model.objects.filter(mgnifam=OuterRef('pk'))))
            active_annotation_filters = True
        elif val == 'no':
            qs = qs.exclude(Exists(model.objects.filter(mgnifam=OuterRef('pk'))))
            active_annotation_filters = True
```

New:
```python
    # Apply annotation presence filters (yes/no/any)
    active_annotation_filters = False
    for param, field in _ANNOTATION_FILTER_MAP.items():
        val = request.GET.get(param, '').strip()
        if val == 'yes':
            qs = qs.filter(**{field: True})
            active_annotation_filters = True
        elif val == 'no':
            qs = qs.filter(**{field: False})
            active_annotation_filters = True
```

- [ ] **Step 3: Clean up the now-unused imports at the top of `views.py`**

The `Exists` and `OuterRef` imports are still needed by the `annotation_term` filter block (lines 449–466). Leave them in place — do not remove.

Also verify the model imports: `MgnifamPfams`, `MgnifamFunfams`, `MgnifamModelPfams`, `MgnifamFolds` are still used in `_get_pfams_data`, `_get_funfams_data`, etc. Leave them in place.

---

## Task 4: Run Full Test Suite

- [ ] **Step 1: Run all tests**

```bash
cd /home/vangelis/Desktop/Projects/mgnifams-site
python -m pytest mgnifams_site/explorer/tests.py -v 2>&1 | tail -30
```

Expected: All tests pass, including the new `AnnotationPresenceFilterTests`.

- [ ] **Step 2: Confirm new tests all pass**

```bash
python -m pytest mgnifams_site/explorer/tests.py::AnnotationPresenceFilterTests -v
```

Expected output:
```
PASSED tests.py::AnnotationPresenceFilterTests::test_has_pfam_yes_returns_only_annotated
PASSED tests.py::AnnotationPresenceFilterTests::test_has_pfam_no_returns_only_unannotated
PASSED tests.py::AnnotationPresenceFilterTests::test_has_funfam_yes_returns_only_annotated
PASSED tests.py::AnnotationPresenceFilterTests::test_has_funfam_no_returns_only_unannotated
PASSED tests.py::AnnotationPresenceFilterTests::test_has_model_pfam_yes_returns_only_annotated
PASSED tests.py::AnnotationPresenceFilterTests::test_has_model_pfam_no_returns_only_unannotated
PASSED tests.py::AnnotationPresenceFilterTests::test_has_structure_yes_returns_only_annotated
PASSED tests.py::AnnotationPresenceFilterTests::test_has_structure_no_returns_only_unannotated
PASSED tests.py::AnnotationPresenceFilterTests::test_all_no_filters_return_fully_unannotated_families
PASSED tests.py::AnnotationPresenceFilterTests::test_annotation_filter_combined_with_range_filter
PASSED tests.py::AnnotationPresenceFilterTests::test_annotation_filter_any_value_applies_no_filter
```

---

## Task 5: Commit Code Changes

- [ ] **Step 1: Stage and commit**

```bash
git add \
  mgnifams_site/explorer/models.py \
  mgnifams_site/explorer/migrations/0002_add_annotation_boolean_columns.py \
  mgnifams_site/explorer/views.py \
  mgnifams_site/explorer/tests.py \
  docs/superpowers/plans/2026-06-12-annotation-boolean-columns.md

git commit -m "$(cat <<'EOF'
perf: replace NOT EXISTS subqueries with precomputed boolean columns

Eliminates 4 correlated NOT EXISTS subqueries (including one against the
13M-row mgnifam_folds table) that caused the annotation filter on the
mgnifams_list page to hang. Replaces them with direct indexed column lookups
on has_pfam, has_funfam, has_model_pfam, has_structure.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Apply SQL Scripts to Production DB

> Do this after deploying the code, or before — the new columns are ignored by old code and the new code works once the columns exist.

- [ ] **Step 1: Back up the production DB before altering schema**

```bash
cp /path/to/production/mgnifams.sqlite3 /path/to/production/mgnifams.sqlite3.bak_$(date +%Y%m%d)
```

- [ ] **Step 2: Run Script A (add columns, populate, index)**

```bash
sqlite3 /path/to/production/mgnifams.sqlite3 < add_annotation_columns.sql
```

The `has_structure` UPDATE may take several minutes (35K rows × indexed 13M-row table). Do not interrupt.

- [ ] **Step 3: Run Script B to verify population**

```bash
sqlite3 /path/to/production/mgnifams.sqlite3 "
SELECT
    SUM(has_pfam)       AS families_with_pfam,
    SUM(has_funfam)     AS families_with_funfam,
    SUM(has_model_pfam) AS families_with_model_pfam,
    SUM(has_structure)  AS families_with_structure,
    COUNT(*)            AS total_families
FROM mgnifam;
SELECT COUNT(DISTINCT mgnifam_id) AS folds_check FROM mgnifam_folds;
"
```

`families_with_structure` and `folds_check` must match.

- [ ] **Step 4: Run Script C to verify query plan**

```bash
sqlite3 /path/to/production/mgnifams.sqlite3 "
EXPLAIN QUERY PLAN
SELECT id FROM mgnifam
WHERE full_size >= 100
  AND rep_length >= 150
  AND plddt >= 70
  AND strand_percent >= 10
  AND has_pfam = 0
  AND has_funfam = 0
  AND has_model_pfam = 0
  AND has_structure = 0
ORDER BY id;
"
```

Confirm no `CORRELATED SCALAR SUBQUERY` lines appear.

---

## Notes on the Details Page Overview Table

The Overview table in `details.html` (lines 116, 134, 152, 171) renders checkmarks via `{% if funfams_data %}` etc. These lists are already loaded by the `details` view for the full annotation tables below — so there is no extra query cost. The boolean columns would not reduce query count on that page.

If you later want to avoid loading the full annotation lists just for the overview checkmarks (e.g., to speed up a future lightweight details endpoint), you could pass `has_pfam=mgnifam.has_pfam` etc. from the view and update those four `{% if %}` checks in the Overview section. That is out of scope for this plan.
