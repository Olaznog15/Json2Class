import json
import os
import sys
from typing import Any, Dict, List, Union, Optional
from collections import defaultdict

def infer_type(value: Any, class_name: str = "Root", classes: Dict[str, str] = None, class_counter: Dict[str, int] = None) -> str:
    """
    Infers the Python type string for a given JSON value.

    Args:
        value (Any): The value from the JSON data to infer the type for.
        class_name (str, optional): The base name for generated classes. Defaults to "Root".
        classes (Dict[str, str], optional): A dictionary to store generated class code. Defaults to None.
        class_counter (Dict[str, int], optional): A counter to ensure unique class names for nested objects. Defaults to None.

    Returns:
        str: The Python type string (e.g., 'int', 'str', 'List[int]', 'MyClassSub0').
    """
    if classes is None:
        classes = {}
    if class_counter is None:
        class_counter = {}
    
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
        # Collect all unique types in the list
        types = set()
        for item in value:
            types.add(infer_type(item, class_name, classes, class_counter))
        if len(types) == 1:
            return f'List[{list(types)[0]}]'
        else:
            union_types = ' | '.join(sorted(types))
            return f'List[{union_types}]'
    elif isinstance(value, dict):
        # Generate a unique nested class based on structure
        dict_key = str(sorted(value.keys()))  # Simple hash based on keys
        if dict_key not in class_counter:
            class_counter[dict_key] = len(class_counter)
        sub_class_name = f"{class_name}Sub{class_counter[dict_key]}"
        if sub_class_name not in classes:
            classes[sub_class_name] = generate_class(value, sub_class_name, classes, class_counter)
        return sub_class_name
    else:
        return 'Any'

def generate_class(json_data: Dict[str, Any], class_name: str, classes: Dict[str, str] = None, class_counter: Dict[str, int] = None, defaults: Dict[str, Any] = None) -> str:
    """
    Generates the Python code for a dataclass based on a JSON dictionary.

    Args:
        json_data (Dict[str, Any]): The JSON dictionary defining the class structure.
        class_name (str): The name of the class to generate.
        classes (Dict[str, str], optional): A dictionary to store generated class code. Defaults to None.
        class_counter (Dict[str, int], optional): A counter for unique nested class names. Defaults to None.
        defaults (Dict[str, Any], optional): Default values for fields (not currently used extensively but kept for signature). Defaults to None.

    Returns:
        str: The complete Python code string for the generated class.
    """
    if classes is None:
        classes = {}
    if class_counter is None:
        class_counter = {}
    if defaults is None:
        defaults = {}
    
    fields = []
    for key, value in json_data.items():
        typ = infer_type(value, class_name, classes, class_counter)
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
            sub_class_name = infer_type(value, class_name, classes, class_counter)
            default_str = f" = field(default_factory=lambda: {sub_class_name}())"
        elif value is None:
            default_str = " = None"
        
        if 'Optional' in typ or typ == 'Any':
            typ = f'Optional[{typ}]'
        fields.append(f'    {key}: {typ}{default_str}')
    
    imports = ""
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
    Main function to execute the class generation process.

    Args:
        input_json_path (str, optional): Path to the input JSON file. 
                                         If None, tries to read from command line args or defaults to '../default.json'.
    """
    if input_json_path is None:
        if len(sys.argv) > 1:
            input_json_path = sys.argv[1]
        else:
            input_json_path = os.path.join(os.path.dirname(__file__), '..', 'default.json')
    
    output_path = os.path.join(os.path.dirname(__file__), 'generated_class.py')
    
    with open(input_json_path, 'r') as f:
        json_data = json.load(f)
    
    classes = {}
    class_counter = {}
    main_class = generate_class(json_data, 'DefaultClass', classes, class_counter)
    
    # Combine all classes
    all_code = 'from dataclasses import dataclass, field\nfrom typing import Any, Dict, List, Optional\n\n'
    for class_code in classes.values():
        all_code += class_code + '\n'
    all_code += main_class
    
    with open(output_path, 'w') as f:
        f.write(all_code)
    
    print('Class generated successfully!')

if __name__ == '__main__':
    main()