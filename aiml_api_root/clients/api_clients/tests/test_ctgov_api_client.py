import unittest
from unittest.mock import patch, Mock
from requests.exceptions import HTTPError, RequestException
from tenacity import RetryError

from clients.api_clients.ctgov_trials import CTGovTrialClient, CTGovClientException, ResponseFormat
from clients.api_clients.dao.ctgov_data_models import ClinicalTrialData, ProtocolSection, DescriptionModule, \
    EligibilityModule


class TestCTGovTrialClient(unittest.TestCase):


    def setUp(self):
        # Creating the mock ClinicalTrialData and assigning it to success_mock
        self.success_mock = ClinicalTrialData(
            protocol_section=ProtocolSection(
                description_module=DescriptionModule(
                    brief_summary="This is a brief summary of the trial.",
                    detailed_description="This is a detailed description of the trial, explaining the purpose and objectives in more depth."
                ),
                eligibility_module=EligibilityModule(
                    criteria="Inclusion: Age 18-65. Exclusion: Pregnant women.",
                    gender="All",
                    minimum_age="18 Years",
                    maximum_age="65 Years",
                    healthy_volunteers="No"
                )
            )
        )

    @patch('clients.api_clients.ctgov.requests.get')
    def test_get_trial_with_nct_id_success(self, mock_get):
        # Set up mock response
        mock_response = Mock()
        mock_response.json.return_value = self.success_mock.dict()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = CTGovTrialClient()
        trial_data = client.get_trial_with_nct_id("NCT12345678")

        self.assertIsInstance(trial_data, ClinicalTrialData)
        self.assertEqual(trial_data.protocol_section.description_module.brief_summary,
                         "This is a brief summary of the trial.")

    @patch('clients.api_clients.ctgov_client.requests.get')
    def test_get_trial_with_nct_id_404(self, mock_get):
        # Simulate 404 error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = HTTPError(response=Mock(status_code=404))
        mock_get.return_value = mock_response

        client = CTGovTrialClient()
        result = client.get_trial_with_nct_id("NCT12345678")

        self.assertIsInstance(result, CTGovClientException)
        self.assertEqual(str(result), "No result found for the provided NCT ID")

    @patch('clients.api_clients.ctgov_client.requests.get')
    def test_get_trial_with_nct_id_retry_error(self, mock_get):
        # Simulate RetryError
        mock_get.side_effect = RetryError(last_attempt=Mock(exception=Mock(return_value=RequestException("Timeout"))))

        client = CTGovTrialClient()
        result = client.get_trial_with_nct_id("NCT12345678")

        self.assertIsInstance(result, CTGovClientException)
        self.assertTrue("Retry exception from tenacity" in str(result))

    @patch('clients.api_clients.ctgov_client.requests.get')
    def test_get_trial_with_nct_id_unexpected_error(self, mock_get):
        # Simulate an unexpected error
        mock_get.side_effect = Exception("Some unexpected error")

        client = CTGovTrialClient()

        with self.assertRaises(CTGovClientException) as context:
            client.get_trial_with_nct_id("NCT12345678")

        self.assertTrue("An unexpected error occurred: Some unexpected error" in str(context.exception))


if __name__ == '__main__':
    unittest.main()
