# standard library
from copy import deepcopy
from unittest import TestCase
# testing
from tests.unit.example_data import lorawan_webhook_example
# project
from webhook.src import extract


class TextExtract(TestCase):

    def test_extract(self):
        res = extract.extract_gps_message(lorawan_webhook_example)


    def test_invalid_json(self):
        modified_example = deepcopy(lorawan_webhook_example)
        modified_example['body'] = 'not valid'
        self.assertEqual(
            extract.extract_gps_message(modified_example), {})
