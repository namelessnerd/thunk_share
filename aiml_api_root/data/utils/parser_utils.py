import re
from dataclasses import dataclass, field, is_dataclass, asdict
from typing import Any, Type, TypeVar, Dict, List



"""
Given an name in camel case, converts to snake case.
"""
def camel_to_snake(name: str) -> str:
    """
    Convert camelCase to snake_case.
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

"""
Given a name in snake case, converts to camel case
"""
def snake_to_camel(name: str) -> str:
    """
    Convert snake_case to camelCase.
    """
    components = name.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

"""
Given a dictionary and a data class, recursively goes through the dictionary to populate and 
return the data class.

For example, given

@dataclass
class Job:
    title: str
    dept: str

@dataclass
class Person:
    name: str
    age: int
    job: Job
    model_of_car: Optional[str] = None

d = {
    "name": "Alice",
    "age": 20,
    "job": {
        "title": "Test dummy",
        "dept": "universal"
    },
    "modelOfCar": "Delorean"
}

returns
Person(name='Alice', age=20, job=Job(title='Test dummy', dept='universal'), model_of_car='Delorean')
  
"""

T = TypeVar('T')


def from_dict(data_class: Type[T], data: Dict[str, Any]) -> T:
    """
    Create an instance of a data class from a dictionary, converting camelCase keys to snake_case.
    """
    # Create a dictionary for initialization, converting nested dictionaries recursively
    init_args = {}
    for field_name, field_type in data_class.__annotations__.items():
        # Convert the snake_case field name to camelCase to match with the JSON keys
        json_key = snake_to_camel(field_name)
        if json_key in data:
            field_value = data[json_key]
            if isinstance(field_value, dict) and field_type != dict:
                # Recursively convert dictionaries to data class instances
                sub_data_class = field_type.__args__[0] if hasattr(field_type, '__args__') else field_type

                init_args[field_name] = from_dict(sub_data_class, field_value)
            elif isinstance(field_value, list) and len(field_value) > 0 and hasattr(field_type, '__args__'):
                # Recursively convert lists of dictionaries
                sub_data_class = field_type.__args__[0]  # Get the expected type of list elements

    # Check if the list is expected to contain dictionaries
                if issubclass(sub_data_class, dict):  # Ensure the type is a dictionary
                    init_args[field_name] = [from_dict(sub_data_class, item)
                                             if isinstance(item, dict) else item
                                             for item in field_value]
            else:
                init_args[field_name] = field_value
    return data_class(**init_args)
