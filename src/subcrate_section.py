import os
from collections import Counter
from html_builder import find_root_node, categorize_items, load_subcrate_data

def generate_subcrate_summary(subcrate_json, base_dir, metadata_path, parent_root=None):
    """Generate a summary of a subcrate with enhanced fields
    
    Parameters:
    - subcrate_json: The JSON data of the subcrate
    - base_dir: Base directory path
    - metadata_path: Path to the metadata file
    - parent_root: The root node of the parent crate to inherit values from if missing
    """
    if not subcrate_json:
        return "<p>Error loading subcrate data.</p>"
    
    graph = subcrate_json.get("@graph", [])
    root = find_root_node(graph)
    files, software, computations, schemas, other = categorize_items(graph, root)
    
    # Get additional information for the header
    name = root.get("name", "Untitled Subcrate")
    description = root.get("description", "")
    authors = root.get("author", "")
    keywords = root.get("keywords", [])
    if isinstance(keywords, list):
        keywords_str = ", ".join(keywords)
    else:
        keywords_str = str(keywords)
    
    # Get format summaries
    file_formats = get_formats_summary(files)
    software_formats = get_formats_summary(software)
    file_access = get_access_summary(files)
    software_access = get_access_summary(software)
    
    rocrate_id = root.get("@id", "")
    
    doi = root.get("doi", "")
    if not doi and parent_root:
        doi = parent_root.get("doi", "")
    doi_display = doi if doi else "None"
    
    date = root.get("datePublished", "")
    if not date and parent_root:
        date = parent_root.get("datePublished", "")
    date_display = date if date else "Not specified"
    
    size = root.get("contentSize", "")
    size_display = size if size else "Unknown"
    
    contact_email = root.get("contactEmail", "")
    if not contact_email and parent_root:
        contact_email = parent_root.get("contactEmail", "")
    contact_display = contact_email if contact_email else "Not specified"
    
    license_value = root.get("license", "")
    if not license_value and parent_root:
        license_value = parent_root.get("license", "")
    
    confidentiality = root.get("confidentialityLevel", "")
    if not confidentiality and parent_root:
        confidentiality = parent_root.get("confidentialityLevel", "")
    confidentiality_display = confidentiality if confidentiality else "Not specified"
    
    # Related publications handling with fallback to parent
    related_pubs = root.get("relatedPublications", [])
    if not related_pubs:
        # Try associatedPublication as a fallback
        associated_pub = root.get("associatedPublication", "")
        if associated_pub:
            if isinstance(associated_pub, str):
                related_pubs = [associated_pub]
        elif parent_root:
            # If still no publications, try parent's publications
            related_pubs = parent_root.get("relatedPublications", [])
            if not related_pubs:
                associated_pub = parent_root.get("associatedPublication", "")
                if associated_pub and isinstance(associated_pub, str):
                    related_pubs = [associated_pub]
    
    subcrate_html = f"""
    <div class="subcrate-summary">
        <h3 class="subcrate-title">{name}</h3>
        <div class="subcrate-metadata">
            <div class="metadata-item">
                <span class="metadata-label">ROCrate ID:</span>
                <span class="metadata-value">{rocrate_id}</span>
            </div>
            <div class="metadata-item">
                <span class="metadata-label">Description:</span>
                <span class="metadata-value">{description}</span>
            </div>
            <div class="metadata-item">
                <span class="metadata-label">Authors:</span>
                <span class="metadata-value">{authors}</span>
            </div>
            <div class="metadata-item">
                <span class="metadata-label">Date:</span>
                <span class="metadata-value">{date_display}</span>
            </div>
            <div class="metadata-item">
                <span class="metadata-label">Size:</span>
                <span class="metadata-value">{size_display}</span>
            </div>
            <div class="metadata-item">
                <span class="metadata-label">DOI:</span>
                <span class="metadata-value">{doi_display}</span>
            </div>
            <div class="metadata-item">
                <span class="metadata-label">Contact:</span>
                <span class="metadata-value">{contact_display}</span>
            </div>
            <div class="metadata-item">
                <span class="metadata-label">License:</span>
                <span class="metadata-value">{license_value}</span>
            </div>
            <div class="metadata-item">
                <span class="metadata-label">Confidentiality:</span>
                <span class="metadata-value">{confidentiality_display}</span>
            </div>
            <div class="metadata-item">
                <span class="metadata-label">Keywords:</span>
                <span class="metadata-value">{keywords_str}</span>
            </div>
    """

    # Related publications
    if related_pubs:
        subcrate_html += """
            <div class="metadata-item">
                <span class="metadata-label">Related Publications:</span>
                <span class="metadata-value">
                    <ul>
        """
        for pub in related_pubs:
            subcrate_html += f"""<li>{pub}</li>"""
        
        subcrate_html += """
                    </ul>
                </span>
            </div>
        """

    # Access information
    access_info = ""
    for access_type, count in file_access.items():
        access_info += f"{access_type}: {count}, "
    access_info = access_info.rstrip(", ")
    
    subcrate_html += f"""
            <div class="metadata-item">
                <span class="metadata-label">Access:</span>
                <span class="metadata-value">{access_info}</span>
            </div>
        </div>
        
        <div class="subcrate-composition">
            <h4>Content Summary</h4>
            <div class="composition-grid">
                <div class="composition-card">
                    <div class="card-header">
                        <span class="card-icon">📊</span>
                        <span class="card-title">Files ({len(files)})</span>
                    </div>
                    <div class="card-content">
                        <div class="card-stats">
                            <div class="stat-item">
                                <span class="stat-label">Formats:</span>
                                <span class="stat-value">{', '.join(f'{fmt} ({count})' for fmt, count in file_formats.items())}</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Access:</span>
                                <span class="stat-value">{', '.join(f'{acc} ({count})' for acc, count in file_access.items())}</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="composition-card">
                    <div class="card-header">
                        <span class="card-icon">💻</span>
                        <span class="card-title">Software ({len(software)})</span>
                    </div>
                    <div class="card-content">
                        <div class="card-stats">
                            <div class="stat-item">
                                <span class="stat-label">Formats:</span>
                                <span class="stat-value">{', '.join(f'{fmt} ({count})' for fmt, count in software_formats.items())}</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Access:</span>
                                <span class="stat-value">{', '.join(f'{acc} ({count})' for acc, count in software_access.items())}</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="composition-card">
                    <div class="card-header">
                        <span class="card-icon">⚙️</span>
                        <span class="card-title">Other Components</span>
                    </div>
                    <div class="card-content">
                        <div class="card-stats">
                            <div class="stat-item">
                                <span class="stat-label">Computations:</span>
                                <span class="stat-value">{len(computations)}</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Schemas:</span>
                                <span class="stat-value">{len(schemas)}</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Other:</span>
                                <span class="stat-value">{len(other)}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="view-full-link">
            <a href="{os.path.dirname(metadata_path)}/ro-crate-preview.html">View Full Subcrate Details</a>
        </div>
    </div>
    """
    
    return subcrate_html

def generate_subcrates_summary(subcrates, base_dir, parent_root=None):
    """Generate a summary view of all subcrates
    
    Parameters:
    - subcrates: List of subcrate info dictionaries
    - base_dir: Base directory path
    - parent_root: The root node of the parent crate to inherit values from if missing
    """
    summary_html = "<div class='subcrates-container'>"
    
    for subcrate in subcrates:
        name = subcrate.get("name", "Unnamed Sub-Crate")
        metadata_path = subcrate.get("metadata_path", "")
        
        # Load the subcrate data
        subcrate_json = load_subcrate_data(metadata_path, base_dir)
        if not subcrate_json:
            summary_html += f"""
            <div class='subcrate-error'>
                <h3>{name}</h3>
                <p>Error loading subcrate data.</p>
            </div>
            """
            continue
        
        # Add the subcrate summary
        summary_html += generate_subcrate_summary(subcrate_json, base_dir, metadata_path, parent_root)
    
    summary_html += "</div>"
    return summary_html

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