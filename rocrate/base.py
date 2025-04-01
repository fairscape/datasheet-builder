from collections import Counter
import json
import os


class ROCrateProcessor:
    """Base class for processing RO-Crate data"""
    
    def __init__(self, json_data=None, json_path=None):
        """Initialize with either JSON data or a path to a JSON file"""
        if json_data:
            self.json_data = json_data
        elif json_path:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.json_data = json.load(f)
        else:
            raise ValueError("Either json_data or json_path must be provided")
        
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
        
        # If no clear root found, use the first non-metadata item
        for item in self.graph:
            if "@id" in item and not item["@id"].endswith("metadata.json"):
                return item
        
        # Fallback
        return self.graph[0] if self.graph else {}
    
    def find_subcrates(self):
        """Find sub-crates referenced in the RO-Crate"""
        subcrates = []
        
        # Extract sub-crate references from the graph
        for item in self.graph:
            if "@type" in item and item != self.root:
                item_types = item["@type"] if isinstance(item["@type"], list) else [item["@type"]]
                
                # Check if this is a sub-crate (Dataset + ROCrate type)
                if ("Dataset" in item_types and "https://w3id.org/EVI#ROCrate" in item_types) or "ROCrate" in item_types:
                    # If it has a ro-crate-metadata path, it's a sub-crate
                    if "ro-crate-metadata" in item:
                        subcrates.append({
                            "id": item.get("@id", ""),
                            "name": item.get("name", "Unnamed Sub-Crate"),
                            "description": item.get("description", ""),
                            "metadata_path": item.get("ro-crate-metadata", "")
                        })
        
        return subcrates
    
    def categorize_items(self):
        """Categorize items in a graph into files, software, and computations"""
        files = []
        software = []
        computations = []
        schemas = []
        other = []
        
        for item in self.graph:
            if "@type" not in item:
                continue
                
            item_types = item["@type"] if isinstance(item["@type"], list) else [item["@type"]]
            
            if item == self.root or (item.get("@id", "").endswith("metadata.json")):
                continue
                
            # Skip items that are identified as subcrates
            if "ro-crate-metadata" in item:
                continue
            
            # Categorize by type
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
    
    def get_formats_summary(self, items):
        """Get a summary of formats in a list of items"""
        formats = [item.get("format", "unknown") for item in items]
        format_counter = Counter(formats)
        return format_counter
    
    def get_access_summary(self, items):
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
    
    def get_date_range(self, items):
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
    
    def get_property_value(self, property_name, additional_properties=None):
        """Get a property value from root or from additionalProperty if present"""
        # First, check if the property exists directly in the root object
        if property_name in self.root:
            return self.root[property_name]
        
        # If additionalProperty is provided, check in there
        if additional_properties is None:
            additional_properties = self.root.get("additionalProperty", [])
            
        for prop in additional_properties:
            if prop.get("name") == property_name:
                return prop.get("value", "")
        
        return ""