import json
import os
import sys
from datetime import datetime

from html_builder import (
    find_root_node,
    find_subcrates,
    categorize_items,
    get_common_styles,
    get_property_value
)
from file_section import generate_file_section_summary
from software_section import generate_software_section_summary
from schema_section import generate_schema_section_summary
from distribution_section import generate_distribution_section
from use_cases_section import generate_use_cases_section
from subcrate_section import generate_subcrates_summary, load_subcrate_data

def rocrate_datasheet_view(json_data, base_dir):
    """Generate a comprehensive datasheet view HTML for an RO-Crate and all its subcrates"""
    graph = json_data.get("@graph", [])
    root = find_root_node(graph)
    
    title = root.get("name", "Untitled RO-Crate")
    description = root.get("description", "")
    id_value = root.get("@id", "")
    doi = root.get("doi", "")
    license_value = root.get("license", "")
    
    release_date = root.get("datePublished", "")
    created_date = root.get("dateCreated", datetime.now().strftime("%Y-%m-%d"))
    updated_date = root.get("dateModified", "")
    
    # Find sub-crates
    subcrates = find_subcrates(graph, root)
    subcrate_count = len(subcrates)
    
    # Get the additional properties
    authors = root.get("author", "")
    publisher = root.get("publisher", "")
    principal_investigator = root.get("principalInvestigator", "")
    contact_email = root.get("contactEmail", "")
    confidentiality_level = root.get("confidentialityLevel", "")
    citation = root.get("citation", "")
    version = root.get("version", "")
    
    # Extract additionalProperty array if it exists
    additional_properties = root.get("additionalProperty", [])
    
    # Get related publications
    related_publications = root.get("relatedPublications", [])
    if related_publications and isinstance(related_publications, list):
        related_publications_html = "<ul class='publications-list'>"
        for pub in related_publications:
            related_publications_html += f"<li>{pub}</li>"
        related_publications_html += "</ul>"
    else:
        related_publications_html = ""
    
    keywords = root.get("keywords", [])
    if isinstance(keywords, list):
        keywords = ", ".join(keywords)
    
    # Added fields
    content_size = root.get("contentSize", "")
    human_subject = get_property_value(root, "Human Subject", additional_properties)
    completeness = get_property_value(root, "Completeness", additional_properties)
    funding = root.get("funder", "")
    
    # Generate the composition summary
    files, software, computations, schemas, other = categorize_items(graph, root)
    
    # Calculate values in advance instead of using format()
    files_count = len(files)
    software_count = len(software)
    computations_count = len(computations)
    schemas_count = len(schemas)
    
    # Generate section summaries
    file_section = generate_file_section_summary(files)
    software_section = generate_software_section_summary(software)
    schema_section = generate_schema_section_summary(schemas)
    distribution_section = generate_distribution_section(root)
    use_cases_section = generate_use_cases_section(root, additional_properties)
    subcrates_summary = generate_subcrates_summary(subcrates, base_dir, root)
    
    # Create the HTML template with values already inserted
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - RO-Crate Datasheet</title>
<style>
    {get_common_styles()}
</style>
</head>
<body>
    <div class="container">
        <header>
            <h1 id="project-title">{title}</h1>
            <div>Version: {version}</div>
        </header>

        <div class="summary-section">
            <h2>Release Overview</h2>
            <div class="summary-row">
                <div class="summary-label">ROCrate ID</div>
                <div class="summary-value" id="accession">{id_value}</div>
            </div>
            <div class="summary-row">
                <div class="summary-label">DOI</div>
                <div class="summary-value" id="doi"><a href="{doi}" target="_blank">{doi}</a></div>
            </div>
            <div class="summary-row">
                <div class="summary-label">Release Date</div>
                <div class="summary-value" id="release-date">{release_date}</div>
            </div>
            <div class="summary-row">
                <div class="summary-label">Size</div>
                <div class="summary-value" id="content-size">{content_size}</div>
            </div>
            <div class="summary-row">
                <div class="summary-label">Description</div>
                <div class="summary-value" id="description">{description}</div>
            </div>
            <div class="summary-row">
                <div class="summary-label">Authors</div>
                <div class="summary-value" id="authors">{authors}</div>
            </div>
            <div class="summary-row">
                <div class="summary-label">Publisher</div>
                <div class="summary-value" id="publisher">{publisher}</div>
            </div>
            <div class="summary-row">
                <div class="summary-label">Principal Investigator</div>
                <div class="summary-value" id="principal-investigator">{principal_investigator}</div>
            </div>
            <div class="summary-row">
                <div class="summary-label">Contact Email</div>
                <div class="summary-value" id="contact-email">{contact_email}</div>
            </div>
            <div class="summary-row">
                <div class="summary-label">License</div>
                <div class="summary-value" id="license"><a href="{license_value}" target="_blank">{license_value}</a></div>
            </div>
            <div class="summary-row">
                <div class="summary-label">Confidentiality Level</div>
                <div class="summary-value" id="confidentiality-level">{confidentiality_level}</div>
            </div>
            <div class="summary-row">
                <div class="summary-label">Keywords</div>
                <div class="summary-value" id="keywords">{keywords}</div>
            </div>
            <div class="summary-row">
                <div class="summary-label">Citation</div>
                <div class="summary-value" id="citation">{citation}</div>
            </div>
            <div class="summary-row">
                <div class="summary-label">Human Subject Data</div>
                <div class="summary-value" id="human-subject">{human_subject}</div>
            </div>
            <div class="summary-row">
                <div class="summary-label">Funding</div>
                <div class="summary-value" id="funding">{funding}</div>
            </div>
            <div class="summary-row">
                <div class="summary-label">Completeness</div>
                <div class="summary-value" id="completeness">{completeness}</div>
            </div>

            <div class="summary-row">
                <div class="summary-label">Related Publications</div>
                <div class="summary-value" id="related-publications">{related_publications_html}</div>
            </div>
        </div>
        
        {use_cases_section}
        
        <div class="section-header">
            <h2>Composition (Sub-Crates {subcrate_count})</h2>
        </div>
        
        {subcrates_summary}
        
        {distribution_section}

    </div>
</body>
</html>'''
    
    return html

def process_subcrates(subcrates, base_dir):
    """Process all sub-crates and generate HTML files in their respective directories"""
    for subcrate in subcrates:
        metadata_path = subcrate.get("metadata_path", "")
        
        if not metadata_path:
            continue
            
        # Get the absolute path to the metadata file
        full_path = os.path.join(base_dir, metadata_path)
        if not os.path.exists(full_path):
            continue
            
        try:
            # Load and process the sub-crate
            with open(full_path, 'r', encoding='utf-8') as f:
                subcrate_json = json.load(f)
                
            # Generate HTML for this sub-crate
            subcrate_html = rocrate_to_html(subcrate_json)
            
            # Save the HTML in the same directory as the metadata file
            subcrate_dir = os.path.dirname(full_path)
            output_file = os.path.join(subcrate_dir, "ro-crate-preview.html")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(subcrate_html)
                
        except Exception as e:
            print(f"Error processing sub-crate {subcrate.get('name', '')}: {str(e)}")

def rocrate_to_html(json_data):
    """Placeholder for the actual HTML preview generation function"""
    return "<html><body><h1>RO-Crate Preview</h1><p>This is a placeholder. Implement actual functionality here.</p></body></html>"