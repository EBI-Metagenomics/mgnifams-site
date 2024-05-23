import os
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from Bio import SeqIO
from explorer.models import Mgnifam, MgnifamProteins, MgnifamPfams, MgnifamFolds
import re
import glob
import requests
import json
import subprocess

# Global init
base_dir = "../data/" # "../data/" "../data_old/"

def count_lines_in_file(filepath):
    with open(filepath, 'r') as f:
        return sum(1 for _ in f)

def index(request):
    # Calculate statistics
    num_mgnifams = count_lines_in_file(os.path.join(base_dir, 'mgnifam_names.txt'))

    # Get the first ID from mgnifam_names.txt
    with open(os.path.join(base_dir, 'mgnifam_names.txt'), 'r') as f:
        first_id = f.readline().strip()

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

def format_protein_link(protein_id, region):
    """
    Formats the protein ID into a clickable link.
    Output: HTML link element
    """
    formatted_name = format_protein_name(str(protein_id))
    link_text      = formatted_name
    region_start   = ""
    region_end     = ""
    if (region != "-"):
        region_parts = region.split("-")
        region_start = region_parts[0]
        region_end   = region_parts[1]
        link_text    = f"{formatted_name}/{region_start}-{region_end}"

    link_url = f"http://proteins.mgnify.org/{formatted_name}"
    if region_start != "":
        link_url += f"/?s={region_start}&e={region_end}"

    return f'<a href="{link_url}">{link_text}</a>'

def call_skylign_api(blob_data):
    url = "http://skylign.org"
    headers = {'Accept': 'application/json'}
    files = {'file': ('filename', blob_data)}
    data = {'processing': 'hmm'}

    response = requests.post(url, headers=headers, files=files, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def fetch_skylign_logo_json(uuid):
    url = f'http://skylign.org/logo/{uuid}'
    headers = {'Accept': 'application/json'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return json.dumps(response.json())
    return None

def generate_structure_link_and_db(part):
    if part.startswith('MGYP'):
        # Remove '.pdb.gz' extension and format link for MGYP
        id = part.replace('.pdb.gz', '')
        return f'<a href="http://proteins.mgnify.org/{id}">{id}</a>', 'ESM'
    elif part.startswith('AF'):
        # Split with '-' and keep the second part for AlphaFold
        af_id = part.split('-')[1]
        return f'<a href="https://alphafold.ebi.ac.uk/entry/{af_id}">{af_id}</a>', 'AlphaFold'
    elif '.cif.gz' in part:
        # Split with '.' and keep the first part for RCSB PDB
        pdb_id = part.split('.')[0]
        return f'<a href="https://www.rcsb.org/structure/{pdb_id}">{pdb_id}</a>', 'PDB'
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

    family_size = mgnifam.family_size
    protein_rep = format_protein_name(str(mgnifam.protein_rep))
    region = mgnifam.rep_region
    region_start = ""
    region_end = ""
    if (region != "-"):
        region_parts = region.split("-")
        region_start = region_parts[0]
        region_end   = region_parts[1]
    plddt = mgnifam.plddt
    converged = mgnifam.converged

    cif_blob = mgnifam.cif_blob.decode('utf-8')

    seed_msa_blob = mgnifam.seed_msa_blob.decode('utf-8')
    if mgnifam.msa_blob is not None:
        msa_blob = mgnifam.msa_blob.decode('utf-8')
    else:
        msa_blob = ""
    rf = mgnifam.rf_blob.decode('utf-8')
    hmm_blob = mgnifam.hmm_blob.decode('utf-8')
    response_data = call_skylign_api(hmm_blob)
    uuid = ""
    if response_data and 'uuid' in response_data:
        uuid = response_data['uuid']
    hmm_logo_json = fetch_skylign_logo_json(uuid)

    biomes_blob = mgnifam.biomes_blob.decode('utf-8')
    domain_architecture_blob = mgnifam.domain_architecture_blob.decode('utf-8')

    # Fetch MgnifamProteins objects
    mgnifam_proteins = MgnifamProteins.objects.filter(mgnifam=mgyf_id)
    family_members_links = []
    for mgnifam_protein in mgnifam_proteins:
        protein_id = mgnifam_protein.protein
        region = mgnifam_protein.region
        family_members_links.append(format_protein_link(protein_id, region))

    # Fetch related MgnifamPfams objects
    mgnifam_pfams = MgnifamPfams.objects.filter(mgnifam=mgyf_id)
    hits_data = []
    for mgnifam_pfam in mgnifam_pfams:
        hit = {
            'rank': mgnifam_pfam.rank,
            'name': mgnifam_pfam.pfam_hit,
            'pfam_id': mgnifam_pfam.pfam_id,
            'e_value': mgnifam_pfam.e_value,
            'query_hmm': mgnifam_pfam.query_hmm_range,
            'template_hmm': mgnifam_pfam.template_hmm_range
        }
        hits_data.append(hit)

    # Fetch related MgnifamFolds objects
    mgnifam_folds = MgnifamFolds.objects.filter(mgnifam=mgyf_id)
    structural_annotations = []
    for mgnifam_fold in mgnifam_folds:
        link, db = generate_structure_link_and_db(mgnifam_fold.target_structure)
        annotation = {
            'target_structure_identifier': link,
            'target_structure_db': db,
            'aligned_length': mgnifam_fold.aligned_length,
            'query_start': mgnifam_fold.query_start,
            'query_end': mgnifam_fold.query_end,
            'target_start': mgnifam_fold.target_start,
            'target_end': mgnifam_fold.target_end,
            'e_value': mgnifam_fold.e_value
        }
        structural_annotations.append(annotation)
    structural_annotations.sort(key=lambda x: x['e_value'])
    for i, annotation in enumerate(structural_annotations, start=1):
        annotation['rank'] = i

    return render(request, 'explorer/details.html', {
        'mgyf': mgyf,
        'mgyf_id': mgyf_id,
        'family_size': family_size,
        'protein_rep': protein_rep,
        'region_start': region_start,
        'region_end': region_end,
        'plddt': plddt,
        'converged': converged,
        'cif_blob': cif_blob,
        'seed_msa_blob': seed_msa_blob,
        'msa_blob': msa_blob,
        'rf': rf,
        'hmm_blob': hmm_blob,
        'hmm_logo_json': hmm_logo_json,
        'biomes_blob': biomes_blob,
        'domain_architecture_blob': domain_architecture_blob,
        'family_members_links': family_members_links,
        'hits_data': hits_data,
        'structural_annotations': structural_annotations
    })

def mgnifam_names(request):
    # Read the cluster rep names from the file
    with open(os.path.join(base_dir, 'mgnifam_names.txt'), 'r') as f:
        mgnifam_names = f.readlines()

    return render(request, 'explorer/mgnifam_names.html', {'mgnifam_names': mgnifam_names})

def serve_blob_as_file(request, pk, column_name):
    mgnifam_instance = get_object_or_404(Mgnifam, pk=pk)
    blob_data = getattr(mgnifam_instance, column_name)
    response = HttpResponse(blob_data, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment;'
    return response