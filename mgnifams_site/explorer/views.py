import json
import logging
import re

import requests
from django.core.cache import cache
from django.db.models import Exists, OuterRef, Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from explorer.models import Mgnifam, MgnifamFolds, MgnifamFunfams, MgnifamModelPfams, MgnifamPfams
from explorer.utils import format_family_name

logger = logging.getLogger(__name__)


def index(request):
    num_mgnifams = Mgnifam.objects.count()
    first_mgnifam = Mgnifam.objects.only('id').first()
    first_id = format_family_name(str(first_mgnifam.id)) if first_mgnifam else None

    return render(
        request,
        'explorer/index.html',
        {
            'num_mgnifams': num_mgnifams,
            'first_id': first_id,
            'mgnifams_data_url': reverse('mgnifams_data'),
            'details_url_prefix': reverse('details', args=['MGYF0000000001']).replace('MGYF0000000001/', ''),
        },
    )


def translate_mgyf_to_int_id(mgyf):
    id = re.sub(r'^MGYF0*', '', mgyf)
    try:
        return int(id) if id else 0
    except ValueError:
        raise Http404(f'Invalid MGYF identifier: {mgyf}')


def format_protein_name(raw_name):
    """
    Formats the protein name by appending zeros in front to make it 12 characters,
    and then adds 'MGYP' as a prefix.
    """
    formatted_name = raw_name.zfill(12)  # Append zeros to make it 12 characters
    return 'MGYP' + formatted_name


SKYLIGN_CACHE_TIMEOUT = 7 * 24 * 3600  # 1 week — DB is static so results never change


