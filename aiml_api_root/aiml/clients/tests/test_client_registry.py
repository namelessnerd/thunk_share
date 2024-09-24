import unittest
from aiml.clients.client_registry import ai_clients_registry
from aiml.clients.openai_client import OpenAIClient  # Import the class to trigger registration

class TestClientRegistry(unittest.TestCase):
    
    def test_openai_client_registration(self):
        # Check that 'openai' key exists in the client_registry
        self.assertIn('openAI', ai_clients_registry)
        # Check that the registered class is OpenAIClient
        self.assertEqual(ai_clients_registry['openAI'], OpenAIClient)