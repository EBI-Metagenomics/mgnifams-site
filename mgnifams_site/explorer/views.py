import os
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from Bio import SeqIO

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

def get_cluster_size(target_id, filepath):
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
            return str(record.seq)
    return None

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

    # Get the cluster size
    cluster_size = get_cluster_size(id, cluster_filepath)

    # Fetch the sequence from the FASTA file
    sequence = get_sequence_from_fasta(id, fasta_filepath)

    return render(request, 'explorer/details.html', {
        'id': id, 
        'cluster_size': cluster_size,
        'sequence': sequence
    })

def cluster_reps(request):
    base_dir = "../data/"

    # Read the cluster rep names from the file
    with open(os.path.join(base_dir, 'rep_names.txt'), 'r') as f:
        rep_names = f.readlines()

    return render(request, 'explorer/cluster_reps.html', {'rep_names': rep_names})
