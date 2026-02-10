"""Json2Class generator module

This module inspects a JSON structure and generates equivalent Python
dataclasses that mirror the JSON schema. The generator:

- Infers Python types for JSON values (primitives, lists, nested objects).
- Creates nested dataclasses for JSON objects and reuses types when
    structures match (deduplication based on keys+value types).
- Emits dataclasses with a `to_dict()` helper and a `__post_init__`
    that converts nested dicts/lists into the corresponding dataclass
    instances at runtime.

Usage (from project root):

        python src/generator.py path/to/input.json

The generated file is written to `src/generated_class.py` by default.
"""

import json
import os
import sys
import hashlib
from typing import Any, Dict, List, Union, Optional

def to_pascal_case(text: str) -> str:
    """
    Converts a string to PascalCase.
    
    Handles both snake_case (e.g., 'my_variable') and camelCase (e.g., 'myVariable').
    
    Args:
        text (str): The input string.
        
    Returns:
        str: The string converted to PascalCase.
    """
    if '_' in text:
        return ''.join(x.title() for x in text.split('_'))
    return text[0].upper() + text[1:]

def get_singular_name(name: str) -> str:
    """
    Simple heuristic to singularize a word.
    
    Currently just removes the trailing 's' if present.
    
    Args:
        name (str): The plural name.
        
    Returns:
        str: The singularized name.
    """
    if name.endswith('s'):
        return name[:-1]
    return name

def infer_type(value: Any, classes: Dict[str, str], structure_map: Dict[str, str], name_counts: Dict[str, int], field_name: str = None) -> str:
    """
    Infers the Python type string for a given JSON value and handles nested class generation.

    This function recursively determines the type of a value. If the value is a dictionary,
    it generates a new class (or reuses an existing one) and returns the class name.
    
    Args:
        value (Any): The value to infer the type for.
        classes (Dict[str, str]): A dictionary accumulating the generated class code (name -> code).
        structure_map (Dict[str, str]): A map of {sorted_keys_string -> class_name} to detect duplicate structures.
        name_counts (Dict[str, int]): A counter to handle name collisions (e.g., Telemetry, Telemetry2).
        field_name (str, optional): The name of the field this value belongs to. Used for naming generated classes.

    Returns:
        str: The Python type string (e.g., 'int', 'List[str]', 'MyClass').
    """
    # Primitive types
    if isinstance(value, bool):
        return 'bool'
    elif isinstance(value, int):
        return 'int'
    elif isinstance(value, float):
        return 'float'
    elif isinstance(value, str):
        return 'str'
    elif value is None:
        return 'Optional[Any]'
    elif isinstance(value, list):
        if not value:
            return 'List[Any]'
        
        # Determine singular name for items (used for naming item classes)
        item_name = None
        if field_name:
            item_name = get_singular_name(field_name)
            
        # Collect all unique types in the list
        types = set()
        for item in value:
            types.add(infer_type(item, classes, structure_map, name_counts, field_name=item_name))
        
        if len(types) == 1:
            return f'List[{list(types)[0]}]'
        else:
            union_types = ' | '.join(sorted(types))
            return f'List[{union_types}]'
    elif isinstance(value, dict):
        # For object values, derive a signature based on the keys and the
        # types of their values (not the concrete values). This lets us
        # deduplicate classes that share the same structure but different
        # data.
        structure_sig = json.dumps(
            {k: type(v).__name__ for k, v in sorted(value.items())},
            sort_keys=True,
        )
        dict_hash = hashlib.md5(structure_sig.encode()).hexdigest()[:8]

        # Reuse class name if this structural signature was already seen
        if dict_hash in structure_map:
            return structure_map[dict_hash]

        # Derive a human-friendly base name from the field name if present
        base_name = "GeneratedClass"
        if field_name:
            base_name = to_pascal_case(field_name)
            if base_name and base_name[0].islower():
                base_name = base_name[0].upper() + base_name[1:]

        # Ensure uniqueness against already used class names
        class_name = base_name
        counter = 0
        original_base = base_name
        while class_name in classes or class_name in name_counts:
            counter += 1
            class_name = f"{original_base}{counter}"

        # Register the structural signature before generating the body to
        # correctly handle recursive structures.
        structure_map[dict_hash] = class_name
        if class_name not in name_counts:
            name_counts[class_name] = 0

        classes[class_name] = generate_class(value, class_name, classes, structure_map, name_counts)
        return class_name
    else:
        return 'Any'

