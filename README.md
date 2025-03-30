# RO-Crate Datasheet Generator

A template-based tool for generating HTML datasheets from RO-Crate metadata.

## Installation

1. Clone this repository
2. Install requirements:

```bash
pip install -r requirements.txt
```

## Usage

### Command-line

Generate a datasheet from a RO-Crate metadata file:

```bash
python generate_datasheet.py --input /path/to/ro-crate-metadata.json
```

### Python API

```python
from rocrate.datasheet_generator import DatasheetGenerator

# Create a generator from a JSON file
generator = DatasheetGenerator(json_path="/path/to/ro-crate-metadata.json")

# Process subcrates
generator.process_subcrates()

# Generate and save the datasheet
output_path = generator.save_datasheet("output.html")
```

## License

MIT
