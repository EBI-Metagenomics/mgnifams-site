import argparse
import configparser
import psycopg2
import csv
import pandas as pd

def read_config(filename='bin/db_config.ini'):
    config = configparser.ConfigParser()
    config.read(filename)
    return dict(config.items('database'))

def extract_second_column(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        second_column = [line.split()[1] for line in lines]
    return second_column

def parse_edge_list_column(edge_list_column):
    parsed_items = []
    for item in edge_list_column:
        parts = item.split('/')
        if len(parts) > 1:
            first_part = parts[0].split('_')[0]
            parsed_items.append(first_part)
    return parsed_items

def query_sequence_explorer_protein(config_file, edge_list_file, output_csv):
    db_params = read_config(config_file)
    edge_list_second_column = extract_second_column(edge_list_file)
    parsed_items = parse_edge_list_column(edge_list_second_column)
    unique_parsed_items = list(set(parsed_items))

    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        sql_query = "SELECT * FROM sequence_explorer_protein WHERE mgyp IN ({})".format(
            ",".join([str(parsed_item) for parsed_item in unique_parsed_items[:60]])
        )
        cursor.execute(sql_query)
        rows = cursor.fetchall()

        with open(output_csv, 'w', newline='') as csvfile:
            fieldnames = ['mgyp', 'b_value']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            for row in rows:
                metadata = row[4]
                if 'b' in metadata:
                    mgyp = row[0]
                    b_values = metadata['b']
                    for b_value_pair in b_values:
                        first_number = b_value_pair[0]
                        writer.writerow({'mgyp': mgyp, 'b_value': first_number})


    except psycopg2.Error as e:
            print("Error executing SQL query:", e)

    except FileNotFoundError:
        print("Configuration file not found.")

    finally:
        cursor.close()
        conn.close()

def read_csv_to_dataframe(csv_file):
    df = pd.read_csv(csv_file)
    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query a PostgreSQL database and process an edge list file.")
    parser.add_argument("config_file", help="Path to the configuration file for the database secrets")
    parser.add_argument("edge_list_file", help="Path to the edge list file with two columns")
    parser.add_argument("output_csv", help="Path to the output CSV file")
    # python3 bin/get_biome_distribution.py bin/db_config.ini data/families/updated_refined_families.tsv tmp/output.csv

    args = parser.parse_args()
    query_sequence_explorer_protein(args.config_file, args.edge_list_file, args.output_csv)

    df = read_csv_to_dataframe(args.output_csv)
    b_counts = df['b_value'].value_counts()
    b_counts_df = b_counts.reset_index()
    b_counts_df.columns = ['b_value', 'count']
    print(b_counts_df) # TODO per family
