from django.test import TestCase
from django.urls import reverse
from django.http import Http404
from unittest.mock import patch
from explorer.models import Mgnifam, MgnifamFolds
from explorer.views import translate_mgyf_to_int_id, format_family_name, decode_blob


BLOB = b"placeholder"
SKYLIGN_PATCH = "explorer.views.call_skylign_api"
SKYLIGN_LOGO_PATCH = "explorer.views.fetch_skylign_logo_json"


def make_mgnifam(**kwargs):
    defaults = dict(
        id=1,
        full_size=100,
        protein_rep=123456789012,
        rep_region="10-90",
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
        rep_sequence="ACDEFGHIKLM",
        consensus="ACDEFGHIKLM",
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
        self.assertEqual(format_family_name(1), "MGYF0000000001")
        self.assertEqual(format_family_name(9999999999), "MGYF9999999999")

    def test_translate_valid_id(self):
        self.assertEqual(translate_mgyf_to_int_id("MGYF0000000001"), 1)
        self.assertEqual(translate_mgyf_to_int_id("MGYF0000000042"), 42)

    def test_translate_invalid_id_raises_404(self):
        with self.assertRaises(Http404):
            translate_mgyf_to_int_id("MGYF000000XXXX")

    def test_translate_all_zeros_returns_zero(self):
        # MGYF0000000000 correctly maps to ID 0; if ID 0 doesn't exist the
        # DB lookup (not the parser) will produce the 404.
        self.assertEqual(translate_mgyf_to_int_id("MGYF0000000000"), 0)


class IndexViewTests(TestCase):
    def test_index_empty_db(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_index_with_data(self):
        make_mgnifam()
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["num_mgnifams"], 1)


class DetailsViewTests(TestCase):
    def setUp(self):
        self.family = make_mgnifam()
        self.url = reverse("details", args=["MGYF0000000001"])

    @patch(SKYLIGN_LOGO_PATCH, return_value=None)
    @patch(SKYLIGN_PATCH, return_value=None)
    def test_details_ok(self, _mock_api, _mock_logo):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    pass  # placeholder so the class body remains valid if all tests above are removed

    def test_details_nonexistent_id_returns_404(self):
        # Bug #2: the try/except DoesNotExist is dead code; Http404 should propagate
        response = self.client.get(reverse("details", args=["MGYF0000099999"]))
        self.assertEqual(response.status_code, 404)

    @patch(SKYLIGN_LOGO_PATCH, return_value=None)
    @patch(SKYLIGN_PATCH, return_value=None)
    def test_converged_true_in_context(self, _mock_api, _mock_logo):
        # Bug #7: view does `mgnifam.converged == "True"` but converged is a BooleanField,
        # so the comparison always returns False even when the DB value is True.
        response = self.client.get(self.url)
        self.assertTrue(response.context["converged"])

    @patch(SKYLIGN_LOGO_PATCH, return_value=None)
    @patch(SKYLIGN_PATCH, return_value=None)
    def test_none_cif_blob_does_not_crash(self, _mock_api, _mock_logo):
        # Bug #1: cif_blob.decode('utf-8') called unconditionally; crashes when None
        make_mgnifam(id=2, cif_blob=None)
        response = self.client.get(reverse("details", args=["MGYF0000000002"]))
        self.assertEqual(response.status_code, 200)

    @patch(SKYLIGN_LOGO_PATCH, return_value=None)
    @patch(SKYLIGN_PATCH, return_value=None)
    def test_none_seed_msa_blob_does_not_crash(self, _mock_api, _mock_logo):
        # Bug #1: seed_msa_blob decoded before None check
        make_mgnifam(id=3, seed_msa_blob=None)
        response = self.client.get(reverse("details", args=["MGYF0000000003"]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["seed_msa_blob"], "")

    @patch(SKYLIGN_LOGO_PATCH, return_value=None)
    @patch(SKYLIGN_PATCH, return_value=None)
    def test_none_hmm_blob_does_not_crash(self, _mock_api, _mock_logo):
        # Bug #1: hmm_blob.decode('utf-8') called unconditionally
        make_mgnifam(id=4, hmm_blob=None)
        response = self.client.get(reverse("details", args=["MGYF0000000004"]))
        self.assertEqual(response.status_code, 200)

    @patch(SKYLIGN_LOGO_PATCH, return_value='"logo_json"')
    @patch(SKYLIGN_PATCH, return_value={"uuid": "ABCD-1234"})
    def test_skylign_uuid_lowercased(self, _mock_api, _mock_logo):
        self.client.get(self.url)
        _mock_logo.assert_called_once_with("abcd-1234")


class StructuralAnnotationsTests(TestCase):
    @patch(SKYLIGN_LOGO_PATCH, return_value=None)
    @patch(SKYLIGN_PATCH, return_value=None)
    def test_t_start_present_in_structural_annotations(self, _mock_api, _mock_logo):
        # Bug #3: duplicate 't_end' key means t_start is never included in the dict
        family = make_mgnifam()
        MgnifamFolds.objects.create(
            mgnifam=family,
            fold="somestructure.cif.gz",
            aligned_length=50,
            q_start=1,
            q_end=50,
            t_start=10,
            t_end=60,
            e_value=1e-5,
        )
        response = self.client.get(reverse("details", args=["MGYF0000000001"]))
        annotations = response.context["structural_annotations"]
        self.assertEqual(len(annotations), 1)
        self.assertIn("t_start", annotations[0])
        self.assertEqual(annotations[0]["t_start"], 10)


class ServeBlobViewTests(TestCase):
    def setUp(self):
        self.family = make_mgnifam()

    def test_serve_known_blob_column(self):
        url = reverse("serve_blob_as_file", args=[1, "hmm_blob"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, BLOB)

    def test_serve_nonexistent_pk_returns_404(self):
        url = reverse("serve_blob_as_file", args=[99999, "hmm_blob"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_serve_arbitrary_non_blob_column_is_rejected(self):
        # Bug #4: no allowlist — any attribute name accepted, exposing non-blob fields.
        # This test documents the expected secure behaviour (400/403/404);
        # it will FAIL until an allowlist is added to serve_blob_as_file.
        url = reverse("serve_blob_as_file", args=[1, "rep_sequence"])
        response = self.client.get(url)
        self.assertIn(response.status_code, [400, 403, 404])


class DecodeBlobTests(TestCase):
    """Unit tests for decode_blob — covers the real DB's string-typed BinaryField values."""

    def test_bytes_decoded(self):
        self.assertEqual(decode_blob(b"hello"), "hello")

    def test_memoryview_decoded(self):
        self.assertEqual(decode_blob(memoryview(b"hello")), "hello")

    def test_string_passthrough(self):
        # Real SQLite DB stores blobs as str when inserted outside Django ORM.
        self.assertEqual(decode_blob("hello"), "hello")

    def test_none_returns_fallback(self):
        self.assertEqual(decode_blob(None), "")
        self.assertEqual(decode_blob(None, fallback="n/a"), "n/a")
