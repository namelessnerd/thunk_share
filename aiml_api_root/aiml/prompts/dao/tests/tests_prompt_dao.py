import json
import unittest
from pathlib import Path

from aiml.prompts.prescreener.prompt_generator import generate_prescreener_prompt
from aiml.schemas import schema_utils
from ..prompt42_prompt import ProblemDefinition, OutputSpecification, InputElement, create_prompt
from aiml.prompts.creatives.prompt_generator import generate_creatives_prompt
from aiml import settings


def get_prescreener_template(template_name: str) -> dict:
    prompt_template_root = settings.prompts["creatives"]["templates"]
    print(Path(settings.__file__).parent)
    prompt_template_file = (f"{Path(settings.__file__).parent}/"
                            f"{prompt_template_root}{template_name}")
    with open(prompt_template_file, 'r') as file:
        return json.load(file)


class PromptLoaderTestCase(unittest.TestCase):
    prob_defn_list: dict = None
    prob_defn_str = {
        "problem_definition": {
            "description": "el1",
            "subproblems": ["sp1", "sp2"]
        }
    }

    @classmethod
    def setUpClass(cls):
        """This method runs once before all tests."""
        super().setUpClass()
        # Load template and store in class variable
        cls.prob_defn_list = get_prescreener_template("generate_creative_prompt42.json")

    def test_problemdefn_string(self):
        pd_given = PromptLoaderTestCase.prob_defn_str["problem_definition"]
        pd_str = ProblemDefinition(**pd_given)
        self.assertEqual(pd_str.description, pd_given["description"])

    def test_problemdefn_list(self):
        pd_given = self.__class__.prob_defn_list["problem_definition"]
        pd_str = ProblemDefinition(**pd_given)
        self.assertEqual(pd_str.description, " ".join(pd_given["description"]))

    def test_output_gen(self):
        pd_given = self.__class__.prob_defn_list["output_specifications"]
        schema = schema_utils.get_schema_file(pd_given["schema"])
        output_str = str(OutputSpecification(expected_format="json",
                                             schema=schema,
                                             examples=[str(ex) for ex in pd_given["examples"]]))
        self.assertIn("<format> json </format>", output_str)

    def test_input_gen(self):
        requirements_for_inputs = [
            InputElement(
                key="description",
                type="str",
                schema=None,
                value="description1"
            ),
            InputElement(
                key="eligibility",
                type="str",
                schema=None,
                value="eligibility1"
            )
        ]
        res = "\n".join([str(req) for req in requirements_for_inputs])
        self.assertIn("<description>description1</description>", res)

    def test_prompt42(self):
        gpsp = generate_prescreener_prompt("acmeinc", "some desc", "some elig")
        create_prompt(gpsp)
        self.assertTrue()

if __name__ == '__main__':
    unittest.main()
