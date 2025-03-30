import os
import json
from collections import Counter
import datetime

def find_root_node(graph):
    """Find the root node in the RO-Crate graph (which is typically an entity of type 'Dataset' and 'ROCrate')"""
    for item in graph:
        if "@type" in item:
            if isinstance(item["@type"], list) and "Dataset" in item["@type"] and "https://w3id.org/EVI#ROCrate" in item["@type"]:
                return item
            elif item["@type"] == "Dataset" or "ROCrate" in item["@type"]:
                return item
    
    for item in graph:
        if "@id" in item and not item["@id"].endswith("metadata.json"):
            return item
    
    return graph[0]

def find_subcrates(graph, root_node):
    """
    Find sub-crates referenced in the RO-Crate
    Returns a list of sub-crate information dictionaries
    """
    subcrates = []
    
    for item in graph:
        if "@type" in item and item != root_node:
            item_types = item["@type"] if isinstance(item["@type"], list) else [item["@type"]]
            
            if ("Dataset" in item_types and "https://w3id.org/EVI#ROCrate" in item_types) or "ROCrate" in item_types:
                if "ro-crate-metadata" in item:
                    subcrates.append({
                        "id": item.get("@id", ""),
                        "name": item.get("name", "Unnamed Sub-Crate"),
                        "description": item.get("description", ""),
                        "metadata_path": item.get("ro-crate-metadata", "")
                    })
    
    return subcrates

def categorize_items(graph, root):
    """Categorize items in a graph into files, software, and computations"""
    files = []
    software = []
    computations = []
    schemas = []
    other = []
    
    for item in graph:
        if "@type" not in item:
            continue
            
        item_types = item["@type"] if isinstance(item["@type"], list) else [item["@type"]]
        
        if item == root or (item.get("@id", "").endswith("metadata.json")):
            continue
            
        if "ro-crate-metadata" in item:
            continue
        
        if "Dataset" in item_types or "EVI:Dataset" in item_types or "https://w3id.org/EVI#Dataset" in item_types or item.get("metadataType") == "https://w3id.org/EVI#Dataset" or item.get("additionalType") == "Dataset":
            files.append(item)
        elif "SoftwareSourceCode" in item_types or "EVI:Software" in item_types or "Software" in item_types or "https://w3id.org/EVI#Software" in item_types or item.get("metadataType") == "https://w3id.org/EVI#Software" or item.get("additionalType") == "Software":
            software.append(item)
        elif "Computation" in item_types or "https://w3id.org/EVI#Computation" in item_types or item.get("metadataType") == "https://w3id.org/EVI#Computation" or item.get("additionalType") == "Computation":
            computations.append(item)
        elif "Schema" in item_types or "EVI:Schema" in item_types or "https://w3id.org/EVI#Schema" in item_types:
            schemas.append(item)
        else:
            other.append(item)
    
    return files, software, computations, schemas, other

def load_subcrate_data(metadata_path, base_dir):
    """Load data from a subcrate metadata file"""
    full_path = os.path.join(base_dir, metadata_path)
    if not os.path.exists(full_path):
        return None
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            subcrate_json = json.load(f)
        return subcrate_json
    except Exception as e:
        print(f"Error loading subcrate from {full_path}: {str(e)}")
        return None

def get_formats_summary(items):
    """Get a summary of formats in a list of items"""
    formats = [item.get("format", "unknown") for item in items]
    format_counter = Counter(formats)
    return format_counter

def get_access_summary(items):
    """Get a summary of content URL types (available, embargoed, etc.)"""
    access_types = []
    for item in items:
        content_url = item.get("contentUrl", "")
        if not content_url:
            access_types.append("No link")
        elif content_url == "Embargoed":
            access_types.append("Embargoed")
        else:
            access_types.append("Available")
    
    access_counter = Counter(access_types)
    return access_counter

def get_license_summary(items):
    """Get a summary of licenses in a list of items"""
    licenses = [item.get("license", "unknown") for item in items]
    unique_licenses = list(set(licenses))
    return unique_licenses

def get_date_range(items):
    """Get the date range for a list of items"""
    dates = []
    for item in items:
        date = item.get("datePublished", "")
        if not date:
            date = item.get("dateModified", "")
            if not date:
                date = item.get("dateCreated", "")
        
        if date:
            dates.append(date)
    
    if not dates:
        return "Unknown"
    
    return f"{min(dates)} to {max(dates)}"

def get_derived_from_summary(items):
    """Get a summary of derived from relationships"""
    derived_counts = 0
    for item in items:
        if "derivedFrom" in item and item["derivedFrom"]:
            derived_counts += 1
    
    return derived_counts

def get_generated_by_summary(items):
    """Get a summary of generated by relationships"""
    generated_counts = 0
    for item in items:
        if "generatedBy" in item and item["generatedBy"]:
            generated_counts += 1
    
    return generated_counts

def get_property_value(root, property_name, additional_properties=None):
    """Get a property value from root or from additionalProperty if present"""
    if property_name in root:
        return root[property_name]
    
    if additional_properties:
        for prop in additional_properties:
            if prop.get("name") == property_name:
                return prop.get("value", "")
    
    return ""

