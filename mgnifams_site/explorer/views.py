import json
import re

import requests
from django.core.cache import cache
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from explorer.models import Mgnifam, MgnifamFolds, MgnifamFunfams, MgnifamModelPfams, MgnifamPfams


def format_family_name(id):
    return 'MGYF' + str(id).zfill(10)


def index(request):
    num_mgnifams = Mgnifam.objects.count()
    first_mgnifam = Mgnifam.objects.only('id').first()
    first_id = format_family_name(str(first_mgnifam.id)) if first_mgnifam else None

    context = {'num_mgnifams': num_mgnifams, 'first_id': first_id}

    return render(request, 'explorer/index.html', context)


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
        print('⚠️ Skylign request timed out')
        return None
    except requests.exceptions.RequestException as e:
        print(f'⚠️ Skylign error: {e}')
        return None


def fetch_skylign_logo_json(uuid):
    url = f'https://skylign.org/logo/{uuid}'  # f'https://pavlopoulos-lab.org/skylign/logo/{uuid}'
    headers = {'Accept': 'application/json'}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return json.dumps(response.json())
    except requests.exceptions.RequestException as e:
        print(f'⚠️ Skylign logo fetch error: {e}')
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


def details(request, pk):
    mgyf_id = translate_mgyf_to_int_id(pk)

    mgnifam = get_object_or_404(Mgnifam.objects.defer('biome_blob', 'domain_blob', 's4pred_blob'), id=mgyf_id)

    full_size = mgnifam.full_size
    protein_rep = format_protein_name(str(mgnifam.protein_rep))
    region = mgnifam.rep_region
    region_start = ''
    region_end = ''
    if region != '-':
        region_parts = region.split('-')
        region_start = region_parts[0]
        region_end = region_parts[1]
    rep_length = mgnifam.rep_length
    converged = mgnifam.converged

    plddt = mgnifam.plddt
    ptm = mgnifam.ptm

    helix_percent = mgnifam.helix_percent
    strand_percent = mgnifam.strand_percent
    coil_percent = mgnifam.coil_percent

    inside_percent = mgnifam.inside_percent
    membrane_alpha_percent = mgnifam.membrane_alpha_percent
    outside_percent = mgnifam.outside_percent
    signal_percent = mgnifam.signal_percent
    membrane_beta_percent = mgnifam.membrane_beta_percent
    periplasm_percent = mgnifam.periplasm_percent

    rep_sequence = mgnifam.rep_sequence
    consensus = mgnifam.consensus

    cif_blob = decode_blob(mgnifam.cif_blob)
    seed_msa_blob = decode_blob(mgnifam.seed_msa_blob)
    rf = decode_blob(mgnifam.rf_blob)
    hmm_blob = decode_blob(mgnifam.hmm_blob)

    hmm_logo_json = 'null'
    if hmm_blob:
        _cache_key = f'skylign_logo_json_{mgyf_id}'
        hmm_logo_json = cache.get(_cache_key) or 'null'
        if hmm_logo_json == 'null':
            response_data = call_skylign_api(hmm_blob)
            if response_data and 'uuid' in response_data:
                uuid = response_data['uuid'].lower()
                fetched = fetch_skylign_logo_json(uuid)
                if fetched is not None:
                    cache.set(_cache_key, fetched, SKYLIGN_CACHE_TIMEOUT)
                    hmm_logo_json = fetched

    tm_blob = mgnifam.tm_blob is not None

    # Fetch related MgnifamPfams objects
    mgnifam_pfams = MgnifamPfams.objects.filter(mgnifam=mgyf_id)
    pfams_data = []
    for mgnifam_pfam in mgnifam_pfams:
        hit = {
            'pfam': mgnifam_pfam.pfam,
            'name': mgnifam_pfam.name,
            'e_value': mgnifam_pfam.e_value,
            'score': mgnifam_pfam.score,
            'hmm_from': mgnifam_pfam.hmm_from,
            'hmm_to': mgnifam_pfam.hmm_to,
            'ali_from': mgnifam_pfam.ali_from,
            'ali_to': mgnifam_pfam.ali_to,
            'env_from': mgnifam_pfam.env_from,
            'env_to': mgnifam_pfam.env_to,
            'acc': mgnifam_pfam.acc,
        }
        pfams_data.append(hit)

    # Fetch related MgnifamFunfams objects
    mgnifam_funfams = MgnifamFunfams.objects.filter(mgnifam=mgyf_id)
    funfams_data = []
    for mgnifam_funfam in mgnifam_funfams:
        try:
            superfamily, ff_part = mgnifam_funfam.funfam.split('-FF-')
            funfam_number = str(int(ff_part))  # e.g., '000002' → 2
            funfam_url = f'http://cathdb.info/version/4_3_0/superfamily/{superfamily}/funfam/{funfam_number}'
        except ValueError:
            superfamily = None
            funfam_number = None
            funfam_url = '#'
        hit = {
            'funfam': mgnifam_funfam.funfam,
            'funfam_url': funfam_url,
            'e_value': mgnifam_funfam.e_value,
            'score': mgnifam_funfam.score,
            'hmm_from': mgnifam_funfam.hmm_from,
            'hmm_to': mgnifam_funfam.hmm_to,
            'ali_from': mgnifam_funfam.ali_from,
            'ali_to': mgnifam_funfam.ali_to,
            'env_from': mgnifam_funfam.env_from,
            'env_to': mgnifam_funfam.env_to,
            'acc': mgnifam_funfam.acc,
        }
        funfams_data.append(hit)

    # Fetch related MgnifamModelPfams objects
    mgnifam_model_pfams = MgnifamModelPfams.objects.filter(mgnifam=mgyf_id)
    pfams_model_data = []
    for mgnifam_model_pfam in mgnifam_model_pfams:
        hit = {
            'pfam': mgnifam_model_pfam.pfam,
            'name': mgnifam_model_pfam.name,
            'description': mgnifam_model_pfam.description,
            'prob': mgnifam_model_pfam.prob,
            'e_value': mgnifam_model_pfam.e_value,
            'length': mgnifam_model_pfam.length,
            'query_hmm': mgnifam_model_pfam.query_hmm,
            'template_hmm': mgnifam_model_pfam.template_hmm,
        }
        pfams_model_data.append(hit)

    # Fetch related MgnifamFolds objects
    mgnifam_folds = MgnifamFolds.objects.filter(mgnifam=mgyf_id).order_by('e_value')
    structural_annotations = []
    for mgnifam_fold in mgnifam_folds:
        link, db = generate_structure_link_and_db(mgnifam_fold.fold)
        annotation = {
            'target_structure_identifier': link,
            'target_structure_db': db,
            'aligned_length': mgnifam_fold.aligned_length,
            'q_start': mgnifam_fold.q_start,
            'q_end': mgnifam_fold.q_end,
            't_start': mgnifam_fold.t_start,
            't_end': mgnifam_fold.t_end,
            'e_value': mgnifam_fold.e_value,
        }
        structural_annotations.append(annotation)
    for i, annotation in enumerate(structural_annotations, start=1):
        annotation['prob'] = i

    return render(
        request,
        'explorer/details.html',
        {
            'mgyf_id': mgyf_id,
            'full_size': full_size,
            'protein_rep': protein_rep,
            'region_start': region_start,
            'region_end': region_end,
            'rep_length': rep_length,
            'rep_sequence': rep_sequence,
            'consensus': consensus,
            'plddt': plddt,
            'ptm': ptm,
            'helix_percent': helix_percent,
            'strand_percent': strand_percent,
            'coil_percent': coil_percent,
            'inside_percent': inside_percent,
            'membrane_alpha_percent': membrane_alpha_percent,
            'outside_percent': outside_percent,
            'signal_percent': signal_percent,
            'membrane_beta_percent': membrane_beta_percent,
            'periplasm_percent': periplasm_percent,
            'membrane_total': membrane_alpha_percent + membrane_beta_percent,
            'converged': converged,
            'cif_blob': cif_blob,
            'seed_msa_blob': seed_msa_blob,
            'rf': rf,
            'hmm_blob': hmm_blob,
            'hmm_logo_json': hmm_logo_json,
            'tm_blob': tm_blob,
            'pfams_data': pfams_data,
            'funfams_data': funfams_data,
            'pfams_model_data': pfams_model_data,
            'structural_annotations': structural_annotations,
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

_FILTER_MAP = {
    'full_size_min': 'full_size__gte',
    'full_size_max': 'full_size__lte',
    'rep_length_min': 'rep_length__gte',
    'rep_length_max': 'rep_length__lte',
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
    records_total = qs.count()

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

    records_filtered = qs.count()

    rows = qs.order_by(sort_field)[start : start + length]
    data = [
        [
            format_family_name(m.id),
            m.full_size,
            m.rep_length,
            m.helix_percent,
            m.strand_percent,
            m.coil_percent,
            m.inside_percent,
            m.membrane_alpha_percent,
            m.outside_percent,
            m.signal_percent,
            m.membrane_beta_percent,
            m.periplasm_percent,
        ]
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
