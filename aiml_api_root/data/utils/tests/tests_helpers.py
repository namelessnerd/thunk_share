import unittest
from typing import Optional

from clients.api_clients.dao.ctgov_data_models import ProtocolSection, DescriptionModule, EligibilityModule
from data.utils.helpers import safe_getattr


class TestHelpers(unittest.TestCase):

    def test_safe_getattr(self):
        description_module : DescriptionModule = DescriptionModule(
            brief_summary="test summary"
        )
        eligibility: EligibilityModule = EligibilityModule(
            eligibility_criteria="all are eligible"
        )
        protocol_section : ProtocolSection  = ProtocolSection(
            description_module=description_module,
            eligibility=eligibility
        )
        summary = safe_getattr(protocol_section, ["description_module", "brief_summary"])
        self.assertEqual(summary, "test summary")
        protocol_section = ProtocolSection(
            description_module=None,
            eligibility=eligibility
        )
        summary = safe_getattr(protocol_section, ["description_module", "brief_summary"])
        self.assertIsNone(summary)
        protocol_section = ProtocolSection(
            eligibility=eligibility
        )
        summary = safe_getattr(protocol_section, ["description_module", "brief_summary"])
        self.assertIsNone(summary)
        description_module = DescriptionModule()
        protocol_section = ProtocolSection(
            description_module=description_module,
            eligibility=eligibility
        )
        summary = safe_getattr(protocol_section, ["description_module", "brief_summary"])
        self.assertIsNone(summary)
        summary = safe_getattr(None, ["description_module", "brief_summary"])
        self.assertIsNone(summary)
