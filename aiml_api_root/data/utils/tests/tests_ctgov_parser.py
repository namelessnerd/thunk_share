import unittest
from typing import Optional, List, Dict

from pydantic import BaseModel

from data.utils.parser_utils import camel_to_snake, snake_to_camel, from_dict


class Job(BaseModel):
    title: str
    dept: str


class Person(BaseModel):
    name: str
    age: int
    job: Job
    current_car: Optional[str] = None
    all_cars: Optional[List[Dict[str, str]]] = None



class TestDataUtils(unittest.TestCase):

    def test_camel_to_snake(self):
        self.assertEqual(camel_to_snake('camelCase'), 'camel_case')
        self.assertEqual(camel_to_snake('CamelCaseTest'), 'camel_case_test')

    def test_snake_to_camel(self):
        self.assertEqual(snake_to_camel('snake_case'), 'snakeCase')
        self.assertEqual(snake_to_camel('snake_case_test'), 'snakeCaseTest')

    def test_from_dict(self):
        json_data = {
            "name": "Alice",
            "age": 30,
            "job": {
                "title": "Developer",
                "dept": "Engineering"
            },
            "currentCar": "Tesla"
        }
        person = from_dict(Person, json_data)
        self.assertEqual(person.name, "Alice")
        self.assertEqual(person.age, 30)
        self.assertEqual(person.job.title, "Developer")
        self.assertEqual(person.job.dept, "Engineering")
        self.assertEqual(person.current_car, "Tesla")

    def test_from_dict_missing_optional(self):
        json_data = {
            "name": "Bob",
            "age": 25,
            "job": {
                "title": "Designer",
                "dept": "Creative"
            }
        }
        person = from_dict(Person, json_data)
        self.assertEqual(person.name, "Bob")
        self.assertEqual(person.age, 25)
        self.assertEqual(person.job.title, "Designer")
        self.assertEqual(person.job.dept, "Creative")
        self.assertIsNone(person.current_car)

    def test_from_dict_extra_fields(self):
        json_data = {
            "name": "Eve",
            "age": 28,
            "job": {
                "title": "Artist",
                "dept": "Creative"
            },
            "currentCar": "Fiat",
            "extraField": "This should be ignored"
        }
        person = from_dict(Person, json_data)
        self.assertEqual(person.name, "Eve")
        self.assertEqual(person.age, 28)
        self.assertEqual(person.job.title, "Artist")
        self.assertEqual(person.job.dept, "Creative")
        self.assertEqual(person.current_car, "Fiat")

    def test_from_dict_wrong_data_type(self):
        json_data = {
            "name": "Frank",
            "age": "twenty-five",  # Invalid type for age
            "job": {
                "title": "Engineer",
                "dept": "Development"
            }
        }
        with self.assertRaises(ValueError):
            from_dict(Person, json_data)


if __name__ == '__main__':
    unittest.main()