def generate_class(json_data: Dict[str, Any], class_name: str, classes: Dict[str, str], structure_map: Dict[str, str], name_counts: Dict[str, int]) -> str:
    """
    Generates the Python code for a dataclass based on a JSON dictionary.

    Iterates through the dictionary keys to define fields and their types.
    Also adds a `to_dict` method to the generated class for serialization.
    Includes __post_init__ to convert nested dicts to class instances.

    Args:
        json_data (Dict[str, Any]): The JSON data defining the class structure.
        class_name (str): The name of the class to generate.
        classes (Dict[str, str]): Dictionary to store generated class code.
        structure_map (Dict[str, str]): Map for structural deduplication.
        name_counts (Dict[str, int]): Counter for name collision resolution.

    Returns:
        str: The complete Python code string for the generated class.
    """
    fields = []
    post_init_conversions = []
    
    for key, value in json_data.items():
        typ = infer_type(value, classes, structure_map, name_counts, field_name=key)
        default_str = ""
        if isinstance(value, (str, int, float, bool)):
            default_str = f" = {repr(value)}"
        elif isinstance(value, list):
            if value:
                # For lists, store raw data as default and convert in __post_init__
                default_str = f" = field(default_factory=lambda: {repr(value)})"
                # Extract item class name from List[ClassName]
                if isinstance(value[0], dict):
                    item_type = typ[5:-1] if typ.startswith('List[') else 'dict'
                    post_init_conversions.append((key, item_type, True))  # True = is_list
            else:
                default_str = " = field(default_factory=list)"
        elif isinstance(value, dict):
            # For nested objects, store raw data as default and convert in __post_init__
            sub_class_name = infer_type(value, classes, structure_map, name_counts, field_name=key)
            default_str = f" = field(default_factory=lambda: {repr(value)})"
            post_init_conversions.append((key, sub_class_name, False))  # False = not is_list
        elif value is None:
            default_str = " = None"
        
        if 'Optional' in typ or typ == 'Any':
            typ = f'Optional[{typ}]'
        fields.append(f'    {key}: {typ}{default_str}')
    
    # Build __post_init__ method if needed
    post_init_code = ""
    if post_init_conversions:
        post_init_lines = ["    def __post_init__(self) -> None:"]
        for field_name, nested_class_name, is_list in post_init_conversions:
            if is_list:
                post_init_lines.append(f"        if isinstance(self.{field_name}, list) and self.{field_name} and isinstance(self.{field_name}[0], dict):")
                post_init_lines.append(f"            self.{field_name} = [{nested_class_name}(**item) for item in self.{field_name}]")
            else:
                post_init_lines.append(f"        if isinstance(self.{field_name}, dict):")
                post_init_lines.append(f"            self.{field_name} = {nested_class_name}(**self.{field_name})")
        post_init_code = "\n" + "\n".join(post_init_lines)
    
    class_code = f'''@dataclass(slots=True)
class {class_name}:
{chr(10).join(fields)}{post_init_code}

    def to_dict(self) -> Dict[str, Any]:
        result = dict()
        for key in self.__dataclass_fields__:
            value = getattr(self, key)
            if isinstance(value, list):
                result[key] = [item.to_dict() if hasattr(item, 'to_dict') else item for item in value]
            elif hasattr(value, 'to_dict'):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result
'''
    return class_code

def main(input_json_path: str = None):
    """
    Main execution entry point.

    1. Determines input JSON path (arg or default).
    2. Loads JSON data.
    3. Generates the 'Root' class and all dependency classes.
    4. Writes the result to 'generated_class.py'.

    Args:
        input_json_path (str, optional): Path to the input JSON file.
    """
    if input_json_path is None:
        if len(sys.argv) > 1:
            input_json_path = sys.argv[1]
        else:
            input_json_path = os.path.join(os.path.dirname(__file__), '..', 'default.json')
    
    output_path = os.path.join(os.path.dirname(__file__), 'generated_class.py')
    
    try:
        with open(input_json_path, 'r') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {input_json_path}")
        return

    classes = {}
    structure_map = {} # Maps dict_key -> class_name
    name_counts = {}   # Maps base_name -> count
    
    # Generate root class
    # Derive class name from filename
    filename = os.path.basename(input_json_path)
    filename_no_ext = os.path.splitext(filename)[0]
    main_class_name = to_pascal_case(filename_no_ext)
    
    main_class = generate_class(json_data, main_class_name, classes, structure_map, name_counts)
    
    # Combine all classes
    all_code = 'from __future__ import annotations\n\nfrom dataclasses import dataclass, field\nfrom typing import Any, Dict, List, Optional\n\n'
    
    # Sort classes to ensure definition order (children before parents usually not strictly required in Python if using strings, 
    # but here we are not using string forward refs in type hints for the most part, except we might need to.
    # However, the current implementation puts main class at the end and deps in `classes`.
    # `classes` will contain all nested classes.
    
    for class_name, class_code in classes.items():
        all_code += class_code + '\n'
    all_code += main_class
    
    with open(output_path, 'w') as f:
        f.write(all_code)
    
    print(f'Class generated successfully at {output_path}!')

if __name__ == '__main__':
    main()