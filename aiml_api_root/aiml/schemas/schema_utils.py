import logging
from pathlib import Path
from typing import Optional, Dict
import json

current_dir = Path(__file__).parent


def get_schema_file(schema_file_name: str) -> Optional[str]:
    """
    reads and returns the schema file as a str. 
    returns: json schema as str
    None: if exception
    """
    schema_file = f"{current_dir}/{schema_file_name}"
    try:
        return Path(schema_file).read_text()
    except FileNotFoundError as f:
        logging.error(f"Schema file - {schema_file} not found")
        return None
    except IOError as e:
        logging.error(f"Schema file - {schema_file} cannot be read due to {e}")
        return None


def get_json_schema_file(schema_file_name: str) -> Optional[Dict]:
    """
    reads and returns the schema file as a dict. 
    returns: json schema as dict
    None: if exception
    """
    schema = get_schema_file(schema_file_name)
    if schema:
        try:
            return json.loads(schema)
        except TypeError:
            logging.error(f"Schema file - {schema_file_name} not a valid json")
    return None
