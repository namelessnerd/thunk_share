import os
from typing import Type, TypeVar


T = TypeVar('T') 

def getenv(env_variable: str, return_type: Type[T], default: T = None) -> T:
    """
    A utility function to retrieve environment variables and cast them to a specific data type.

    :param env_variable: The name of the environment variable to retrieve.
    :param return_type: The expected type of the environment variable's value.
    :param default: The default value to return if the environment variable is not set (must match the return type).
    :return: The environment variable value cast to the specified type, or the default value.
    :raises ValueError: If the environment variable cannot be cast to the specified type.
    :raises KeyError: If the environment variable is not set and no default is provided.
    """
    value = os.getenv(env_variable, None)
    if value is None:
        if default is not None:
            return default
        else:
            raise KeyError(f"Environment variable '{env_variable}' is not set and no default value was provided.")
    try:
        return return_type(value)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Environment variable '{env_variable}' cannot be cast to {return_type.__name__}: {e}")
