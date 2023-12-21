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
    cif_files = glob.glob(os.path.join(cif_directory, id + '*'))
    
    # Extract only the filename from the first matching cif file
    cif_filename = os.path.basename(cif_files[0]) if cif_files else None

    # Check if cif file exists
    if not cif_filename:
        messages.error(request, 'No CIF file found for the given ID.')
        return redirect('index')

    return render(request, 'explorer/details.html', {
        'id': id,
        'cif_path': cif_filename  # Updated to use just the filename
    })

def mgnifam_names(request):
    base_dir = "../data/"

    # Read the cluster rep names from the file
    with open(os.path.join(base_dir, 'mgnifam_names.txt'), 'r') as f:
        mgnifam_names = f.readlines()

    return render(request, 'explorer/mgnifam_names.html', {'mgnifam_names': mgnifam_names})
