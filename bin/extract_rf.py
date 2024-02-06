import os
import subprocess

def run_hmmbuild(msa_file, output_hmm, extra_args):                                                               
    hmmbuild_command = ["hmmbuild"] + extra_args + [output_hmm, msa_file]
    subprocess.run(hmmbuild_command, stdout=subprocess.DEVNULL)
    
def process_alignment(ms_file, output_folder, basename):
    # Extract lines starting with "#=GC RF"
    with open(ms_file, 'r') as file:
        relevant_lines = [line.strip() for line in file if line.startswith("#=GC RF")]

    # Keep only 'x's and '.'
    cleaned_lines = [''.join(filter(lambda c: c == 'x' or c == '.', line)) for line in relevant_lines]

    # Combine lines into a single sequence
    combined_sequence = ''.join(cleaned_lines)

    # Write the combined sequence to the output file
    output_file_path = os.path.join(output_folder, f'{basename}.txt')
    with open(output_file_path, 'w') as output_file:
        output_file.write(combined_sequence)

# Example usage
input_folder_path = 'data/families/seed_msa'
tmp_hmm_path = 'tmp.hmm'
tmp_ms_msa_path = 'tmp.ms'
output_folder_path = 'rf'
if not os.path.exists(output_folder_path):
    os.makedirs(output_folder_path)
output_hmm_path = os.path.join(output_folder_path, tmp_hmm_path)
output_ms_path = os.path.join(output_folder_path, tmp_ms_msa_path)

# Run hmmbuild for each MSA file in the input folder
for filename in os.listdir(input_folder_path):
    input_file_path = os.path.join(input_folder_path, filename)
    basename, _ = os.path.splitext(os.path.basename(input_file_path))
    
    # Check if the path is a file
    if os.path.isfile(input_file_path):
        # Run hmmbuild to create HMM file
        run_hmmbuild(input_file_path, output_hmm_path, ["-O", output_ms_path])

        # Process the HMM file with process_alignment
        process_alignment(output_ms_path, output_folder_path, basename)
