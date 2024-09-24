import json
import unittest

from aiml.schemas.dao.prescreener import parse_prescreener, parse_ps_result


class MyTestCase(unittest.TestCase):
    invalid_data = {
        'key1a': {
            'key2b': {
                'key3c': 'value3',
                'key3a': 'value4'
            },
            'key2c': {
                'key3b': 'value5',
                'key3c': 'value6'
            }
        },
        'key1b': {
            'key2a': {
                'key3a': 'value7',
                'key3b': 'value8'
            },
            'key2c': {
                'key3c': 'value9',
                'key3a': 'value10'
            }
        }
    }

    valid_data_1 = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "PrescreenerQuestionnaire",
        "type": "object",
        "properties": {
            "start_question_id": "q1",
            "questions": [
                {
                    "id": "q1",
                    "question": "Have you been diagnosed with nonsquamous non-small cell lung cancer (NSCLC)?",
                    "explanation": "This question is necessary to determine if the participant has the specific type of cancer being studied.",
                    "source": "Inclusion Criteria: Histologically or cytologically confirmed diagnosis of locally advanced, unresectable (Stage IIIB, IIIC), or metastatic Stage IV (M1a, M1b, or M1c) NSCLC.",
                    "confidence_score": 0.95,
                    "next_question_id": "q2",
                    "data_type": "boolean",
                    "is_required": True,
                    "user_input": False,
                    "input control": "radio",
                    "options": [
                        {"value": True, "label": "Yes"},
                        {"value": False, "label": "No"}
                    ]
                },
                {
                    "id": "q2",
                    "question": "Is your NSCLC of nonsquamous histology?",
                    "explanation": "This question helps to confirm the specific histology of the cancer.",
                    "source": "Inclusion Criteria: Participants must have NSCLC with nonsquamous histology.",
                    "confidence_score": 0.95,
                    "next_question_id": "q3",
                    "data_type": "boolean",
                    "is_required": True,
                    "user_input": False,
                    "input control": "radio",
                    "options": [
                        {"value": True, "label": "Yes"},
                        {"value": False, "label": "No"}
                    ]
                }]
        },
        "required": ["start_question_id", "questions"],
        "additionalProperties": False
    }

    valid_data_2 = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PrescreenerQuestionnaire",
  "type": "object",
  "properties": {
    "start_question_id": {
      "type": "string",
      "description": "ID of the first question in the questionnaire"
    },
    "questions": {
      "type": "array",
      "description": "List of questions in the questionnaire",
      "items":  [
                {
                    "id": "q1",
                    "question": "Have you been diagnosed with nonsquamous non-small cell lung cancer (NSCLC)?",
                    "explanation": "This question is necessary to determine if the participant has the specific type of cancer being studied.",
                    "source": "Inclusion Criteria: Histologically or cytologically confirmed diagnosis of locally advanced, unresectable (Stage IIIB, IIIC), or metastatic Stage IV (M1a, M1b, or M1c) NSCLC.",
                    "confidence_score": 0.95,
                    "next_question_id": "q2",
                    "data_type": "boolean",
                    "is_required": True,
                    "user_input": False,
                    "input control": "radio",
                    "options": [
                        {"value": True, "label": "Yes"},
                        {"value": False, "label": "No"}
                    ]
                },
                {
                    "id": "q2",
                    "question": "Is your NSCLC of nonsquamous histology?",
                    "explanation": "This question helps to confirm the specific histology of the cancer.",
                    "source": "Inclusion Criteria: Participants must have NSCLC with nonsquamous histology.",
                    "confidence_score": 0.95,
                    "next_question_id": "q3",
                    "data_type": "boolean",
                    "is_required": True,
                    "user_input": False,
                    "input control": "radio",
                    "options": [
                        {"value": True, "label": "Yes"},
                        {"value": False, "label": "No"}
                    ]
                }]}},
        "required": ["start_question_id", "questions"],
        "additionalProperties": False
    }

    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_prescreen_parser_bad_input(self):
        result = parse_ps_result(MyTestCase.invalid_data, {})
        self.assertEqual(result, {})  # add assertion here


    def test_prescreen_parser(self):
        result = parse_ps_result(MyTestCase.valid_data_1, {"questions": []})
        self.assertIsNotNone(result.get("start_question_id"))
        self.assertEqual(len(result.get("questions")), 2)
        print(result)
        result = parse_ps_result(MyTestCase.valid_data_2, {"questions": []})
        self.assertIsNotNone(result.get("start_question_id"))
        self.assertEqual(len(result.get("questions")), 2)
        print(result)


if __name__ == '__main__':
    unittest.main()
