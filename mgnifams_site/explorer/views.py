from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from explorer.models import Mgnifam, MgnifamFunfams, MgnifamPfams, MgnifamFolds
import xml.etree.ElementTree as ET
import re
import requests
import json

def format_family_name(id):
    return "MGYF" + str(id).zfill(10)    

def index(request):
    num_mgnifams  = Mgnifam.objects.count()
    first_mgnifam = Mgnifam.objects.first()
    first_id = format_family_name(str(first_mgnifam.id)) if first_mgnifam else None

    context = {
        'num_mgnifams': num_mgnifams,
        'first_id': first_id
    }

    return render(request, 'explorer/index.html', context)           

def translate_mgyf_to_int_id(mgyf):
    id = re.sub(r'^MGYF0+', '', mgyf)
    return int(id)              

def format_protein_name(raw_name):
    """
    Formats the protein name by appending zeros in front to make it 12 characters,
    and then adds 'MGYP' as a prefix.
    """
    formatted_name = raw_name.zfill(12)  # Append zeros to make it 12 characters
    return "MGYP" + formatted_name

def call_skylign_api(blob_data):
    url = "https://pavlopoulos-lab.org/skylign/" # "http://skylign.org"
    headers = {'Accept': 'application/json'}
    files = {'file': ('filename', blob_data)}
    data = {'processing': 'hmm'}

    response = requests.post(url, headers=headers, files=files, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def fetch_skylign_logo_json(uuid):
    url = f'https://pavlopoulos-lab.org/skylign/logo/{uuid}' # f'http://skylign.org/logo/{uuid}'
    headers = {'Accept': 'application/json'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return json.dumps(response.json())
    return None

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

def details(request):
    mgyf = request.GET.get('id', None)
    mgyf_id = translate_mgyf_to_int_id(mgyf)

    try:
        # Fetch Mgnifam object
        mgnifam = Mgnifam.objects.get(id=mgyf_id)
    except Mgnifam.DoesNotExist:
        messages.error(request, 'Invalid ID entered. Please check and try again.')
        return redirect('index')

    full_size = mgnifam.full_size
    protein_rep = format_protein_name(str(mgnifam.protein_rep))
    region = mgnifam.rep_region
    region_start = ""
    region_end = ""
    if (region != "-"):
        region_parts = region.split("-")
        region_start = region_parts[0]
        region_end   = region_parts[1]
    rep_length = mgnifam.rep_length
    converged = (mgnifam.converged == "True") # casting to boolean

    plddt = mgnifam.plddt
    ptm = mgnifam.ptm

    helix_percent = mgnifam.helix_percent
    strand_percent = mgnifam.strand_percent
    coil_percent = mgnifam.coil_percent

    inside_percent = mgnifam.inside_percent
    membrane_percent = mgnifam.membrane_percent
    outside_percent = mgnifam.outside_percent

    rep_sequence = mgnifam.rep_sequence
    consensus = mgnifam.consensus

    cif_blob = mgnifam.cif_blob.decode('utf-8')

    seed_msa_blob = mgnifam.seed_msa_blob.decode('utf-8')
    if mgnifam.seed_msa_blob is not None:
        seed_msa_blob = mgnifam.seed_msa_blob.decode('utf-8')
    else:
        seed_msa_blob = ""
    rf = mgnifam.rf_blob.decode('utf-8')
    hmm_blob = mgnifam.hmm_blob.decode('utf-8')
    response_data = call_skylign_api(hmm_blob)
    uuid = ""
    if response_data and 'uuid' in response_data:
        uuid = response_data['uuid']
    hmm_logo_json = fetch_skylign_logo_json(uuid)

    biome_blob = mgnifam.biome_blob.decode('utf-8')
    domain_blob = mgnifam.domain_blob.decode('utf-8')
    s4pred_blob = mgnifam.s4pred_blob.decode('utf-8')
    tm_blob = mgnifam.tm_blob.decode('utf-8') if mgnifam.tm_blob else ''

    # Fetch related MgnifamFunfams objects
    mgnifam_funfams = MgnifamFunfams.objects.filter(mgnifam=mgyf_id)
    funfams_data = []
    for mgnifam_funfam in mgnifam_funfams:
        try:
            superfamily, ff_part = mgnifam_funfam.funfam.split('-FF-')
            funfam_number = str(int(ff_part))  # e.g., '000002' → 2
            funfam_url = f"http://cathdb.info/version/4_3_0/superfamily/{superfamily}/funfam/{funfam_number}"
        except ValueError:
            superfamily = None
            funfam_number = None
            funfam_url = "#"
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
            'acc': mgnifam_funfam.acc
        }
        funfams_data.append(hit)

    # Fetch related MgnifamPfams objects
    mgnifam_pfams = MgnifamPfams.objects.filter(mgnifam=mgyf_id)
    hits_data = []
    for mgnifam_pfam in mgnifam_pfams:
        hit = {
            'pfam': mgnifam_pfam.pfam,
            'name': mgnifam_pfam.name,
            'description': mgnifam_pfam.description,
            'prob': mgnifam_pfam.prob,
            'e_value': mgnifam_pfam.e_value,
            'length': mgnifam_pfam.length,
            'query_hmm': mgnifam_pfam.query_hmm,
            'template_hmm': mgnifam_pfam.template_hmm
        }
        hits_data.append(hit)

    # Fetch related MgnifamFolds objects
    mgnifam_folds = MgnifamFolds.objects.filter(mgnifam=mgyf_id)
    structural_annotations = []
    for mgnifam_fold in mgnifam_folds:
        link, db = generate_structure_link_and_db(mgnifam_fold.fold)
        annotation = {
            'target_structure_identifier': link,
            'target_structure_db': db,
            'aligned_length': mgnifam_fold.aligned_length,
            'q_start': mgnifam_fold.q_start,
            'q_end': mgnifam_fold.q_end,
            't_end': mgnifam_fold.t_end,
            't_end': mgnifam_fold.t_end,
            'e_value': mgnifam_fold.e_value
        }
        structural_annotations.append(annotation)
    structural_annotations.sort(key=lambda x: x['e_value'])
    for i, annotation in enumerate(structural_annotations, start=1):
        annotation['prob'] = i

    return render(request, 'explorer/details.html', {
        'mgyf': mgyf,
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
        'membrane_percent': membrane_percent,
        'outside_percent': outside_percent,
        'converged': converged,
        'cif_blob': cif_blob,
        'seed_msa_blob': seed_msa_blob,
        'rf': rf,
        'hmm_blob': hmm_blob,
        'hmm_logo_json': hmm_logo_json,
        'biome_blob': biome_blob,
        'domain_blob': domain_blob,
        's4pred_blob': s4pred_blob,
        'tm_blob': tm_blob,
        'funfams_data': funfams_data,
        'hits_data': hits_data,
        'structural_annotations': structural_annotations
    })

def serve_blob_as_file(request, pk, column_name):
    mgnifam_instance = get_object_or_404(Mgnifam, pk=pk)
    blob_data = getattr(mgnifam_instance, column_name)
    response = HttpResponse(blob_data, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment;'
    return response

# def send_hmmsearch_request(mgyf_id):
#     mgnifam  = get_object_or_404(Mgnifam, id=mgyf_id)
#     hmm_blob = mgnifam.hmm_blob

#     url = "https://www.ebi.ac.uk/Tools/hmmer/search/hmmsearch"
#     headers = {
#         'Expect': '',
#         'Accept': 'text/xml',
#     }
#     data = {
#         'seqdb': 'pdb',
#         'seq': hmm_blob
#     }
#     response = requests.post(url, headers=headers, data=data)

#     return response.content

# def submit_hmmsearch(request, mgyf_id):
#     response_content = send_hmmsearch_request(mgyf_id)

#     # Parse XML response to extract UUID
#     root = ET.fromstring(response_content)
#     uuid = root.find(".//data[@name='results']").attrib.get('uuid')

#     hmmer_url = f"https://www.ebi.ac.uk/Tools/hmmer/results/{uuid}/domain"
    
#     return redirect(hmmer_url)
