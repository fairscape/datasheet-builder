import json
import argparse
import os
import sys
import traceback

from main_datasheet import rocrate_datasheet_view, process_subcrates
from use_cases_section import generate_use_cases_section
from html_builder import find_root_node, find_subcrates

def main():
    parser = argparse.ArgumentParser(description='Generate RO-Crate datasheets and previews with support for sub-crates')
    parser.add_argument('--input', required=True, help='Path to top-level ro-crate-metadata.json file')
    
    args = parser.parse_args()
    
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        base_dir = os.path.dirname(args.input)
        
        graph = json_data.get("@graph", [])
        root = find_root_node(graph)
        subcrates = find_subcrates(graph, root)
        
        process_subcrates(subcrates, base_dir)
        
        datasheet_html = rocrate_datasheet_view(json_data, base_dir)
        datasheet_output = os.path.join(base_dir, "ro-crate-datasheet.html")
        with open(datasheet_output, 'w', encoding='utf-8') as f:
            f.write(datasheet_html)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())