def get_common_styles():
    """Return common CSS styles for RO-Crate datasheets"""
    return """
        body {
            font-family: 'Helvetica', 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            color: #333;
            line-height: 1.5;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1100px;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        header {
            margin-bottom: 20px;
            border-bottom: 2px solid #2c3e50;
            padding-bottom: 15px;
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
        }
        h1 {
            font-size: 24px;
            margin-bottom: 5px;
            color: #2c3e50;
        }
        h2 {
            font-size: 20px;
            color: #2c3e50;
            margin-top: 25px;
            margin-bottom: 15px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 8px;
        }
        h3 {
            font-size: 18px;
            color: #2c3e50;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        h4 {
            font-size: 16px;
            color: #2c3e50;
            margin-top: 15px;
            margin-bottom: 10px;
        }
        .summary-section {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 4px;
            margin-bottom: 30px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        }
        .summary-row {
            display: flex;
            margin-bottom: 12px;
            border-bottom: 1px solid #eee;
            padding-bottom: 8px;
        }
        .summary-label {
            width: 220px;
            font-weight: bold;
            color: #2c3e50;
        }
        .summary-value {
            flex: 1;
        }
        .section-header {
            margin: 25px 0 15px 0;
            padding-bottom: 8px;
            border-bottom: 1px solid #ddd;
            color: #2c3e50;
        }
        .composition-summary {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 20px;
        }
        .composition-item {
            background-color: #f8f9fa;
            border-radius: 4px;
            padding: 15px;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
            width: calc(20% - 20px);
            min-width: 120px;
        }
        .composition-count {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            display: block;
            margin-bottom: 5px;
        }
        .composition-label {
            color: #555;
        }
        .subcrates-container {
            margin-top: 30px;
        }
        .subcrate-summary {
            background-color: #f8f9fa;
            border-radius: 4px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        }
        .subcrate-metadata {
            margin-bottom: 15px;
        }
        .metadata-item {
            margin-bottom: 8px;
        }
        .metadata-label {
            font-weight: bold;
            color: #2c3e50;
            margin-right: 10px;
        }
        .section-summary {
            background-color: white;
            border-radius: 4px;
            padding: 15px;
            margin-top: 15px;
            margin-bottom: 15px;
            border: 1px solid #eaeaea;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
        }
        .summary-item {
            margin-bottom: 15px;
        }
        details {
            margin-top: 15px;
            border: 1px solid #eaeaea;
            border-radius: 4px;
            padding: 10px;
        }
        summary {
            font-weight: bold;
            cursor: pointer;
            padding: 5px;
            color: #2c3e50;
        }
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        .data-table th, .data-table td {
            text-align: left;
            padding: 8px;
            border-bottom: 1px solid #eaeaea;
        }
        .data-table th {
            background-color: #f8f9fa;
            font-weight: bold;
            color: #2c3e50;
        }
        .view-full-link {
            margin-top: 15px;
            text-align: right;
        }
        .view-full-link a {
            display: inline-block;
            padding: 8px 15px;
            background-color: #2c3e50;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
        }
        .view-full-link a:hover {
            background-color: #1a252f;
        }
        .distribution-section, .use-cases-section {
            background-color: #f8f9fa;
            border-radius: 4px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        }
        .distribution-item, .use-cases-item {
            margin-bottom: 12px;
            border-bottom: 1px solid #eee;
            padding-bottom: 8px;
        }
        .distribution-label, .use-cases-label {
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        .publications-list {
            margin-top: 5px;
            padding-left: 15px;
        }
        .publications-list li {
            margin-bottom: 8px;
        }
        .subcrate-error {
            background-color: #fff0f0;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
            border: 1px solid #ffcccb;
        }
        .subcrate-title {
            border-bottom: 2px solid #2c3e50;
            padding-bottom: 10px;
            margin-bottom: 15px;
            color: #2c3e50;
        }
        
        .composition-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 15px;
            margin-bottom: 15px;
        }
        
        .composition-card {
            border: 1px solid #eaeaea;
            border-radius: 5px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        }
        
        .card-header {
            background-color: #f8f9fa;
            padding: 10px 15px;
            border-bottom: 1px solid #eaeaea;
            display: flex;
            align-items: center;
        }
        
        .card-icon {
            font-size: 20px;
            margin-right: 10px;
        }
        
        .card-title {
            font-weight: bold;
            color: #2c3e50;
        }
        
        .card-content {
            padding: 15px;
        }
        
        .card-stats {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .stat-item {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        
        .stat-label {
            font-weight: bold;
            color: #555;
        }
        
        .stat-value {
            color: #333;
        }
        
        @media print {
            body {
                background-color: white;
            }
            .container {
                box-shadow: none;
                max-width: 100%;
                padding: 10px;
            }
            .view-full-link {
                display: none;
            }
            details {
                margin-bottom: 20px;
            }
            details > summary {
                list-style: none;
            }
            details > summary::marker,
            details > summary::-webkit-details-marker {
                display: none;
            }
        }
    """

def rocrate_to_html(json_data):
    """Generate an HTML preview for an RO-Crate"""
    html = "Not implemented"
    return html