def generate_distribution_section(root):
    """Generate a distribution section based on metadata"""
    license_value = root.get("license", "")
    publisher = root.get("publisher", "")
    host = root.get("distributionHost", "")
    doi = root.get("doi", "")
    release_date = root.get("datePublished", "")
    version = root.get("version", "")
    
    distribution_html = """
    <div class="section-header">
        <h2>Distribution Information</h2>
    </div>
    <div class="distribution-section">
    """
    
    if publisher:
        distribution_html += f"""
        <div class="distribution-item">
            <div class="distribution-label">Publisher:</div>
            <div class="distribution-value">{publisher}</div>
        </div>
        """
    
    if host:
        distribution_html += f"""
        <div class="distribution-item">
            <div class="distribution-label">Distribution Host:</div>
            <div class="distribution-value">{host}</div>
        </div>
        """
    
    if license_value:
        distribution_html += f"""
        <div class="distribution-item">
            <div class="distribution-label">License:</div>
            <div class="distribution-value"><a href="{license_value}" target="_blank">{license_value}</a></div>
        </div>
        """
    
    if doi:
        distribution_html += f"""
        <div class="distribution-item">
            <div class="distribution-label">DOI:</div>
            <div class="distribution-value"><a href="{doi}" target="_blank">{doi}</a></div>
        </div>
        """
    
    if release_date:
        distribution_html += f"""
        <div class="distribution-item">
            <div class="distribution-label">Release Date:</div>
            <div class="distribution-value">{release_date}</div>
        </div>
        """
    
    if version:
        distribution_html += f"""
        <div class="distribution-item">
            <div class="distribution-label">Version:</div>
            <div class="distribution-value">{version}</div>
        </div>
        """
    
    distribution_html += """
    </div>
    """
    
    return distribution_html