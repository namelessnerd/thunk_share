import unittest
from unittest.mock import patch, MagicMock
from pydantic import ValidationError
from typing import Dict, Any, Union
import sys
import os
from service_config.service_registry import ServiceRegistry, AIServiceConfig


class TestServiceRegistry(unittest.TestCase):

    @patch('service_config.service_registry.ServiceRegistry._ServiceRegistry__get_ai_service_models')
    @patch('service_config.service_registry.ServiceRegistry._ServiceRegistry__handle_cache')
    def test_get_ai_service_models_valid_provider(self, mock_get_ai_service_models, mock_handle_cache):
        # Mock the cache miss and valid configuration
        mock_handle_cache.side_effect = [None, None]  # Cache miss on both calls
        mock_get_ai_service_models.return_value = {
            "provider1": {
                "provider": "provider1",
                "model": "gpt-3",
                "temperature": 0.7,
                "api_key": "abc123"
            }
        }
        registry = ServiceRegistry(configs={})
        result = registry.get_ai_service_configs("acmeinc", "creatives")
        self.assertIsInstance(result["provider1"], AIServiceConfig)
        self.assertEqual(result["provider1"].provider, "provider1")
        self.assertEqual(result["provider1"].model, "gpt-3")

    @patch('service_config.service_registry.ServiceRegistry._ServiceRegistry__get_ai_service_models')
    @patch('service_config.service_registry.ServiceRegistry._ServiceRegistry__handle_cache')
    def test_get_ai_service_models_validation_error(self, mock_get_ai_service_models, mock_handle_cache):
        # Mock cache miss and a config with missing fields (causing ValidationError)
        mock_handle_cache.side_effect = [None, None]  # Cache miss on both calls
        mock_get_ai_service_models.return_value = {
            "provider1": {
                "model": "gpt-3",  # Missing "provider" field
                "temperature": 0.7,
                "api_key": "abc123"
            }
        }
        registry = ServiceRegistry(configs={})
        result = registry.get_ai_service_configs("acmeinc", "creatives")
        self.assertIsInstance(result["provider1"], str)
        self.assertIn("Field: ('provider',)", result["provider1"])
        self.assertIn("Err: ('provider',)", result["provider1"])

    @patch('service_config.service_registry.ServiceRegistry._ServiceRegistry__handle_cache')
    def test_get_ai_service_models_cache_hit(self, mock_handle_cache):
        # Mock cache hit with valid data
        mock_handle_cache.return_value = {
            "provider1": {
                "provider": "provider1",
                "model": "gpt-3",
                "temperature": 0.7,
                "api_key": "abc123"
            }
        }
        registry = ServiceRegistry(configs={})
        result = registry.get_ai_service_configs("acmeinc", "creatives")
        self.assertIsInstance(result["provider1"], AIServiceConfig)
        self.assertEqual(result["provider1"].provider, "provider1")
        self.assertEqual(result["provider1"].model, "gpt-3")

    @patch('service_config.service_registry.ServiceRegistry._ServiceRegistry__handle_cache')
    def test_get_ai_service_models_cache_hit_with_validation_error(self, mock_handle_cache):
        # Mock cache hit with invalid data (missing "provider" field)
        mock_handle_cache.return_value = {
            "provider1": {
                "model": "gpt-3",  # Missing "provider" field
                "temperature": 0.7,
                "api_key": "abc123"
            }
        }
        registry = ServiceRegistry(configs={})
        result = registry.get_ai_service_configs("acmeinc", "creatives")

        # Verify that a ValidationError string is returned for provider1
        self.assertIsInstance(result["provider1"], str)
        self.assertIn("Field: ('provider',)", result["provider1"])
        self.assertIn("Err: ('provider',)", result["provider1"])