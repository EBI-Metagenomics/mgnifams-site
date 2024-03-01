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

def query_sequence_explorer_protein(config_file, edge_list_file, tmp_dir, result_dir):
    db_params = read_config(config_file)

    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        with open(edge_list_file, 'r') as file:
            previous_col1 = None
            query_items = []
            for line in file:
                col1, col2 = line.strip().split('\t')
                if col1 != previous_col1:
                    if query_items:  # Execute previous query if items exist
                        execute_query(cursor, query_items, tmp_dir, result_dir)
                    query_items = []
                    previous_col1 = col1
                parsed_col2 = parse_col2(col2)
                query_items.append((col1, parsed_col2))

            # Execute the last query
            if query_items:
                execute_query(cursor, query_items, tmp_dir, result_dir)

    except psycopg2.Error as e:
        print("Error executing SQL query:", e)

    except FileNotFoundError:
        print("Configuration file not found.")

    finally:
        cursor.close()
        conn.close()

def execute_query(cursor, query_items, tmp_dir, result_dir):
    col1 = query_items[0][0]  # Get col1 from the first item
    output_csv = f"{tmp_dir}/{col1}_output.csv"

    unique_col2_values = list(set(item[1] for item in query_items))
    sql_query = "SELECT * FROM sequence_explorer_protein WHERE mgyp IN ({})".format(
        ",".join([f"'{col2}'" for col2 in unique_col2_values])
    )
    print(sql_query)
    cursor.execute(sql_query)
    rows = cursor.fetchall()

    with open(output_csv, 'w') as file:
        for row in rows:
            metadata = row[4]
            if 'b' in metadata:
                mgyp = row[0]
                b_values = metadata['b']
                for b_value_pair in b_values:
                    first_number = b_value_pair[0]
                    file.write(f"{mgyp},{first_number}\n")

    # Calculate and save b_counts_df for each family
    df = pd.DataFrame({'b_value': [b_value_pair[0] for row in rows for b_value_pair in row[4].get('b', [])]})
    b_counts = df['b_value'].value_counts()
    b_counts_df = b_counts.reset_index()
    b_counts_df.columns = ['b_value', 'count']
    b_counts_df.to_csv(os.path.join(result_dir, f"{col1}_b_counts.csv"), index=False)


def parse_col2(col2):
    parts = col2.split('/')
    if len(parts) > 1:
        first_part = parts[0].split('_')[0]
        return first_part
    elif "_" in col2:
        return col2.split('_')[0]
    return col2

def read_csv_to_dataframe(csv_file):
    df = pd.read_csv(csv_file)
    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query a PostgreSQL database and process an edge list file.")
    parser.add_argument("config_file", help="Path to the configuration file for the database secrets")
    parser.add_argument("edge_list_file", help="Path to the edge list file with two columns")
    parser.add_argument("tmp_dir", help="Path to the tmp directory")
    parser.add_argument("result_dir", help="Path to the result directory")
    # python3 bin/get_biome_distribution.py bin/db_config.ini data/families/updated_refined_families.tsv tmp/ results/
    args = parser.parse_args()

    os.makedirs(args.tmp_dir, exist_ok=True)
    os.makedirs(args.result_dir, exist_ok=True)

    query_sequence_explorer_protein(args.config_file, args.edge_list_file, args.tmp_dir, args.result_dir)
