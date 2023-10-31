import os
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from Bio import SeqIO
import glob

def count_lines_in_file(filepath):
    with open(filepath, 'r') as f:
        return sum(1 for _ in f)

def count_lines_in_files(directory, pattern):
    import glob
    files = glob.glob(os.path.join(directory, pattern))
    return sum(count_lines_in_file(file) for file in files)

def index(request):
    base_dir = "../data/"

    # Calculate statistics
    num_representatives = count_lines_in_file(os.path.join(base_dir, 'rep_names.txt'))
    num_annotations_mg = count_lines_in_files(base_dir, 'mg*.txt')
    num_annotations_reps = count_lines_in_files(base_dir, 'reps.*.tsv')
    num_annotations = num_annotations_mg + num_annotations_reps
    num_unannotated = count_lines_in_file(os.path.join(base_dir, 'unannotated_ids.txt'))

    # Get the first ID from rep_names.txt
    with open(os.path.join(base_dir, 'rep_names.txt'), 'r') as f:
        first_id = f.readline().strip()

    context = {
        'num_representatives': num_representatives,
        'num_annotations': num_annotations,
        'num_unannotated': num_unannotated,
        'first_id': first_id
    }

    return render(request, 'explorer/index.html', context)

def id_exists(check_id, filepath):
    with open(filepath, 'r') as f:
        return check_id in f.read().splitlines()

def get_family_size(target_id, filepath):
    with open(filepath, 'r') as f:
        count = 0
        for line in f:
            if line.split('\t')[0] == target_id:
                count += 1
            # Since the data is sorted, you can break early when the ID changes
            elif count > 0:
                break
        return count

def get_sequence_from_fasta(target_id, filepath):
    for record in SeqIO.parse(filepath, "fasta"):
        if record.id == target_id:
            sequence = str(record.seq)
            length = len(sequence)
            return sequence, length
    return None, None


def details(request):
    id = request.GET.get('id', None)
    
    base_dir = "../data/"
    id_filepath = os.path.join(base_dir, 'rep_names.txt')
    cluster_filepath = os.path.join(base_dir, 'filtered_clusters.tsv')
    fasta_filepath = os.path.join(base_dir, 'reps.fa')

    # Validate if ID exists in rep_names.txt
    if not id_exists(id, id_filepath):
        messages.error(request, 'Invalid ID entered. Please check and try again.')
        return redirect('index')

    # Get the family size
    family_size = get_family_size(id, cluster_filepath)

    # Fetch the sequence from the FASTA file
    sequence, sequence_length = get_sequence_from_fasta(id, os.path.join(base_dir, 'reps.fa'))

    annotations = []

    # Parse mg*.txt files
    for file in glob.glob(os.path.join(base_dir, 'mg*.txt')):
        with open(file, 'r') as f:
            for line in f:
                parts = line.strip().split('\t')
                if parts[0] == id:
                    domain_parts = parts[1].split('|')
                    domain_name = domain_parts[1] + "|" + domain_parts[2]
                    annotations.append({
                        'domain': domain_name,
                        'database': 'Uniprot SwissProt',
                        'description': '-',
                        'start': parts[6],
                        'end': parts[7],
                        'evalue': parts[10],
                        'bit_score': parts[11],
                        'link': f'https://swissmodel.expasy.org/repository/uniprot/{domain_parts[1]}'
                    })

    # Parse reps.*.tsv files
    for file in glob.glob(os.path.join(base_dir, 'reps.*.tsv')):
        with open(file, 'r') as f:
            for line in f:
                parts = line.strip().split('\t')
                if parts[0] == id:
                    base_url = 'https://www.ebi.ac.uk/interpro/entry/'
                    url_db = {
                        'Gene3D': 'cathgene3d',
                        'ProSiteProfiles': 'profile',
                        'SUPERFAMILY': 'ssf',
                        'PANTHER': 'panther',
                        'NCBIfam': 'ncbifam',
                        'CDD': 'cdd',
                        'Hamap': 'hamap',
                        'AntiFam': 'antifam',
                        'Pfam': 'pfam'
                    }
                    suffix = url_db.get(parts[3], '')
                    link = f"{base_url}{suffix}/{parts[4]}"

                    annotations.append({
                        'domain': parts[4],
                        'database': parts[3],
                        'description': parts[5],
                        'start': parts[6],
                        'end': parts[7],
                        'evalue': parts[8],
                        'bit_score': '-',
                        'link': link
                    })

    
    return render(request, 'explorer/details.html', {
        'id': id, 
        'family_size': family_size,
        'sequence': sequence,
        'sequence_length': sequence_length,
        'annotations': annotations
    })

def cluster_reps(request):
    base_dir = "../data/"

    # Read the cluster rep names from the file
    with open(os.path.join(base_dir, 'rep_names.txt'), 'r') as f:
        rep_names = f.readlines()

    return render(request, 'explorer/cluster_reps.html', {'rep_names': rep_names})

def unannotated_ids(request):
    base_dir = "../data/"

    # Read the IDs from the file
    with open(os.path.join(base_dir, 'unannotated_ids.txt'), 'r') as f:
        ids = f.readlines()

    return render(request, 'explorer/unannotated_ids.html', {'ids': ids})

def family_members(request, protein_id):
    base_dir = "../data/"
    members = []

    with open(os.path.join(base_dir, 'filtered_clusters.tsv'), 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            if parts[0] == protein_id:
                members.append(parts[1])

    member_count = len(members)
    return render(request,
        'explorer/family_members.html',
        {'members': members, 'protein_id': protein_id, 'member_count': member_count}
    )
