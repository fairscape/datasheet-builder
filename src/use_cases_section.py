def generate_use_cases_section(root, additional_properties=None):
    """Generate a use cases and limitations section based on metadata"""
    # Extract values either directly from root or from additionalProperty
    intended_uses = get_property_value(root, "Intended Use", additional_properties)
    limitations = get_property_value(root, "Limitations", additional_properties)
    prohibited_uses = get_property_value(root, "Prohibited Uses", additional_properties)
    maintenance_plan = get_property_value(root, "Maintenance Plan", additional_properties)
    
    # Generate the HTML
    section_html = """
    <div class="section-header">
        <h2>Use Cases and Limitations</h2>
    </div>
    <div class="use-cases-section">
    """
    
    if intended_uses:
        section_html += f"""
        <div class="use-cases-item">
            <div class="use-cases-label">Intended Uses:</div>
            <div class="use-cases-value">{intended_uses}</div>
        </div>
        """
    
    if limitations:
        section_html += f"""
        <div class="use-cases-item">
            <div class="use-cases-label">Limitations:</div>
            <div class="use-cases-value">{limitations}</div>
        </div>
        """
    
    if prohibited_uses:
        section_html += f"""
        <div class="use-cases-item">
            <div class="use-cases-label">Prohibited Uses:</div>
            <div class="use-cases-value">{prohibited_uses}</div>
        </div>
        """
    
    if maintenance_plan:
        section_html += f"""
        <div class="use-cases-item">
            <div class="use-cases-label">Maintenance Plan:</div>
            <div class="use-cases-value">{maintenance_plan}</div>
        </div>
        """
    
    section_html += """
    </div>
    """
    
    return section_html

def get_property_value(root, property_name, additional_properties=None):
    """Get a property value from root or from additionalProperty if present"""
    # First, check if the property exists directly in the root object
    if property_name in root:
        return root[property_name]
    
    # If additionalProperty is provided, check in there
    if additional_properties:
        for prop in additional_properties:
            if prop.get("name") == property_name:
                return prop.get("value", "")
    
    return ""