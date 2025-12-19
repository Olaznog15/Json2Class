import json
import os
import sys
from typing import Any, Dict, List, Union, Optional
from collections import defaultdict

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
        
        # Determine singular name for items
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
        # Generate a unique nested class based on structure
        dict_key = str(sorted(value.keys()))
        
        if dict_key in structure_map:
            return structure_map[dict_key]
        
        # Determine new class name
        base_name = "GeneratedClass"
        if field_name:
            base_name = to_pascal_case(field_name)
            # Handle cases where field name might be camelCase already
            if base_name[0].islower():
                 base_name = base_name[0].upper() + base_name[1:]
        
        # Ensure uniqueness
        class_name = base_name
        if class_name in classes or class_name in name_counts:
            name_counts[class_name] = name_counts.get(class_name, 0) + 1
            class_name = f"{base_name}{name_counts[base_name]}"
        
        # Register before generating to handle recursion (though JSON is usually a tree)
        structure_map[dict_key] = class_name
        name_counts[class_name] = 0 # Initialize count
        
        classes[class_name] = generate_class(value, class_name, classes, structure_map, name_counts)
        return class_name
    else:
        return 'Any'

def generate_class(json_data: Dict[str, Any], class_name: str, classes: Dict[str, str], structure_map: Dict[str, str], name_counts: Dict[str, int]) -> str:
    """
    Generates the Python code for a dataclass based on a JSON dictionary.

    Iterates through the dictionary keys to define fields and their types.
    Also adds a `to_dict` method to the generated class for serialization.

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
    for key, value in json_data.items():
        typ = infer_type(value, classes, structure_map, name_counts, field_name=key)
        default_str = ""
        if isinstance(value, (str, int, float, bool)):
            default_str = f" = {repr(value)}"
        elif isinstance(value, list):
            if value:
                default_str = f" = field(default_factory=lambda: {repr(value)})"
            else:
                default_str = " = field(default_factory=list)"
        elif isinstance(value, dict):
            # For nested objects, create default instance
            sub_class_name = infer_type(value, classes, structure_map, name_counts, field_name=key)
            default_str = f" = field(default_factory=lambda: {sub_class_name}())"
        elif value is None:
            default_str = " = None"
        
        if 'Optional' in typ or typ == 'Any':
            typ = f'Optional[{typ}]'
        fields.append(f'    {key}: {typ}{default_str}')
    
    class_code = f'''@dataclass(slots=True)
class {class_name}:
{chr(10).join(fields)}

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
    all_code = 'from dataclasses import dataclass, field\nfrom typing import Any, Dict, List, Optional\n\n'
    
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