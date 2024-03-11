import argparse
import configparser
import psycopg2
import os
import json

def read_config(filename='bin/db_config.ini'):
    config = configparser.ConfigParser()
    config.read(filename)
    return dict(config.items('database'))

def subset_json(json_items, threshold = 10):
    return json_items['architecture_containers'][:threshold]

def execute_pfam_translation_query(cursor, pfam_id):
    sql_query = f"SELECT name FROM sequence_explorer_pfam WHERE id = '{pfam_id}'"
    cursor.execute(sql_query)
    result = cursor.fetchall()
    return(result)

def append_link(domain):
    pass

def write_out_json(json_object, output_filename):
    final_json_object = {"architecture_containers": json_object}
    with open(output_filename, 'w') as f:
        json.dump(final_json_object, f, indent=4)

def string_to_hex_color(s):
    hash_val = 0
    for char in s:
        hash_val = ord(char) + ((hash_val << 5) - hash_val)
    
    color = '#'
    for i in range(3):
        value = (hash_val >> (i * 8)) & 0xFF
        color += ('00' + format(value, 'x'))[-2:]

    return color

def hex_to_rgb(hex_color):
    # Remove '#' from the beginning of the hex color
    hex_color = hex_color.lstrip('#')
    
    # Convert the hex color to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    return (r, g, b)

def calculate_luminosity(rgb):
    # Convert RGB to linear RGB
    def linearize(color):
        c = color / 255.0
        if c <= 0.03928:
            return c / 12.92
        return ((c + 0.055) / 1.055) ** 2.4
    
    r, g, b = rgb
    # Calculate relative luminance
    luminance = 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)
    return luminance

def decide_font_color(hex_color):
    # Convert hex color to RGB
    rgb = hex_to_rgb(hex_color)
    
    # Calculate luminosity
    luminosity = calculate_luminosity(rgb)
    
    # Decide font color based on luminosity
    if luminosity > 0.2:
        return 'black'
    else:
        return 'white'

def construct_name(mgnifam_id):
    name = mgnifam_id.replace('mgnifam', 'MGYF')
    number_str = name[4:]
    number = int(number_str)
    formatted_number = '{:010d}'.format(number)
    final_name = 'MGYF' + formatted_number
    
    return final_name

def translate_pfams(cursor, read_dir, out_dir):
    files = os.listdir(read_dir)
    for file_name in files:
        full_path = os.path.join(read_dir, file_name)
        with open(full_path, 'r') as file:
            json_data = json.load(file)
            top_10_architecture_containers = subset_json(json_data, 10)
            for architecture_container in top_10_architecture_containers:
                for domain in architecture_container['domains']:
                    if 'mgnifam' not in domain['name']:
                        domain['link'] = f'https://www.ebi.ac.uk/interpro/entry/pfam/{domain["name"]}/domain_architecture/'
                        domain['name'] = execute_pfam_translation_query(cursor, domain['name'])[0][0]
                        domain['color'] = string_to_hex_color(domain['name'])
                    else:
                        domain['link'] = f'http://127.0.0.1:8000/details/?id={construct_name(domain["name"])}' # TODO change base url
                    domain['font_color'] = decide_font_color(domain['color'])

            output_filename = os.path.join(out_dir, file_name)
            write_out_json(top_10_architecture_containers, output_filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query a PostgreSQL database and transalte pfam ids into clickable names.")
    parser.add_argument("config_file", help="Path to the configuration file for the database secrets")
    parser.add_argument("read_dir", help="Path to the folder with the domain architecture json files")
    parser.add_argument("out_dir", help="Path to the translated results directory")
    # python3 bin/translate_pfams.py bin/db_config.ini data/pfams/result/ data/pfams/translated/ 
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    db_params = read_config(args.config_file)
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    
    translate_pfams(cursor, args.read_dir, args.out_dir)

    cursor.close()
    conn.close()
