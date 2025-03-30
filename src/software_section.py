from collections import Counter

def generate_software_section_summary(software):
    """Generate a summary of software information"""
    if not software:
        return "<p>No software found.</p>"
    
    formats = get_formats_summary(software)
    access = get_access_summary(software)
    date_range = get_date_range(software)
    
    summary_html = f"""
    <div class="section-summary">
        <h4>Software Summary ({len(software)} items)</h4>
        <div class="summary-grid">
            <div class="summary-item">
                <div class="summary-label">Formats:</div>
                <div class="summary-value">
                    <ul>
                        {''.join(f'<li>{fmt}: {count}</li>' for fmt, count in formats.items())}
                    </ul>
                </div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Access:</div>
                <div class="summary-value">
                    <ul>
                        {''.join(f'<li>{access_type}: {count}</li>' for access_type, count in access.items())}
                    </ul>
                </div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Date Range:</div>
                <div class="summary-value">{date_range}</div>
            </div>
        </div>
    </div>
    """
    
    # Add sample items (first 3)
    if software:
        preview_software = software[:3]
        summary_html += """
        <details>
            <summary>Sample Software</summary>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Description</th>
                        <th>Format</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for item in preview_software:
            name = item.get("name", "")
            description = item.get("description", "")
            # Truncate description if too long
            description_display = description
            if len(description) > 100:
                description_display = description[:100] + "..."
            
            format_val = item.get("format", "")
            date = item.get("dateModified", "")
            if not date:
                date = item.get("datePublished", "")
                if not date:
                    date = item.get("dateCreated", "")
            
            summary_html += f"""
            <tr>
                <td>{name}</td>
                <td title="{description}">{description_display}</td>
                <td>{format_val}</td>
                <td>{date}</td>
            </tr>
            """
        
        summary_html += """
                </tbody>
            </table>
        </details>
        """
    
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