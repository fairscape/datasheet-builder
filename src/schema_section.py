def generate_schema_section_summary(schemas):
    """Generate a summary of schema information"""
    if not schemas:
        return "<p>No schemas found.</p>"
    
    summary_html = f"""
    <div class="section-summary">
        <h4>Schema Summary ({len(schemas)} items)</h4>
        <div class="summary-grid">
            <div class="summary-item">
                <div class="summary-label">Schema Names:</div>
                <div class="summary-value">
                    <ul>
                        {''.join(f'<li>{schema.get("name", "Unnamed Schema")}</li>' for schema in schemas[:5])}
                        {f'<li>... and {len(schemas) - 5} more</li>' if len(schemas) > 5 else ''}
                    </ul>
                </div>
            </div>
        </div>
    </div>
    """
    
    return summary_html