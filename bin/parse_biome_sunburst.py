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

def execute_query(cursor, b_value):
    sql_query = f"SELECT name FROM sequence_explorer_biome WHERE id = {b_value}"
    cursor.execute(sql_query)
    result = cursor.fetchall()
    return(result)

def get_parent(biome_path):
    parts = biome_path.split(':')
    if len(parts) <= 1:
        return ''
    parent = ':'.join(parts[:-1])
    return parent

def get_label(biome_path):
    parts = biome_path.split(':')
    if len(parts) == 0:
        return ''  # No label found
    return parts[-1]

def append_parents(parent_names, biome_names, out_file):
    if ('root' not in biome_names):
        out_file.write("root,root,,0\n")
        biome_names.append("root")
    for parent_name in parent_names:
        while parent_name not in biome_names and parent_name != '':
            biome_names.append(parent_name)
            grandparent_name = get_parent(parent_name)
            label = get_label(parent_name)
            out_file.write(f"{parent_name},{label},{grandparent_name},0\n")
            parent_name = grandparent_name

def query_sequence_explorer_biome(cursor, counts_dir, out_dir):
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
                result = execute_query(cursor, b_value)
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
    
    query_sequence_explorer_biome(cursor, args.counts_dir, args.out_dir)

    cursor.close()
    conn.close()
