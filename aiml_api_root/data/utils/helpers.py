
from typing import Any, List, Optional, Union


def safe_getattr(
    source: Any,
    attr_hierarchy: List[str]
) -> Any:
    """
    Safely retrieves a nested attribute from a source object or dictionary.

    Args:
        source (Any): The source object or dictionary from which to retrieve attributes.
        attr_hierarchy (List[str]): A list of attribute names representing the hierarchy.

    Returns:
        Any: The value of the nested attribute if it exists, otherwise the tail_default.
    """
    if source is None:
        return None
    current = source
    for attr in attr_hierarchy:
        try:
            if isinstance(current, dict):
                current = current.get(attr, None)
            else:
                current = getattr(current, attr, None)
        except AttributeError:
            return None
    return current


