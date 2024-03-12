import argparse
import csv
import pandas as pd
import os
import ast
import json

def extract_mgyp(protein_name):
    parts = protein_name.split('/')
    if len(parts) > 1:
        first_part = parts[0].split('_')[0]
        return first_part
    elif "_" in protein_name:
        return protein_name.split('_')[0]
    return protein_name

def calculate_mgnifams_start(protein_id):
    number_of_underscores = protein_id.count('_')
    if (number_of_underscores == 0): # 250671917
        start = 1
    elif (number_of_underscores == 1): # 250671917/1_50
        parts = protein_id.split('/')
        start = parts[1].split('_')[0]
    elif (number_of_underscores == 2): # 250671917_50_150
        start = protein_id.split('_')[1]
    elif (number_of_underscores == 3): # 250671917_50_200/2_34
        start = int(protein_id.split('_')[1])
        region = protein_id.split('/')[1].split('_')
        start = start + int(region[0]) - 1

    return start

def get_edgelist_family_subset(clusters_df, family_name):
    subset_clusters_df = clusters_df[clusters_df['family_name'] == family_name].copy()
    subset_clusters_df['mgyp'] = subset_clusters_df['protein_name'].apply(extract_mgyp)
    subset_clusters_df['mgnifams_start'] = subset_clusters_df['protein_name'].apply(calculate_mgnifams_start)
    return subset_clusters_df

def construct_domain_architecture(mgyp, pfams, matched_rows):
    pfams = ast.literal_eval(pfams)
    fam_names = []
    start_points = []
    for pfam in pfams:
        fam_names.append(pfam[0])
        start_points.append(pfam[3])

    for index, row in matched_rows.iterrows():
        fam_names.append(row['family_name'])
        start_points.append(int(row['mgnifams_start']))

    # Sort both arrays based on start_points
    sorted_data = sorted(zip(start_points, fam_names))
    start_points, fam_names = zip(*sorted_data)

    domain_architecture = '\t'.join(map(str, fam_names))

    return domain_architecture

def string_to_hex_color(s):
    hash_val = 0
    for char in s:
        hash_val = ord(char) + ((hash_val << 5) - hash_val)
    
    color = '#'
    for i in range(3):
        value = (hash_val >> (i * 8)) & 0xFF
        color += ('00' + format(value, 'x'))[-2:]

    return color

def write_out_json(element_counts, output_filename):
    architecture_containers = []
    for architecture_text, count in element_counts.items():
        domains = []
        for domain in architecture_text.split('\t'):
            domains.append({"name": domain, "color": string_to_hex_color(domain)})
        architecture_containers.append({"architecture_text": str(count), "domains": domains})

    output_json = {"architecture_containers": architecture_containers}

    # Convert to JSON string
    with open(output_filename, 'w') as f:
        json.dump(output_json, f, indent=4)

def construct_pfams_json(edge_list_file, read_dir, out_dir):
    clusters_df = pd.read_csv(edge_list_file, delimiter='\t', header=None, names=['family_name', 'protein_name'])

    files = os.listdir(read_dir)
    for file_name in files:
        print(file_name)
        family_name = file_name.split("_")[0]
        subset_clusters_df = get_edgelist_family_subset(clusters_df, family_name)
        file_path = os.path.join(read_dir, file_name)
        family_domain_architectures = []
        counter = 0
        with open(file_path, 'r') as file:
            for line in file:
                if counter % 1000 == 0:
                    print(counter)
                # if counter == 10:
                #     break
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    mgyp = parts[0]
                    matched_rows = subset_clusters_df[subset_clusters_df['mgyp'] == mgyp]
                    if not matched_rows.empty:
                        pfams = parts[1]
                        domain_architecture = construct_domain_architecture(mgyp, pfams, matched_rows)
                        family_domain_architectures.append(domain_architecture)
                counter += 1

        element_counts = pd.Series(family_domain_architectures).value_counts()
        family_name = family_name.replace("mgnifam", "mgnfam")
        output_filename = os.path.join(out_dir, f"{family_name}_domains.json")
        write_out_json(element_counts, output_filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query a PostgreSQL database and parse pfam ids into domain architecture format.")
    parser.add_argument("edge_list_file", help="Path to the edge list file with two columns")
    parser.add_argument("read_dir", help="Path to the folder with pfam ids per family and sequence")
    parser.add_argument("out_dir", help="Path to the results directory")
    # python3 bin/parse_pfams.py data/families/updated_refined_families.tsv data/pfams/tmp/ data/pfams/result/
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    construct_pfams_json(args.edge_list_file, args.read_dir, args.out_dir)
