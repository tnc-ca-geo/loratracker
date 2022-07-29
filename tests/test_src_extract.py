# standard library
from copy import deepcopy
import json
import os
from unittest import TestCase
import sys
sys.path.insert(
    0, os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'webhook')))
# testing
from tests.example_data import lorawan_webhook_example
# project
from webhook.src import extract


class TextExtract(TestCase):

    def test_extract(self):
        self.assertDictEqual(
            extract.extract_feature(lorawan_webhook_example), {
                'geometry': {'x': -122.27557, 'y': 37.8418,
                'spatialReference': {'wkid': 4326}},
                'attributes': {
                    'received_t': '2021-08-25 12:22:58',
                    'time': '2021-08-25 19:23:00',
                    'app': 'test-n-ranging',
                    'dev': 'feather-ranger-f3c3',
                    'frames': None, # unused
                    'gateway': 'foo',
                    'rssi': -30,
                    'dr': 3,
                    'cr': '4/5',
                    'snr': 10,
                    'f_mhz': 905.3,
                    'airtime_ms': 107,
                    'gtw_count': 2}})

    def test_invalid_json(self):
        modified_example = deepcopy(lorawan_webhook_example)
        modified_example['body'] = 'not valid'
        self.assertEqual(
            extract.extract_feature(modified_example), {})


class TestExtractHelpers(TestCase):

    def test_get_gateways(self):
        example_data = json.loads(
            lorawan_webhook_example['body'])['uplink_message']
        self.assertEqual(
            extract.get_gateways(example_data), [
            ('foo', 10, -30), ('laird-rg191-296af5', 10, -48)])


class TestTransformTime(TestCase):

    def test_transform_time(self):
        example_time = '2021-08-25T19:22:58.780515972Z'
        res = extract.transform_time(example_time)
        self.assertEqual(res, '2021-08-25 12:22:58')
