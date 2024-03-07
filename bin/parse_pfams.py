import argparse
import configparser
import psycopg2
import csv
import pandas as pd
import os

def read_config(filename='bin/db_config.ini'):
    config = configparser.ConfigParser()
    config.read(filename)
    return dict(config.items('database'))

def execute_query(cursor, b_value, out_dir):
    sql_query = f"SELECT name FROM sequence_explorer_biome WHERE id = {b_value}"
    cursor.execute(sql_query)
    result = cursor.fetchall()
    return(result)

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

def query_sequence_explorer_pfam(cursor, counts_dir, out_dir): # TODO
    files = os.listdir(counts_dir)
    for file_name in files:
        file_path = os.path.join(counts_dir, file_name)
        df = pd.read_csv(file_path)
        biome_names = []
        parent_names = []
        file_name = file_name.replace("mgnifam", "mgnfam")
        with open(os.path.join(out_dir, file_name), 'w') as out_file:
            out_file.write("ids,labels,parents,counts\n")
            for index, row in df.iterrows():
                b_value = row['b_value']
                result = execute_query(cursor, b_value, out_dir)
                biome_name = result[0][0]
                parent_name = get_parent(biome_name)
                label = get_label(biome_name)
                biome_names.append(biome_name)
                parent_names.append(parent_name)
                out_file.write(f"{biome_name},{label},{parent_name},{row['count']}\n")
            
            append_parents(parent_names, biome_names, out_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query a PostgreSQL database and parse biome ids into sunburst format.")
    parser.add_argument("config_file", help="Path to the configuration file for the database secrets")
    parser.add_argument("counts_dir", help="Path to the folder with biomes ids and counts per family")
    parser.add_argument("out_dir", help="Path to the results directory")
    # python3 bin/parse_biome_sunburst.py bin/db_config.ini data/biome_sunburst/tmp/ data/biome_sunburst/result/
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    db_params = read_config(args.config_file)
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    
    query_sequence_explorer_pfam(cursor, args.counts_dir, args.out_dir)

    cursor.close()
    conn.close()
