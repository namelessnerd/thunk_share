import unittest

from aiml.prompts.utils import PromptManager


class TestPromptManager(unittest.TestCase):



    """
    Tests that when an existing client is present, it is returned
    instead of a new one being created
    """

    def test_get_ai_client_existing_client(self):
        PromptManager.get_prompt("acmeinc", "prescreener")
