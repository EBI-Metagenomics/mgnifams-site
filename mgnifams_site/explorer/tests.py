from unittest.mock import patch

from django.core.cache import cache
from django.http import Http404
from django.test import TestCase
from django.urls import reverse

from explorer.models import Mgnifam, MgnifamFolds
from explorer.views import decode_blob, format_family_name, translate_mgyf_to_int_id

BLOB = b'placeholder'
SKYLIGN_PATCH = 'explorer.views.call_skylign_api'
SKYLIGN_LOGO_PATCH = 'explorer.views.fetch_skylign_logo_json'


def make_mgnifam(**kwargs):
    defaults = dict(
        id=1,
        full_size=100,
        protein_rep=123456789012,
        rep_region='10-90',
        rep_length=80,
        converged=True,
        plddt=85.5,
        ptm=0.9,
        helix_percent=30.0,
        strand_percent=20.0,
        coil_percent=50.0,
        inside_percent=10.0,
        membrane_alpha_percent=5.0,
        outside_percent=75.0,
        signal_percent=5.0,
        membrane_beta_percent=3.0,
        periplasm_percent=2.0,
        rep_sequence='ACDEFGHIKLM',
        consensus='ACDEFGHIKLM',
        seed_msa_blob=BLOB,
        hmm_blob=BLOB,
        rf_blob=BLOB,
        cif_blob=BLOB,
        biome_blob=BLOB,
        domain_blob=BLOB,
        s4pred_blob=BLOB,
        tm_blob=BLOB,
    )
    defaults.update(kwargs)
    return Mgnifam.objects.create(**defaults)


class IdConversionTests(TestCase):
    def test_format_family_name(self):
        self.assertEqual(format_family_name(1), 'MGYF0000000001')
        self.assertEqual(format_family_name(9999999999), 'MGYF9999999999')

    def test_translate_valid_id(self):
        self.assertEqual(translate_mgyf_to_int_id('MGYF0000000001'), 1)
        self.assertEqual(translate_mgyf_to_int_id('MGYF0000000042'), 42)

    def test_translate_invalid_id_raises_404(self):
        with self.assertRaises(Http404):
            translate_mgyf_to_int_id('MGYF000000XXXX')

    def test_translate_all_zeros_returns_zero(self):
        # MGYF0000000000 correctly maps to ID 0; if ID 0 doesn't exist the
        # DB lookup (not the parser) will produce the 404.
        self.assertEqual(translate_mgyf_to_int_id('MGYF0000000000'), 0)


class IndexViewTests(TestCase):
    def test_index_empty_db(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_index_with_data(self):
        make_mgnifam()
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['num_mgnifams'], 1)

    def test_index_first_id_formatted(self):
        make_mgnifam(id=7)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.context['first_id'], 'MGYF0000000007')


