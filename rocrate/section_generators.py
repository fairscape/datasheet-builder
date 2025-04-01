from .base import ROCrateProcessor
import os

class SectionGenerator:
    def __init__(self, template_engine, processor=None):
        self.template_engine = template_engine
        self.processor = processor
    
    def generate(self, template_name, **context):
        return self.template_engine.render(template_name, **context)


class OverviewSectionGenerator(SectionGenerator):
    def generate(self, processor=None):
        if processor:
            self.processor = processor
        
        if not self.processor:
            raise ValueError("Processor is required to generate the overview section")
        
        root = self.processor.root
        additional_properties = root.get("additionalProperty", [])
        
        context = {
            'title': root.get("name", "Untitled RO-Crate"),
            'description': root.get("description", ""),
            'id_value': root.get("@id", ""),
            'doi': root.get("identifier", ""),
            'license_value': root.get("license", ""),
            'release_date': root.get("datePublished", ""),
            'created_date': root.get("dateCreated", ""),
            'updated_date': root.get("dateModified", ""),
            'authors': root.get("author", ""),
            'publisher': root.get("publisher", ""),
            'principal_investigator': root.get("principalInvestigator", ""),
            'contact_email': root.get("contactEmail", ""),
            'confidentiality_level': root.get("confidentialityLevel", ""),
            'citation': root.get("citation", ""),
            'version': root.get("version", ""),
            'content_size': root.get("contentSize", ""),
            'human_subject': self.processor.get_property_value("Human Subject", additional_properties),
            'completeness': self.processor.get_property_value("Completeness", additional_properties),
            'funding': root.get("funder", ""),
            'keywords': root.get("keywords", [])
        }
        
        related_publications = root.get("associatedPublication", [])
        if related_publications and isinstance(related_publications, list):
            context['related_publications'] = related_publications
        else:
            context['related_publications'] = []
        
        return self.template_engine.render('sections/overview.html', **context)


class UseCasesSectionGenerator(SectionGenerator):
    def generate(self, processor=None):
        if processor:
            self.processor = processor
        
        if not self.processor:
            raise ValueError("Processor is required to generate the use cases section")
        
        root = self.processor.root
        additional_properties = root.get("additionalProperty", [])
        
        context = {
            'intended_uses': self.processor.get_property_value("Intended Use", additional_properties),
            'limitations': self.processor.get_property_value("Limitations", additional_properties),
            'prohibited_uses': self.processor.get_property_value("Prohibited Uses", additional_properties),
            'maintenance_plan': self.processor.get_property_value("Maintenance Plan", additional_properties)
        }
        
        return self.template_engine.render('sections/use_cases.html', **context)


class DistributionSectionGenerator(SectionGenerator):
    def generate(self, processor=None):
        if processor:
            self.processor = processor
        
        if not self.processor:
            raise ValueError("Processor is required to generate the distribution section")
        
        root = self.processor.root
        
        context = {
            'license_value': root.get("license", ""),
            'publisher': root.get("publisher", ""),
            'host': root.get("distributionHost", ""),
            'doi': root.get("doi", ""),
            'release_date': root.get("datePublished", ""),
            'version': root.get("version", "")
        }
        
        return self.template_engine.render('sections/distribution.html', **context)


def get_directory_size(directory):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if not os.path.islink(file_path):
                total_size += os.path.getsize(file_path)
    return total_size


def format_size(size_in_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} PB"


class SubcratesSectionGenerator(SectionGenerator):
    def generate(self, processor=None, base_dir=None):
        if processor:
            self.processor = processor
        
        if not self.processor:
            raise ValueError("Processor is required to generate the subcrates section")
        
        subcrates = self.processor.find_subcrates()
        
        processed_subcrates = []
        for subcrate_info in subcrates:
            metadata_path = subcrate_info.get("metadata_path", "")
            if not metadata_path or not base_dir:
                continue
                
            full_path = os.path.join(base_dir, metadata_path)
            if not os.path.exists(full_path):
                continue
                
            try:
                subcrate_processor = ROCrateProcessor(json_path=full_path)
                subcrate_dir = os.path.dirname(full_path)
                
                subcrate = {
                    'name': subcrate_processor.root.get("name", subcrate_info.get("name", "Unnamed Sub-Crate")),
                    'id': subcrate_processor.root.get("@id", subcrate_info.get("id", "")),
                    'description': subcrate_processor.root.get("description", subcrate_info.get("description", "")),
                    'authors': subcrate_processor.root.get("author", ""),
                    'keywords': subcrate_processor.root.get("keywords", []),
                    'metadata_path': metadata_path,
                }
                
                # Get size from metadata or calculate it from the directory
                size = subcrate_processor.root.get("contentSize", "")
                if not size and os.path.exists(subcrate_dir):
                    try:
                        dir_size = get_directory_size(subcrate_dir)
                        size = format_size(dir_size)
                    except Exception:
                        size = "Unknown"
                
                subcrate["size"] = size
                
                # Get fields with fallback to parent values if available
                subcrate['doi'] = subcrate_processor.root.get("identifier", self.processor.root.get("identifier", ""))
                subcrate['date'] = subcrate_processor.root.get("datePublished", self.processor.root.get("datePublished", ""))
                subcrate['contact'] = subcrate_processor.root.get("contactEmail", self.processor.root.get("contactEmail", ""))
                subcrate['license'] = subcrate_processor.root.get("license", self.processor.root.get("license", ""))
                subcrate['confidentiality'] = subcrate_processor.root.get("confidentialityLevel", self.processor.root.get("confidentialityLevel", ""))
                
                files, software, computations, schemas, other = subcrate_processor.categorize_items()
                subcrate['files'] = files
                subcrate['files_count'] = len(files)
                subcrate['software'] = software
                subcrate['software_count'] = len(software)
                subcrate['computations'] = computations
                subcrate['computations_count'] = len(computations)
                subcrate['schemas'] = schemas
                subcrate['schemas_count'] = len(schemas)
                subcrate['other'] = other
                subcrate['other_count'] = len(other)
                
                subcrate['file_formats'] = subcrate_processor.get_formats_summary(files)
                subcrate['software_formats'] = subcrate_processor.get_formats_summary(software)
                subcrate['file_access'] = subcrate_processor.get_access_summary(files)
                subcrate['software_access'] = subcrate_processor.get_access_summary(software)
                
                related_pubs = subcrate_processor.root.get("relatedPublications", [])
                if not related_pubs:
                    associated_pub = subcrate_processor.root.get("associatedPublication", "")
                    if associated_pub:
                        if isinstance(associated_pub, str):
                            related_pubs = [associated_pub]
                    elif self.processor.root.get("relatedPublications", []):
                        related_pubs = self.processor.root.get("relatedPublications", [])
                    elif self.processor.root.get("associatedPublication", ""):
                        associated_pub = self.processor.root.get("associatedPublication", "")
                        if associated_pub and isinstance(associated_pub, str):
                            related_pubs = [associated_pub]
                
                subcrate['related_publications'] = related_pubs
                
                processed_subcrates.append(subcrate)
                
            except Exception as e:
                continue
        
        context = {
            'subcrates': processed_subcrates,
            'subcrate_count': len(processed_subcrates)
        }
        
        return self.template_engine.render('sections/subcrates.html', **context)