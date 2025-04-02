#!/usr/bin/env python3
import json
import os
from datetime import datetime
from collections import Counter

class ROCratePreviewGenerator:
    """Generator for RO-Crate preview HTML using the old visual style"""
    
    def __init__(self, json_data=None, json_path=None):
        """Initialize with JSON data or a path to a JSON file"""
        if json_path:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.json_data = json.load(f)
            self.base_dir = os.path.dirname(os.path.abspath(json_path))
        else:
            self.json_data = json_data
            self.base_dir = os.getcwd()
        
        self.graph = self.json_data.get("@graph", [])
        self.root = self.find_root_node()
        
    def find_root_node(self):
        """Find the root node in the RO-Crate graph"""
        for item in self.graph:
            if "@type" in item:
                if isinstance(item["@type"], list) and "Dataset" in item["@type"] and "https://w3id.org/EVI#ROCrate" in item["@type"]:
                    return item
                elif item["@type"] == "Dataset" or "ROCrate" in item["@type"]:
                    return item
        
        for item in self.graph:
            if "@id" in item and not item["@id"].endswith("metadata.json"):
                return item
        
        return self.graph[0] if self.graph else {}
    
    def categorize_items(self):
        """Categorize items in the graph"""
        datasets = []
        software = []
        computations = []
        
        for item in self.graph:
            if "@type" not in item:
                continue
                
            item_types = item["@type"] if isinstance(item["@type"], list) else [item["@type"]]
            
            if item == self.root or (item.get("@id", "").endswith("metadata.json")):
                continue
            
            if "Dataset" in item_types or "EVI:Dataset" in item_types or "https://w3id.org/EVI#Dataset" in item_types or item.get("metadataType") == "https://w3id.org/EVI#Dataset" or item.get("additionalType") == "Dataset":
                datasets.append(item)
            elif "SoftwareSourceCode" in item_types or "EVI:Software" in item_types or "Software" in item_types or "https://w3id.org/EVI#Software" in item_types or item.get("metadataType") == "https://w3id.org/EVI#Software" or item.get("additionalType") == "Software":
                software.append(item)
            elif "Computation" in item_types or "https://w3id.org/EVI#Computation" in item_types or item.get("metadataType") == "https://w3id.org/EVI#Computation" or item.get("additionalType") == "Computation":
                computations.append(item)
        
        return datasets, software, computations
    
    def generate_dataset_rows(self, datasets):
        """Generate HTML table rows for datasets"""
        rows = ""
        for dataset in datasets:
            name = dataset.get("name", "")
            description = dataset.get("description", "")
            
            description_display = description
            if len(description) > 100:
                description_display = description[:100] + "..."
            
            date = dataset.get("datePublished", "")
            if not date:
                date = dataset.get("dateCreated", "")
                if not date:
                    date = dataset.get("date", "")
            
            content_url = dataset.get("contentUrl", "")
            if isinstance(content_url, list):
                content_url = content_url[0]
            if content_url == "Embargoed":
                content_status = "Embargoed"
            elif content_url:
                content_status = f"<a href='{content_url}'>Download</a>"
            else:
                content_status = "No link"
            
            rows += f"""
            <tr>
                <td>{name}</td>
                <td title="{description}">{description_display}</td>
                <td>{content_status}</td>
                <td>{date}</td>
            </tr>
            """
        return rows
    
    def generate_software_rows(self, software_items):
        """Generate HTML table rows for software items"""
        rows = ""
        for item in software_items:
            name = item.get("name", "")
            description = item.get("description", "")
            
            description_display = description
            if len(description) > 100:
                description_display = description[:100] + "..."
            
            date = item.get("datePublished", "")
            if not date:
                date = item.get("dateModified", "")
                if not date:
                    date = item.get("dateCreated", "")
                    if not date:
                        date = item.get("date", "")
            
            content_url = item.get("contentUrl", "")
            if isinstance(content_url, list):
                content_url = content_url[0]
            if content_url == "Embargoed":
                content_status = "Embargoed"
            elif content_url:
                content_status = f"<a href='{content_url}'>Download</a>"
            else:
                content_status = "No link"
            
            rows += f"""
            <tr>
                <td>{name}</td>
                <td title="{description}">{description_display}</td>
                <td>{content_status}</td>
                <td>{date}</td>
            </tr>
            """
        return rows
    
    def generate_computation_rows(self, computations):
        """Generate HTML table rows for computations"""
        rows = ""
        for comp in computations:
            name = comp.get("name", "")
            description = comp.get("description", "")
            
            description_display = description
            if len(description) > 100:
                description_display = description[:100] + "..."
            
            date = comp.get("dateCreated", "")
            if not date:
                date = comp.get("date", "")
            
            content_url = comp.get("contentUrl", "")
            if isinstance(content_url, list):
                content_url = content_url[0]
            if content_url == "Embargoed":
                content_status = "Embargoed"
            elif content_url:
                content_status = f"<a href='{content_url}'>Download</a>"
            else:
                content_status = "No link"
            
            rows += f"""
            <tr>
                <td>{name}</td>
                <td title="{description}">{description_display}</td>
                <td>{content_status}</td>
                <td>{date}</td>
            </tr>
            """
        return rows
    
    def generate_preview_html(self):
        """Generate RO-Crate preview HTML with the old visual style"""
        # Extract basic metadata
        title = self.root.get("name", "Untitled RO-Crate")
        description = self.root.get("description", "")
        id_value = self.root.get("@id", "")
        doi = self.root.get("doi", "")
        license_value = self.root.get("license", "")
        
        release_date = self.root.get("datePublished", "")
        if not release_date and "hasPart" in self.root:
            for part_ref in self.root["hasPart"]:
                part_id = part_ref.get("@id", "")
                for item in self.graph:
                    if item.get("@id") == part_id and "datePublished" in item:
                        release_date = item["datePublished"]
                        break
                if release_date:
                    break
        
        created_date = self.root.get("dateCreated", datetime.now().strftime("%Y-%m-%d"))
        updated_date = self.root.get("dateModified", "")
        
        # Additional metadata
        authors = self.root.get("author", "")
        publisher = self.root.get("publisher", "")
        principal_investigator = self.root.get("principalInvestigator", "")
        contact_email = self.root.get("contactEmail", "")
        confidentiality_level = self.root.get("confidentialityLevel", "")
        citation = self.root.get("citation", "")
        version = self.root.get("version", "")
        
        # Related publications
        related_publications = self.root.get("relatedPublications", [])
        if not related_publications:
            related_publications = self.root.get("associatedPublication", [])
            
        if related_publications and isinstance(related_publications, list):
            related_publications_html = "<ul class='publications-list'>"
            for pub in related_publications:
                related_publications_html += f"<li>{pub}</li>"
            related_publications_html += "</ul>"
        else:
            related_publications_html = ""
        
        # Keywords
        keywords = self.root.get("keywords", [])
        if isinstance(keywords, list):
            keywords = ", ".join(keywords)
        
        # Categorize items
        datasets, software, computations = self.categorize_items()
        
        # Generate table rows
        dataset_rows = self.generate_dataset_rows(datasets)
        software_rows = self.generate_software_rows(software)
        computation_rows = self.generate_computation_rows(computations)
        
        # Count items
        dataset_count = len(datasets)
        software_count = len(software)
        computation_count = len(computations)
        
        # Create conditional HTML elements
        doi_html = f'<a href="{doi}" target="_blank">{doi}</a>' if doi else ""
        
        release_date_html = ""
        if release_date:
            release_date_html = f'''
            <div class="summary-row">
                <div class="summary-label">Release Date</div>
                <div class="summary-value" id="release-date">{release_date}</div>
            </div>'''
        
        description_html = ""
        if description:
            description_html = f'''
            <div class="summary-row">
                <div class="summary-label">Description</div>
                <div class="summary-value" id="description">{description}</div>
            </div>'''
        
        authors_html = ""
        if authors:
            authors_html = f'''
            <div class="summary-row">
                <div class="summary-label">Authors</div>
                <div class="summary-value" id="authors">{authors}</div>
            </div>'''
        
        publisher_html = ""
        if publisher:
            publisher_html = f'''
            <div class="summary-row">
                <div class="summary-label">Publisher</div>
                <div class="summary-value" id="publisher">{publisher}</div>
            </div>'''
        
        principal_investigator_html = ""
        if principal_investigator:
            principal_investigator_html = f'''
            <div class="summary-row">
                <div class="summary-label">Principal Investigator</div>
                <div class="summary-value" id="principal-investigator">{principal_investigator}</div>
            </div>'''
        
        contact_email_html = ""
        if contact_email:
            contact_email_html = f'''
            <div class="summary-row">
                <div class="summary-label">Contact Email</div>
                <div class="summary-value" id="contact-email">{contact_email}</div>
            </div>'''
        
        license_html = ""
        if license_value:
            license_html = f'''
            <div class="summary-row">
                <div class="summary-label">License</div>
                <div class="summary-value" id="license"><a href="{license_value}" target="_blank">{license_value}</a></div>
            </div>'''
        
        confidentiality_level_html = ""
        if confidentiality_level:
            confidentiality_level_html = f'''
            <div class="summary-row">
                <div class="summary-label">Confidentiality Level</div>
                <div class="summary-value" id="confidentiality-level">{confidentiality_level}</div>
            </div>'''
        
        keywords_html = ""
        if keywords:
            keywords_html = f'''
            <div class="summary-row">
                <div class="summary-label">Keywords</div>
                <div class="summary-value" id="keywords">{keywords}</div>
            </div>'''
        
        citation_html = ""
        if citation:
            citation_html = f'''
            <div class="summary-row">
                <div class="summary-label">Citation</div>
                <div class="summary-value" id="citation">{citation}</div>
            </div>'''
        
        related_publications_row_html = ""
        if related_publications_html:
            related_publications_row_html = f'''
            <div class="summary-row">
                <div class="summary-label">Related Publications</div>
                <div class="summary-value" id="related-publications">{related_publications_html}</div>
            </div>'''
        
        # Create the HTML template with values already inserted
        html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - RO-Crate Preview</title>
    <style>
        body {{
            font-family: 'Helvetica', 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            color: #333;
            line-height: 1.5;
        }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 20px;
        }}
        header {{
            margin-bottom: 20px;
            border-bottom: 2px solid #2c3e50;
            padding-bottom: 15px;
        }}
        h1 {{
            font-size: 24px;
            margin-bottom: 5px;
            color: #2c3e50;
        }}
        .summary-section {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 4px;
            margin-bottom: 30px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
            page-break-inside: avoid;
        }}
        .summary-row {{
            display: flex;
            margin-bottom: 12px;
            border-bottom: 1px solid #eee;
            padding-bottom: 8px;
        }}
        .summary-label {{
            width: 220px;
            font-weight: bold;
            color: #2c3e50;
        }}
        .summary-value {{
            flex: 1;
        }}
        .tabs {{
            display: flex;
            border-bottom: 1px solid #ddd;
            margin-bottom: 20px;
        }}
        .tab {{
            padding: 12px 15px;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            font-weight: bold;
            color: #2c3e50;
        }}
        .tab.active {{
            border-bottom: 3px solid #2c3e50;
        }}
        .tab .badge {{
            display: inline-block;
            background-color: #2c3e50;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 12px;
            margin-left: 5px;
        }}
        .tab-content {{
            margin-bottom: 30px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        }}
        th, td {{
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid #eaeaea;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: bold;
            color: #2c3e50;
            border-bottom: 2px solid #ddd;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        tr:hover {{
            background-color: #f1f8fe;
        }}
        .publications-list {{
            margin-top: 5px;
            padding-left: 15px;
        }}
        .publications-list li {{
            margin-bottom: 8px;
        }}
        @media print {{
            body {{
                font-size: 11pt;
            }}
            .container {{
                max-width: 100%;
                padding: 10px;
            }}
            table {{
                border: 1px solid #ddd;
            }}
            th, td {{
                border: 1px solid #ddd;
            }}
            .tab-content {{
                display: block !important;
            }}
            .tabs {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1 id="project-title">{title}</h1>
            <div>Version: {version}</div>
        </header>

        <div class="summary-section">
            <div class="summary-row">
                <div class="summary-label">ROCrate ID</div>
                <div class="summary-value" id="accession">{id}</div>
            </div>
            <div class="summary-row">
                <div class="summary-label">DOI</div>
                <div class="summary-value" id="doi">{doi_html}</div>
            </div>
            {release_date_html}
            {description_html}
            {authors_html}
            {publisher_html}
            {principal_investigator_html}
            {contact_email_html}
            {license_html}
            {confidentiality_level_html}
            {keywords_html}
            {citation_html}
            {related_publications_row_html}
        </div>

        <div class="tabs">
            <div class="tab active" data-tab="datasets">Datasets <span class="badge">{dataset_count}</span></div>
            <div class="tab" data-tab="software">Software <span class="badge">{software_count}</span></div>
            <div class="tab" data-tab="computations">Computations <span class="badge">{computation_count}</span></div>
        </div>

        <div id="datasets-content" class="tab-content">
            <table id="datasets-table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Description</th>
                        <th>Access</th>
                        <th>Release Date</th>
                    </tr>
                </thead>
                <tbody id="datasets-body">
                    {dataset_rows}
                </tbody>
            </table>
        </div>

        <div id="software-content" class="tab-content" style="display: none;">
            <table id="software-table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Description</th>
                        <th>Access</th>
                        <th>Release Date</th>
                    </tr>
                </thead>
                <tbody id="software-body">
                    {software_rows}
                </tbody>
            </table>
        </div>

        <div id="computations-content" class="tab-content" style="display: none;">
            <table id="computations-table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Description</th>
                        <th>Access</th>
                        <th>Date Created</th>
                    </tr>
                </thead>
                <tbody id="computations-body">
                    {computation_rows}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // Minimal JavaScript for tab switching functionality
        document.addEventListener('DOMContentLoaded', function() {{
            const tabs = document.querySelectorAll('.tab');
            
            tabs.forEach(tab => {{
                tab.addEventListener('click', function() {{
                    // Remove active class from all tabs
                    tabs.forEach(t => t.classList.remove('active'));
                    
                    // Add active class to clicked tab
                    this.classList.add('active');
                    
                    // Hide all tab content
                    document.querySelectorAll('.tab-content').forEach(content => {{
                        content.style.display = 'none';
                    }});
                    
                    // Show corresponding tab content
                    const tabId = this.getAttribute('data-tab');
                    document.getElementById(`${{tabId}}-content`).style.display = 'block';
                }});
            }});
        }});
    </script>
</body>
</html>
'''
        
        # Format the HTML with the data
        html = html_template.format(
            title=title,
            id=id_value,
            doi_html=doi_html,
            description_html=description_html,
            release_date_html=release_date_html,
            created_date=created_date,
            updated_date=updated_date,
            authors_html=authors_html,
            publisher_html=publisher_html,
            principal_investigator_html=principal_investigator_html,
            contact_email_html=contact_email_html,
            license_html=license_html,
            confidentiality_level_html=confidentiality_level_html,
            keywords_html=keywords_html,
            citation_html=citation_html,
            related_publications_row_html=related_publications_row_html,
            dataset_count=dataset_count,
            software_count=software_count,
            computation_count=computation_count,
            dataset_rows=dataset_rows,
            software_rows=software_rows,
            computation_rows=computation_rows,
            version=version
        )
        
        return html
    
    def save_preview_html(self, output_path=None):
        """Generate and save the RO-Crate preview HTML to a file"""
        if output_path is None:
            output_path = os.path.join(self.base_dir, "ro-crate-preview.html")
        
        html_content = self.generate_preview_html()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path