def call_skylign_api(blob_data):
    url = 'https://skylign.org'  # "https://pavlopoulos-lab.org/skylign/"
    headers = {'Accept': 'application/json'}
    files = {'file': ('filename', blob_data)}
    data = {'processing': 'hmm'}

    try:
        response = requests.post(url, headers=headers, files=files, data=data, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logger.warning('Skylign request timed out')
        return None
    except requests.exceptions.RequestException as e:
        logger.warning('Skylign error: %s', e)
        return None


def fetch_skylign_logo_json(uuid):
    url = f'https://skylign.org/logo/{uuid}'  # f'https://pavlopoulos-lab.org/skylign/logo/{uuid}'
    headers = {'Accept': 'application/json'}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return json.dumps(response.json())
    except requests.exceptions.RequestException as e:
        logger.warning('Skylign logo fetch error: %s', e)
    return None


def decode_blob(blob, fallback=''):
    if blob is None:
        return fallback
    if isinstance(blob, (bytes, memoryview)):
        return bytes(blob).decode('utf-8')
    return str(blob)


def generate_structure_link_and_db(part):
    if part.startswith('AF'):
        # Split with '-' and keep the second part for AlphaFold
        af_id = part.split('-')[1]
        return f'<a href="https://alphafold.ebi.ac.uk/entry/{af_id}">{af_id}</a>', 'AlphaFold'
    elif '.cif.gz' in part:
        # Split with '.' and keep the first part for RCSB PDB
        pdb_id = part.split('.')[0]
        return f'<a href="https://www.ebi.ac.uk/pdbe/entry/pdb/{pdb_id}">{pdb_id}</a>', 'PDB'
    else:
        return part, ''


def _get_hmm_logo_json(mgyf_id, hmm_blob):
    if not hmm_blob:
        return 'null'
    cache_key = f'skylign_logo_json_{mgyf_id}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    response_data = call_skylign_api(hmm_blob)
    if response_data and 'uuid' in response_data:
        uuid = response_data['uuid'].lower()
        fetched = fetch_skylign_logo_json(uuid)
        if fetched is not None:
            cache.set(cache_key, fetched, SKYLIGN_CACHE_TIMEOUT)
            return fetched
    return 'null'


def _get_pfams_data(mgyf_id):
    return [
        {
            'pfam': p.pfam,
            'name': p.name,
            'e_value': p.e_value,
            'score': p.score,
            'hmm_from': p.hmm_from,
            'hmm_to': p.hmm_to,
            'ali_from': p.ali_from,
            'ali_to': p.ali_to,
            'env_from': p.env_from,
            'env_to': p.env_to,
            'acc': p.acc,
        }
        for p in MgnifamPfams.objects.filter(mgnifam=mgyf_id)
    ]


def _get_funfams_data(mgyf_id):
    results = []
    for f in MgnifamFunfams.objects.filter(mgnifam=mgyf_id):
        try:
            superfamily, ff_part = f.funfam.split('-FF-')
            funfam_number = str(int(ff_part))  # e.g., '000002' → 2
            funfam_url = f'http://cathdb.info/version/4_3_0/superfamily/{superfamily}/funfam/{funfam_number}'
        except ValueError:
            funfam_url = '#'
        results.append(
            {
                'funfam': f.funfam,
                'funfam_url': funfam_url,
                'e_value': f.e_value,
                'score': f.score,
                'hmm_from': f.hmm_from,
                'hmm_to': f.hmm_to,
                'ali_from': f.ali_from,
                'ali_to': f.ali_to,
                'env_from': f.env_from,
                'env_to': f.env_to,
                'acc': f.acc,
            }
        )
    return results


def _get_model_pfams_data(mgyf_id):
    return [
        {
            'pfam': p.pfam,
            'name': p.name,
            'description': p.description,
            'prob': p.prob,
            'e_value': p.e_value,
            'length': p.length,
            'query_hmm': p.query_hmm,
            'template_hmm': p.template_hmm,
        }
        for p in MgnifamModelPfams.objects.filter(mgnifam=mgyf_id)
    ]


def _get_structural_annotations(mgyf_id):
    annotations = []
    for i, fold in enumerate(MgnifamFolds.objects.filter(mgnifam=mgyf_id).order_by('e_value'), start=1):
        link, db = generate_structure_link_and_db(fold.fold)
        annotations.append(
            {
                'prob': i,
                'target_structure_identifier': link,
                'target_structure_db': db,
                'aligned_length': fold.aligned_length,
                'q_start': fold.q_start,
                'q_end': fold.q_end,
                't_start': fold.t_start,
                't_end': fold.t_end,
                'e_value': fold.e_value,
            }
        )
    return annotations


def details(request, pk):
    mgyf_id = translate_mgyf_to_int_id(pk)
    mgnifam = get_object_or_404(Mgnifam.objects.defer('biome_blob', 'domain_blob', 's4pred_blob'), id=mgyf_id)

    region = mgnifam.rep_region
    region_start, region_end = ('', '')
    if region != '-':
        region_start, region_end = region.split('-')

    cif_blob = decode_blob(mgnifam.cif_blob)
    seed_msa_blob = decode_blob(mgnifam.seed_msa_blob)
    rf = decode_blob(mgnifam.rf_blob)
    hmm_blob = decode_blob(mgnifam.hmm_blob)

    return render(
        request,
        'explorer/details.html',
        {
            'mgyf_id': mgyf_id,
            'full_size': mgnifam.full_size,
            'protein_rep': format_protein_name(str(mgnifam.protein_rep)),
            'region_start': region_start,
            'region_end': region_end,
            'rep_length': mgnifam.rep_length,
            'rep_sequence': mgnifam.rep_sequence,
            'consensus': mgnifam.consensus,
            'plddt': mgnifam.plddt,
            'ptm': mgnifam.ptm,
            'helix_percent': mgnifam.helix_percent,
            'strand_percent': mgnifam.strand_percent,
            'coil_percent': mgnifam.coil_percent,
            'inside_percent': mgnifam.inside_percent,
            'membrane_alpha_percent': mgnifam.membrane_alpha_percent,
            'outside_percent': mgnifam.outside_percent,
            'signal_percent': mgnifam.signal_percent,
            'membrane_beta_percent': mgnifam.membrane_beta_percent,
            'periplasm_percent': mgnifam.periplasm_percent,
            'membrane_total': mgnifam.membrane_alpha_percent + mgnifam.membrane_beta_percent,
            'converged': mgnifam.converged,
            'cif_blob': cif_blob,
            'seed_msa_blob': seed_msa_blob,
            'rf': rf,
            'hmm_blob': hmm_blob,
            'hmm_logo_json': _get_hmm_logo_json(mgyf_id, hmm_blob),
            'tm_blob': mgnifam.tm_blob is not None,
            'pfams_data': _get_pfams_data(mgyf_id),
            'funfams_data': _get_funfams_data(mgyf_id),
            'pfams_model_data': _get_model_pfams_data(mgyf_id),
            'structural_annotations': _get_structural_annotations(mgyf_id),
        },
    )


BLOB_COLUMNS = {
    'seed_msa_blob',
    'hmm_blob',
    'rf_blob',
    'cif_blob',
    'biome_blob',
    'domain_blob',
    's4pred_blob',
    'tm_blob',
}


def serve_blob_as_file(request, pk, column_name):
    if column_name not in BLOB_COLUMNS:
        raise Http404(f'Unknown blob column: {column_name}')
    mgnifam_instance = get_object_or_404(Mgnifam.objects.only(column_name), pk=pk)
    blob_data = getattr(mgnifam_instance, column_name)
    if not blob_data:
        raise Http404(f'No data for column: {column_name}')
    response = HttpResponse(blob_data, content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment;'
    response['Cache-Control'] = 'public, max-age=86400'  # 24 h — DB is static
    return response


_LIST_FIELDS = [
    'id',
    'full_size',
    'rep_length',
    'plddt',
    'ptm',
    'helix_percent',
    'strand_percent',
    'coil_percent',
    'inside_percent',
    'membrane_alpha_percent',
    'outside_percent',
    'signal_percent',
    'membrane_beta_percent',
    'periplasm_percent',
]

_ANNOTATION_FILTER_MAP = {
    'has_pfam': MgnifamPfams,
    'has_funfam': MgnifamFunfams,
    'has_model_pfam': MgnifamModelPfams,
    'has_structure': MgnifamFolds,
}

_FILTER_MAP = {
    'full_size_min': 'full_size__gte',
    'full_size_max': 'full_size__lte',
    'rep_length_min': 'rep_length__gte',
    'rep_length_max': 'rep_length__lte',
    'plddt_min': 'plddt__gte',
    'plddt_max': 'plddt__lte',
    'ptm_min': 'ptm__gte',
    'ptm_max': 'ptm__lte',
    'helix_min': 'helix_percent__gte',
    'helix_max': 'helix_percent__lte',
    'strand_min': 'strand_percent__gte',
    'strand_max': 'strand_percent__lte',
    'coil_min': 'coil_percent__gte',
    'coil_max': 'coil_percent__lte',
    'inside_min': 'inside_percent__gte',
    'inside_max': 'inside_percent__lte',
    'membrane_alpha_min': 'membrane_alpha_percent__gte',
    'membrane_alpha_max': 'membrane_alpha_percent__lte',
    'outside_min': 'outside_percent__gte',
    'outside_max': 'outside_percent__lte',
    'signal_min': 'signal_percent__gte',
    'signal_max': 'signal_percent__lte',
    'membrane_beta_min': 'membrane_beta_percent__gte',
    'membrane_beta_max': 'membrane_beta_percent__lte',
    'periplasm_min': 'periplasm_percent__gte',
    'periplasm_max': 'periplasm_percent__lte',
}


def mgnifams_list(request):
    return render(
        request,
        'explorer/mgnifams_list.html',
        {
            'mgnifams_data_url': reverse('mgnifams_data'),
            'details_url_prefix': reverse('details', args=['MGYF0000000001']).replace('MGYF0000000001/', ''),
        },
    )


def mgnifams_data(request):
    try:
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 50))
        order_col = int(request.GET.get('order[0][column]', 0))
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid parameters'}, status=400)

    order_dir = request.GET.get('order[0][dir]', 'asc')
    search_value = request.GET.get('search[value]', '').strip()

    sort_field = _LIST_FIELDS[order_col] if 0 <= order_col < len(_LIST_FIELDS) else 'id'
    if order_dir == 'desc':
        sort_field = '-' + sort_field

    qs = Mgnifam.objects.only(*_LIST_FIELDS)

    records_total = cache.get_or_set('mgnifam_total_count', Mgnifam.objects.count, timeout=None)

    # Apply range filters
    active_filters = {}
    for param, lookup in _FILTER_MAP.items():
        val = request.GET.get(param, '').strip()
        if val:
            try:
                active_filters[lookup] = float(val)
            except ValueError:
                pass
    if active_filters:
        qs = qs.filter(**active_filters)

    # Global search by family ID
    if search_value:
        try:
            if search_value.upper().startswith('MGYF'):
                search_id = translate_mgyf_to_int_id(search_value)
            else:
                search_id = int(search_value)
            qs = qs.filter(id=search_id)
        except (ValueError, Http404):
            qs = qs.none()

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

    # Apply annotation text search across Pfam/FunFam tables
    annotation_term = request.GET.get('annotation_term', '').strip()
    if len(annotation_term) >= 4:
        qs = qs.filter(
            Exists(
                MgnifamPfams.objects.filter(mgnifam=OuterRef('pk')).filter(
                    Q(pfam__icontains=annotation_term) | Q(name__icontains=annotation_term)
                )
            )
            | Exists(
                MgnifamModelPfams.objects.filter(mgnifam=OuterRef('pk')).filter(
                    Q(pfam__icontains=annotation_term)
                    | Q(name__icontains=annotation_term)
                    | Q(description__icontains=annotation_term)
                )
            )
            | Exists(MgnifamFunfams.objects.filter(mgnifam=OuterRef('pk'), funfam__icontains=annotation_term))
        )
        active_annotation_filters = True

    has_filters = bool(active_filters) or bool(search_value) or active_annotation_filters
    records_filtered = qs.count() if has_filters else records_total

    rows = qs.order_by(sort_field)[start : start + length]
    data = [
        {
            'mgnifam_id': format_family_name(m.id),
            'full_size': m.full_size,
            'rep_length': m.rep_length,
            'plddt': m.plddt,
            'ptm': m.ptm,
            'helix_percent': m.helix_percent,
            'strand_percent': m.strand_percent,
            'coil_percent': m.coil_percent,
            'inside_percent': m.inside_percent,
            'membrane_alpha_percent': m.membrane_alpha_percent,
            'outside_percent': m.outside_percent,
            'signal_percent': m.signal_percent,
            'membrane_beta_percent': m.membrane_beta_percent,
            'periplasm_percent': m.periplasm_percent,
        }
        for m in rows
    ]

    return JsonResponse(
        {
            'draw': draw,
            'recordsTotal': records_total,
            'recordsFiltered': records_filtered,
            'data': data,
        }
    )
