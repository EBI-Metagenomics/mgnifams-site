import os
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
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

def translate_mgyf_to_file_id(mgyf):
    id = re.sub(r'^MGYF0+', '', mgyf)
    file_id = 'mgnfam' + id
    return file_id              

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

def get_filepath(family_id, sub_dir):
    dir = os.path.join(base_dir, sub_dir)
    search_pattern = os.path.join(dir, family_id + '_*')
    
    for filepath in glob.glob(search_pattern):
        filename = os.path.basename(filepath)
        parts = filename.split('_')
        if parts[0] == family_id:
            # Return the relative path from the base directory
            return os.path.relpath(filepath, base_dir)

    return None

def read_rf_file(family_id):
    rf_folder = os.path.join(base_dir, 'families', 'rf')
    for filename in os.listdir(rf_folder):
        parts = filename.split('_')
        if parts[0] == family_id:
            with open(os.path.join(rf_folder, filename), 'r') as file:
                rf = file.read()
            return rf
    return None

def call_skylign_api(base_dir, file_path):
    url = "http://skylign.org"
    headers = {'Accept': 'application/json'}
    hmm_filepath = os.path.join(base_dir, file_path)
    files = {'file': open(hmm_filepath, 'rb')}
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

def generate_structure_link(part):
    if part.startswith('MGYP'):
        # Remove '.pdb.gz' extension and format link for MGYP
        id = part.replace('.pdb.gz', '')
        return f'<a href="http://proteins.mgnify.org/{id}">{id}</a>'
    elif part.startswith('AF'):
        # Split with '-' and keep the second part for AlphaFold
        af_id = part.split('-')[1]
        return f'<a href="https://alphafold.ebi.ac.uk/entry/{af_id}">{af_id}</a>'
    elif '.cif.gz' in part:
        # Split with '.' and keep the first part for RCSB PDB
        pdb_id = part.split('.')[0]
        return f'<a href="https://www.rcsb.org/structure/{pdb_id}">{pdb_id}</a>'
    else:
        return part

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
        region = f"/{region}"
    else:
        region = ""
    # converged = mgnifam.converged # TODO

    cif_file = mgnifam.cif_file

    seed_msa_file = mgnifam.seed_msa_file
    seed_msa_filepath = os.path.join("families/seed_msa/", seed_msa_file)
    msa_file = mgnifam.msa_file
    full_msa_filepath = os.path.join("families/msa/", msa_file)
    rf_file = mgnifam.rf_file
    rf_filepath = os.path.join("families/rf/", rf_file)
    with open(os.path.join(base_dir, rf_filepath), 'r') as file:
        rf = file.read()
    hmm_file = mgnifam.hmm_file
    hmm_filepath = os.path.join("families/hmm/", hmm_file)
    response_data = call_skylign_api(base_dir, hmm_filepath)
    uuid = ""
    if response_data and 'uuid' in response_data:
        uuid = response_data['uuid']
    hmm_logo_json = fetch_skylign_logo_json(uuid)

    biomes_file = mgnifam.biomes_file
    biomes_filepath = os.path.join("biome_sunburst/result/", biomes_file)
    domain_architecture_file = mgnifam.domain_architecture_file
    domains_json = os.path.join("pfams/translated/", domain_architecture_file)

    # Fetch MgnifamProteins objects
    mgnifam_proteins = MgnifamProteins.objects.filter(mgnifam=mgyf_id)
    family_members_links = []
    for mgnifam_protein in mgnifam_proteins:
        protein_id = mgnifam_protein.protein
        region = mgnifam_protein.region
        family_members_links.append(format_protein_link(protein_id, region))

    # # Fetch related MgnifamPfams objects
    # mgnifam_pfams = MgnifamPfams.objects.filter(mgnifam=mgyf_id)

    # # Fetch related MgnifamFolds objects
    # mgnifam_folds = MgnifamFolds.objects.filter(mgnifam=mgyf_id)

    #######################################

    filename_no_ext = cif_file.split('.')[0]
    first_split = filename_no_ext.split('-')
    first_split_first_part = first_split[0]
    family_id = first_split_first_part.split('_')[0]

    # Model annotation / HHblits
    unannotated_filepath = os.path.join(base_dir, 'hh/unannotated.txt')
    with open(unannotated_filepath, 'r') as file:
        unannotated_content = file.read()
    is_annotated = not (family_id + '_') in unannotated_content
    if is_annotated:
        hits_directory = os.path.join(base_dir, 'hh/hits/')
        hits_files = glob.glob(os.path.join(hits_directory, family_id + '_*'))

        if hits_files:
            with open(hits_files[0], 'r') as file:
                hits_data = []
                for line in file:
                    name = line[4:34].strip()
                    pfam_id = name.split(';')[0].strip().split('.')[0]
                    
                    hit = {
                        'rank': line[0:3].strip(),
                        'name': name,
                        'pfam_id': pfam_id,
                        'e_value': line[41:48].strip(),
                        'query_hmm': line[75:83].strip(),
                        'template_hmm': line[84:99].strip(),
                    }
                    hits_data.append(hit)
        else:
            hits_data = []

    else:
        hits_data = []

    # Structural annotation / Foldseek
    foldseek_annotated_filepath = os.path.join(base_dir, 'foldseek/annotated.txt')
    structural_annotations = []
    with open(foldseek_annotated_filepath, 'r') as file:
        for line in file:
            if line.startswith(family_id + '_'):
                foldseek_folder = os.path.join(base_dir, 'foldseek/')
                for filepath in glob.glob(foldseek_folder + '*'):
                    filename = os.path.basename(filepath)
                    if filename.startswith(('alphafold_', 'esm_', 'pdb_')):
                        with open(filepath, 'r') as f:
                            for file_line in f:
                                parts = file_line.strip().split('\t')
                                first_part = parts[0].split('-')[0].split('_')[0]
                                target_structure_identifier = generate_structure_link(parts[1])
                                if first_part == family_id:
                                    annotation = {
                                        'target_structure_identifier': target_structure_identifier,
                                        'aligned_length': int(parts[3]),
                                        'query_start': int(parts[6]),
                                        'query_end': int(parts[7]),
                                        'target_start': int(parts[8]),
                                        'target_end': int(parts[9]),
                                        'e_value': float(parts[10])
                                    }
                                    structural_annotations.append(annotation)
                        structural_annotations.sort(key=lambda x: x['e_value'])
                        for i, annotation in enumerate(structural_annotations, start=1):
                            annotation['rank'] = i
                break

    return render(request, 'explorer/details.html', {
        'mgyf': mgyf,
        'family_size': family_size,
        'protein_rep': protein_rep,
        'region': region,
        'region_start': region_start,
        'region_end': region_end,
        'cif_path': cif_file,
        'seed_msa_filepath': seed_msa_filepath,
        'full_msa_filepath': full_msa_filepath,
        'rf': rf,
        'hmm_filepath': hmm_filepath,
        'hmm_logo_json': hmm_logo_json,
        'biomes_filepath': biomes_filepath,
        'domains_json': domains_json,
        'family_members_links': family_members_links,
        'hits_data': hits_data,
        'structural_annotations': structural_annotations
    })

def mgnifam_names(request):
    # Read the cluster rep names from the file
    with open(os.path.join(base_dir, 'mgnifam_names.txt'), 'r') as f:
        mgnifam_names = f.readlines()

    return render(request, 'explorer/mgnifam_names.html', {'mgnifam_names': mgnifam_names})
