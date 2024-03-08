import argparse
import configparser
import psycopg2
import csv
import pandas as pd
import os
import ast

def read_config(filename='bin/db_config.ini'):
    config = configparser.ConfigParser()
    config.read(filename)
    return dict(config.items('database'))

def execute_query(cursor, pfam_id):
    sql_query = f"SELECT name FROM sequence_explorer_pfam WHERE id = {pfam_id}"
    cursor.execute(sql_query)
    result = cursor.fetchall()
    return(result)

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

        # Print the sorted arrays
        print("Family Names:", fam_names)
        print("Start Points:", start_points)

        # TODO rest for matched_rows with more than one row
        exit()

    return domain_architecture

def append_to_domain_architecture(family_domain_architectures, domain_architecture):

    return family_domain_architectures

def get_color_from_name(): #TODO
    pass

def write_out_json(): #TODO
    pass

def query_sequence_explorer_pfam(cursor, edge_list_file, read_dir, out_dir):
    clusters_df = pd.read_csv(edge_list_file, delimiter='\t', header=None, names=['family_name', 'protein_name'])

    files = os.listdir(read_dir)
    for file_name in files:
        family_name = file_name.split("_")[0]
        subset_clusters_df = get_edgelist_family_subset(clusters_df, family_name)
        file_path = os.path.join(read_dir, file_name)
        family_domain_architectures = pd.DataFrame(columns=['count', 'domain_architecture'])
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    mgyp = parts[0]
                    matched_rows = subset_clusters_df[subset_clusters_df['mgyp'] == mgyp]
                    if not matched_rows.empty:
                        pfams = parts[1]
                        domain_architecture = construct_domain_architecture(mgyp, pfams, matched_rows)
                        exit()
                        family_domain_architectures = append_to_domain_architecture(family_domain_architectures, domain_architecture)
                        
        # pfam_names = []
        # file_name = file_name.replace("mgnifam", "mgnfam")
        # print(file_name)
        # for index, row in df.iterrows():
        #     column1_value = row[0]
        #     print(column1_value)
        #     column2_value = row[1]
        #     print(column2_value)

        exit()

        # with open(os.path.join(out_dir, file_name), 'w') as out_file:
        #     out_file.write("ids,labels,parents,counts\n")
        #     for index, row in df.iterrows():
        #         b_value = row['b_value']
        #         result = execute_query(cursor, b_value)
        #         biome_name = result[0][0]
        #         parent_name = get_parent(biome_name)
        #         label = get_label(biome_name)
        #         biome_names.append(biome_name)
        #         parent_names.append(parent_name)
        #         out_file.write(f"{biome_name},{label},{parent_name},{row['count']}\n")
            
        #     append_parents(parent_names, biome_names, out_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query a PostgreSQL database and parse pfam ids into domain architecture format.")
    parser.add_argument("config_file", help="Path to the configuration file for the database secrets")
    parser.add_argument("edge_list_file", help="Path to the edge list file with two columns")
    parser.add_argument("read_dir", help="Path to the folder with pfam ids per family and sequence")
    parser.add_argument("out_dir", help="Path to the results directory")
    # python3 bin/parse_pfams.py bin/db_config.ini data/families/updated_refined_families.tsv data/pfams/tmp/ data/pfams/result/
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    db_params = read_config(args.config_file)
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    
    query_sequence_explorer_pfam(cursor, args.edge_list_file, args.read_dir, args.out_dir)

    cursor.close()
    conn.close()