class DetailsViewTests(TestCase):
    def setUp(self):
        self.family = make_mgnifam()
        self.url = reverse('details', args=['MGYF0000000001'])
        cache.clear()

    @patch(SKYLIGN_LOGO_PATCH, return_value=None)
    @patch(SKYLIGN_PATCH, return_value=None)
    def test_details_ok(self, _mock_api, _mock_logo):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    pass  # placeholder so the class body remains valid if all tests above are removed

    def test_details_nonexistent_id_returns_404(self):
        # Bug #2: the try/except DoesNotExist is dead code; Http404 should propagate
        response = self.client.get(reverse('details', args=['MGYF0000099999']))
        self.assertEqual(response.status_code, 404)

    @patch(SKYLIGN_LOGO_PATCH, return_value=None)
    @patch(SKYLIGN_PATCH, return_value=None)
    def test_converged_true_in_context(self, _mock_api, _mock_logo):
        # Bug #7: view does `mgnifam.converged == "True"` but converged is a BooleanField,
        # so the comparison always returns False even when the DB value is True.
        response = self.client.get(self.url)
        self.assertTrue(response.context['converged'])

    @patch(SKYLIGN_LOGO_PATCH, return_value=None)
    @patch(SKYLIGN_PATCH, return_value=None)
    def test_none_cif_blob_does_not_crash(self, _mock_api, _mock_logo):
        # Bug #1: cif_blob.decode('utf-8') called unconditionally; crashes when None
        make_mgnifam(id=2, cif_blob=None)
        response = self.client.get(reverse('details', args=['MGYF0000000002']))
        self.assertEqual(response.status_code, 200)

    @patch(SKYLIGN_LOGO_PATCH, return_value=None)
    @patch(SKYLIGN_PATCH, return_value=None)
    def test_none_seed_msa_blob_does_not_crash(self, _mock_api, _mock_logo):
        # Bug #1: seed_msa_blob decoded before None check
        make_mgnifam(id=3, seed_msa_blob=None)
        response = self.client.get(reverse('details', args=['MGYF0000000003']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['seed_msa_blob'], '')

    @patch(SKYLIGN_LOGO_PATCH, return_value=None)
    @patch(SKYLIGN_PATCH, return_value=None)
    def test_none_hmm_blob_does_not_crash(self, _mock_api, _mock_logo):
        # Bug #1: hmm_blob.decode('utf-8') called unconditionally
        make_mgnifam(id=4, hmm_blob=None)
        response = self.client.get(reverse('details', args=['MGYF0000000004']))
        self.assertEqual(response.status_code, 200)

    @patch(SKYLIGN_LOGO_PATCH, return_value='"logo_json"')
    @patch(SKYLIGN_PATCH, return_value={'uuid': 'ABCD-1234'})
    def test_skylign_uuid_lowercased(self, _mock_api, _mock_logo):
        self.client.get(self.url)
        _mock_logo.assert_called_once_with('abcd-1234')

    @patch(SKYLIGN_LOGO_PATCH, return_value='"logo_json"')
    @patch(SKYLIGN_PATCH, return_value={'uuid': 'ABCD-1234'})
    def test_skylign_result_cached_on_second_request(self, mock_api, mock_logo):
        # H1: Skylign should only be called once; second request hits cache
        self.client.get(self.url)
        self.client.get(self.url)
        mock_api.assert_called_once()
        mock_logo.assert_called_once()

    @patch(SKYLIGN_LOGO_PATCH, return_value=None)
    @patch(SKYLIGN_PATCH, return_value={'uuid': 'ABCD-1234'})
    def test_failed_skylign_fetch_not_cached(self, mock_api, mock_logo):
        # H1: if logo fetch fails (None), result must not be cached so next
        # request retries instead of serving a stale null forever
        self.client.get(self.url)
        self.client.get(self.url)
        self.assertEqual(mock_api.call_count, 2)
        self.assertEqual(mock_logo.call_count, 2)

    @patch(SKYLIGN_LOGO_PATCH, return_value=None)
    @patch(SKYLIGN_PATCH, return_value=None)
    def test_tm_blob_present_is_truthy_in_context(self, _mock_api, _mock_logo):
        # H5: tm_blob is now passed as a boolean, not decoded blob content
        response = self.client.get(self.url)
        self.assertTrue(response.context['tm_blob'])

    @patch(SKYLIGN_LOGO_PATCH, return_value=None)
    @patch(SKYLIGN_PATCH, return_value=None)
    def test_tm_blob_absent_is_falsy_in_context(self, _mock_api, _mock_logo):
        make_mgnifam(id=5, tm_blob=None)
        response = self.client.get(reverse('details', args=['MGYF0000000005']))
        self.assertFalse(response.context['tm_blob'])

    @patch(SKYLIGN_LOGO_PATCH, return_value=None)
    @patch(SKYLIGN_PATCH, return_value=None)
    def test_biome_domain_s4pred_blobs_not_in_context(self, _mock_api, _mock_logo):
        # H5: these blobs are served via serve_blob endpoint, not passed inline
        response = self.client.get(self.url)
        self.assertNotIn('biome_blob', response.context)
        self.assertNotIn('domain_blob', response.context)
        self.assertNotIn('s4pred_blob', response.context)


class StructuralAnnotationsTests(TestCase):
    @patch(SKYLIGN_LOGO_PATCH, return_value=None)
    @patch(SKYLIGN_PATCH, return_value=None)
    def test_t_start_present_in_structural_annotations(self, _mock_api, _mock_logo):
        # Bug #3: duplicate 't_end' key means t_start is never included in the dict
        family = make_mgnifam()
        MgnifamFolds.objects.create(
            mgnifam=family,
            fold='somestructure.cif.gz',
            aligned_length=50,
            q_start=1,
            q_end=50,
            t_start=10,
            t_end=60,
            e_value=1e-5,
        )
        response = self.client.get(reverse('details', args=['MGYF0000000001']))
        annotations = response.context['structural_annotations']
        self.assertEqual(len(annotations), 1)
        self.assertIn('t_start', annotations[0])
        self.assertEqual(annotations[0]['t_start'], 10)


class MgnifamsListViewTests(TestCase):
    def test_list_returns_200(self):
        response = self.client.get(reverse('mgnifams_list'))
        self.assertEqual(response.status_code, 200)

    def test_list_context_has_data_url(self):
        # C2: list view no longer passes a queryset; data comes via AJAX endpoint
        response = self.client.get(reverse('mgnifams_list'))
        self.assertIn('mgnifams_data_url', response.context)
        self.assertNotIn('mgnifams', response.context)

    def test_details_url_prefix_has_no_double_slash(self):
        response = self.client.get(reverse('mgnifams_list'))
        prefix = response.context['details_url_prefix']
        self.assertNotIn('//', prefix)
        self.assertTrue(prefix.endswith('/'))


class MgnifamsDataViewTests(TestCase):
    def setUp(self):
        self.url = reverse('mgnifams_data')
        make_mgnifam(id=1, full_size=100, rep_length=80, helix_percent=30.0)
        make_mgnifam(id=2, full_size=200, rep_length=160, helix_percent=60.0)

    def _get(self, **params):
        defaults = {
            'draw': 1,
            'start': 0,
            'length': 50,
            'order[0][column]': 0,
            'order[0][dir]': 'asc',
            'search[value]': '',
        }
        defaults.update(params)
        return self.client.get(self.url, defaults)

    def test_returns_valid_json_structure(self):
        r = self._get()
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('draw', data)
        self.assertIn('recordsTotal', data)
        self.assertIn('recordsFiltered', data)
        self.assertIn('data', data)

    def test_records_total_matches_db(self):
        r = self._get()
        self.assertEqual(r.json()['recordsTotal'], 2)

    def test_pagination_length(self):
        r = self._get(length=1)
        self.assertEqual(len(r.json()['data']), 1)

    def test_pagination_start(self):
        # With start=1, length=1 we get the second record (sorted by id asc)
        r = self._get(start=1, length=1, **{'order[0][column]': 0, 'order[0][dir]': 'asc'})
        self.assertEqual(r.json()['data'][0][0], 'MGYF0000000002')

    def test_sort_desc(self):
        r = self._get(**{'order[0][column]': 0, 'order[0][dir]': 'desc'})
        rows = r.json()['data']
        self.assertEqual(rows[0][0], 'MGYF0000000002')
        self.assertEqual(rows[1][0], 'MGYF0000000001')

    def test_range_filter_excludes_rows(self):
        # full_size_min=150 should exclude id=1 (full_size=100)
        r = self._get(full_size_min=150)
        data = r.json()
        self.assertEqual(data['recordsFiltered'], 1)
        self.assertEqual(data['data'][0][0], 'MGYF0000000002')

    def test_search_by_mgyf_id(self):
        r = self._get(**{'search[value]': 'MGYF0000000001'})
        data = r.json()
        self.assertEqual(data['recordsFiltered'], 1)
        self.assertEqual(data['data'][0][0], 'MGYF0000000001')

    def test_search_by_numeric_id(self):
        r = self._get(**{'search[value]': '2'})
        data = r.json()
        self.assertEqual(data['recordsFiltered'], 1)
        self.assertEqual(data['data'][0][0], 'MGYF0000000002')

    def test_search_nonexistent_returns_empty(self):
        r = self._get(**{'search[value]': 'MGYF9999999999'})
        data = r.json()
        self.assertEqual(data['recordsFiltered'], 0)
        self.assertEqual(data['data'], [])

    def test_draw_echoed_back(self):
        r = self._get(draw=42)
        self.assertEqual(r.json()['draw'], 42)

    def test_invalid_params_returns_400(self):
        r = self.client.get(self.url, {'draw': 'bad', 'start': 'x'})
        self.assertEqual(r.status_code, 400)


class ServeBlobViewTests(TestCase):
    def setUp(self):
        self.family = make_mgnifam()

    def test_serve_known_blob_column(self):
        url = reverse('serve_blob_as_file', args=[1, 'hmm_blob'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, BLOB)

    def test_serve_nonexistent_pk_returns_404(self):
        url = reverse('serve_blob_as_file', args=[99999, 'hmm_blob'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_serve_null_blob_returns_404(self):
        # blob column exists but is NULL in the DB → must return 404, not empty 200
        # (empty 200 causes "Unexpected end of JSON input" in the JS fetch handler)
        make_mgnifam(id=2, s4pred_blob=None)
        url = reverse('serve_blob_as_file', args=[2, 's4pred_blob'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_serve_arbitrary_non_blob_column_is_rejected(self):
        # Bug #4: no allowlist — any attribute name accepted, exposing non-blob fields.
        # This test documents the expected secure behaviour (400/403/404);
        # it will FAIL until an allowlist is added to serve_blob_as_file.
        url = reverse('serve_blob_as_file', args=[1, 'rep_sequence'])
        response = self.client.get(url)
        self.assertIn(response.status_code, [400, 403, 404])


class DecodeBlobTests(TestCase):
    """Unit tests for decode_blob — covers the real DB's string-typed BinaryField values."""

    def test_bytes_decoded(self):
        self.assertEqual(decode_blob(b'hello'), 'hello')

    def test_memoryview_decoded(self):
        self.assertEqual(decode_blob(memoryview(b'hello')), 'hello')

    def test_string_passthrough(self):
        # Real SQLite DB stores blobs as str when inserted outside Django ORM.
        self.assertEqual(decode_blob('hello'), 'hello')

    def test_none_returns_fallback(self):
        self.assertEqual(decode_blob(None), '')
        self.assertEqual(decode_blob(None, fallback='n/a'), 'n/a')
