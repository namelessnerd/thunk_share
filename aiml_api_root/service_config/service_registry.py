from typing import Optional, Dict, Any, Union
from .dao.ai_service_models import AIServiceConfig
from cache.redis_client import RedisClient, RedisConfig
import json
import logging
from .configs.configs import service_configs
from redis import ConnectionError, TimeoutError
from pydantic import ValidationError

class AIServiceConfigException(Exception):
    
    """
    Custom exception class for handling errors related to TrialX AI service configurations.
    """
    def __init__(self, message: str) -> None:
        """
        Initialize the exception with an error message.
        :param message: The error message to display.
        """
        super().__init__(message)

class ServiceRegistry:
    """
    Connect to a services registry (such as Consul) and get the service config from it. 
    """
    def __init__(self, configs: Dict[str, Any]) -> None:
        """
        Initialize the ServiceRegistry with the configuration.
        :param configs: The configuration dictionary.
        """
        if not configs:
            self.configs = service_configs
        else:
            configs = configs

    def __get_ai_service_models(self,
                                customer: str,
                                service: str) -> Optional[Dict[str, Any]]:
        """
        Get the AI configuration for a specific customer, service.
        Checks if the customer has any AI services. If so, for the requested service
        get the configurations for the AI service the customer has access to.
        For example, given creatives, check if acmeinc has any ai subscriptions.
        for the ai subscriptions, see which apply to creatives and return the config for it.
        :param customer: The customer name (e.g., 'acmeinc').
        :param service: The service name (e.g., 'creatives' or 'prescreener').
        :return: The AI configuration dictionary if found, otherwise None.  
        """
        customer_config = self.configs.get(customer)
        if not customer_config:
            logging.error(f"Customer '{customer}' not found.")
            return None
        
        ai_providers = customer_config.get("aiProviders")
        if not ai_providers:
            logging.error(f"{customer} has no AI subscriptions")
            return None

        # get the ai for the current service
        service_configs = customer_config.get(service)
        if not service_configs:
            logging.error(f"No AI configs for customer: {customer}; Service: {service} ")
            return None               
        ai_configs = {}
        for service in service_configs:
            for provider in service:
                s_config = service[provider]
                provider_config = ai_providers.get(provider)
                if provider_config:
                    api_key = provider_config["api_key"]
                    ai_configs[provider] = {
                                            "provider": provider,
                                            "model" : s_config.get("model"),
                                            "temperature": s_config.get("temperature"),
                                            "api_key": api_key}
        return ai_configs

    @classmethod
    def __get_cache_key(cls, customer, service):
        return f"aim:{customer}:{service}"

    @classmethod
    def __handle_cache(cls, customer: str, service: str,
                       cache_op: str = "GET",
                       data: Optional[dict] = None) -> Optional[dict]:
        """
        Handle the Redis cache interaction for reading or writing.
        If `data` is provided, it will write to the cache. Otherwise, it will attempt to read from the cache.
        :param customer: Customer identifier.
        :param service: Service name.
        :param cache_op: GET or SET
        :param data: Data to write to the cache. If None, perform a read operation.
        :return: Cached data (if reading) or None if writing.
        """
        cache_key = cls.__get_cache_key(customer, service)
        redis_client = RedisClient(RedisConfig())
        try:
            with redis_client.get_connection() as redis_conn:
                if cache_op == "GET":
                    cached_data = redis_conn.get(cache_key)
                    if cached_data:
                        logging.info(f"Cache hit for customer: {customer}, service: {service}.")
                        return json.loads(cached_data)
                    else:
                        logging.info(f"Cache miss for customer: {customer}, service: {service}.")
                        return None
                elif cache_op == "SET":
                    if data:
                    # Write to the cache
                        redis_conn.set(cache_key, json.dumps(data))
                        logging.info(f"Cached data for customer: {customer}, service: {service}.")
                    else:
                        logging.error(f"Cannot set None to cache")
                        return None
                else:
                    logging.error("Cache op is either get or set")
                    return None              
        except (ConnectionError, TimeoutError) as e:
            logging.error(f"Redis error: {e}")
            return None  # Fail silently for now, or raise if preferred


    def get_ai_service_configs(self, customer: str,
                              service: str
                             )-> Dict[str, Union[AIServiceConfig, str]]:
        """
        Get the AI config for the given customer and service.
        Returns a list of AIServiceConfigs.
        Checks the cache first if config is present if not gets it from the config.
        :param customer: The customer name (e.g., 'acmeinc').
        :param service: The service name (e.g., 'creatives' or 'prescreener').
        :return: List of AIServiceConfig if present or the errors generated
        :raises: AIServiceConfigException If no config is found for the provider and service
        """
        # aipc_dict = ServiceRegistry.__handle_cache(customer, service)
        # if not aipc_dict:
        aipc_dict = self.__get_ai_service_models(customer, service)
        ServiceRegistry.__handle_cache(customer, service, "SET",
                                        aipc_dict)
        ai_provider_configs = {}
        if aipc_dict:
            for provider in aipc_dict:
                try:
                    ai_provider_configs[provider] = AIServiceConfig(**aipc_dict[provider])
                except ValidationError as e:
                    val_errors = []
                    for error in e.errors():
                        err_loc = error['loc']
                        error_msg = error['msg']
                        val_errors.append(f"Field: {err_loc}, Err: {err_loc}")
                    ai_provider_configs[provider] = ",".join(val_errors)
            return ai_provider_configs
        raise AIServiceConfigException({"Error" : f"No valid {service} config for {customer}"})


