import os
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from Bio import SeqIO
import glob

def count_lines_in_file(filepath):
    with open(filepath, 'r') as f:
        return sum(1 for _ in f)

def index(request):
    base_dir = "../data/"

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

def id_exists(check_id, filepath):
    with open(filepath, 'r') as f:
        return check_id in f.read().splitlines()

def format_protein_name(raw_name):
    """
    Formats the protein name by appending zeros in front to make it 12 characters,
    and then adds 'MGYP' as a prefix.
    """
    formatted_name = raw_name.zfill(12)  # Append zeros to make it 12 characters
    return "MGYP" + formatted_name

def details(request):
    id = request.GET.get('id', None)
    base_dir = "../data/"
    id_filepath = os.path.join(base_dir, 'mgnifam_names.txt')

    # Validate if ID exists in mgnifam_names.txt
    if not id_exists(id, id_filepath):
        messages.error(request, 'Invalid ID entered. Please check and try again.')
        return redirect('index')
    # Construct the path for the cif file
    cif_directory = os.path.join(base_dir, 'cif/')
    cif_files = glob.glob(os.path.join(cif_directory, id + '_*'))
    # Extract only the filename from the first matching cif file
    cif_filename = os.path.basename(cif_files[0]) if cif_files else None
    # Check if cif file exists
    if not cif_filename:
        messages.error(request, 'No CIF file found for the given ID.')
        return redirect('index')

    filename_no_ext = cif_filename.split('.')[0]
    first_split = filename_no_ext.split('-')
    first_split_first_part = first_split[0]
    first_split_second_part = first_split[1]
    family_id = first_split_first_part.split('_')[0]
    family_size = first_split_first_part.split('_')[1]
    protein_parts = first_split_second_part.split('_')
    protein_rep = format_protein_name(protein_parts[0])
    if (len(protein_parts) == 1):
        mask = "whole MGYP protein"
    elif (len(protein_parts) == 3):
        mask = f"{protein_parts[1]}-{protein_parts[2]}"
    elif (len(protein_parts) == 5):
        mask = f"{int(protein_parts[1]) + int(protein_parts[3]) - 1}-{int(protein_parts[1]) + int(protein_parts[4]) - 1}"

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
    structure_found = False
    structural_annotations = []
    with open(foldseek_annotated_filepath, 'r') as file:
        for line in file:
            if line.startswith(family_id + '_'):
                structure_found = True
                foldseek_folder = os.path.join(base_dir, 'foldseek/')
                for filepath in glob.glob(foldseek_folder + '*'):
                    filename = os.path.basename(filepath)
                    if filename.startswith(('alphafold_', 'esm_', 'pdb_')):
                        with open(filepath, 'r') as f:
                            for file_line in f:
                                parts = file_line.strip().split('\t')
                                first_part = parts[0].split('-')[0].split('_')[0]
                                if first_part == family_id:
                                    annotation = {
                                        'target_structure_identifier': parts[1],
                                        'aligned_length': int(parts[3]),
                                        'query_start': int(parts[6]),
                                        'query_end': int(parts[7]),
                                        'target_start': int(parts[8]),
                                        'target_end': int(parts[9]),
                                        'e_value': float(parts[10])
                                    }
                                    structural_annotations.append(annotation)
                break

    return render(request, 'explorer/details.html', {
        'family_id': family_id,
        'family_size': family_size,
        'cif_path': cif_filename,  
        'protein_rep': protein_rep,
        'mask': mask,
        'hits_data': hits_data,
        'structural_annotations': structural_annotations
    })

def mgnifam_names(request):
    base_dir = "../data/"

    # Read the cluster rep names from the file
    with open(os.path.join(base_dir, 'mgnifam_names.txt'), 'r') as f:
        mgnifam_names = f.readlines()

    return render(request, 'explorer/mgnifam_names.html', {'mgnifam_names': mgnifam_names})
