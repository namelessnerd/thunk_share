
from typing import Type, Callable, Optional
from aiml.clients.ai_client import AIClient
from service_config.dao.ai_service_models import AIServiceConfig
import logging

ai_clients_registry = {}

# Decorator to register clients
def register_client(key:str)-> Callable[[Type], Type]:
    def wrapper(cls: Type) -> Type:
        ai_clients_registry[key] = cls
        return cls
    return wrapper

def get_client(key: str, srvc_model: AIServiceConfig) -> Optional[AIClient]:
    """
    Returns the client for the current key. If none found, logs errors
    and returns None
    """
    client_class = ai_clients_registry.get(key)
    if not client_class:
        logging.error(f"No AI client registered for key: {key}")
        return None
    return client_class(
        api_key=srvc_model.api_key,
        model=srvc_model.model,
        temperature=srvc_model.temperature
    )