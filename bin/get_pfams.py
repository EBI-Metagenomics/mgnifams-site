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

def extract_mgyp(protein_name):
    parts = protein_name.split('/')
    if len(parts) > 1:
        first_part = parts[0].split('_')[0]
        return first_part
    elif "_" in protein_name:
        return protein_name.split('_')[0]
    return protein_name

def execute_query(cursor, query_items, result_dir):
    col1 = query_items[0][0]  # Get col1 from the first item
    output_csv = f"{result_dir}/{col1}_output.tsv"

    unique_col2_values = list(set(item[1] for item in query_items))
    sql_query = "SELECT mgyp, metadata FROM sequence_explorer_protein WHERE mgyp IN ({})".format(
        ",".join([f"'{col2}'" for col2 in unique_col2_values])
    )
    print(sql_query)
    cursor.execute(sql_query)
    rows = cursor.fetchall()

    with open(output_csv, 'w') as file:
        for row in rows:
            metadata = row[1]
            if 'p' in metadata:
                mgyp = row[0]
                file.write(f"{mgyp}\t{metadata['p']}\n")

def is_above_family_id(fam_name, above_family_id):
    fam_id = fam_name.replace("mgnifam", "")
    fam_id = float(fam_id)

    if fam_id > int(above_family_id):
        return True
    else:
        return False

def query_sequence_explorer_protein(cursor, edge_list_file, above_family_id, result_dir):
    with open(edge_list_file, 'r') as file:
        previous_col1 = None
        query_items = []
        for line in file:
            col1, col2 = line.strip().split('\t')
            if (is_above_family_id(col1, above_family_id)):
                if col1 != previous_col1:
                    if query_items:  # Execute previous query if items exist
                        execute_query(cursor, query_items, result_dir)
                    query_items = []
                    previous_col1 = col1
                parsed_col2 = extract_mgyp(col2)
                query_items.append((col1, parsed_col2))

        # Execute the last query
        if query_items:
            execute_query(cursor, query_items, result_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query a PostgreSQL database and process an edge list file.")
    parser.add_argument("config_file", help="Path to the configuration file for the database secrets")
    parser.add_argument("edge_list_file", help="Path to the edge list file with two columns")
    parser.add_argument("above_family_id", help="Threshold for family id, to not recalculate same ones")
    parser.add_argument("result_dir", help="Path to the result directory")
    # python3 bin/get_pfams.py bin/db_config.ini data/families/updated_refined_families.tsv 52 data/pfams/tmp
    args = parser.parse_args()

    os.makedirs(args.result_dir, exist_ok=True)

    db_params = read_config(args.config_file)
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    query_sequence_explorer_protein(cursor, args.edge_list_file, args.above_family_id, args.result_dir)

    cursor.close()
    conn.close()
