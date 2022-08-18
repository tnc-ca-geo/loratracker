# standard library
from copy import deepcopy
from datetime import datetime
from dateutil import tz
import json
import os
from unittest import TestCase
import sys
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(root, 'webhook'))
sys.path.append(os.path.join(root, 'layers', 'shared'))
# testing
from tests.example_data import lorawan_webhook_example
# project
from webhook.src import extract


class TestExtract(TestCase):

    def test_extract(self):
        expected = {
            'geometry': {'x': -122.27557, 'y': 37.8418,
            'spatialReference': {'wkid': 4326}},
            'attributes': {
                'rec_tm_utc': '2021-08-25 19:22:58',
                'pl_tm_utc': '2021-08-25 19:23:00',
                'tr_tm_utc': '2021-08-25 19:23:00',
                'tm_valid': True,
                'buffered': False,
                'app': 'test-n-ranging',
                'dev': 'feather-ranger-f3c3',
                'snr': 10,
                'f_port': 1,
                'gateway_1': 'foo',
                'snr_1': 10,
                'rssi_1': -30,
                'gw_label_1': None,
                'gateway_2': 'laird-rg191-296af5',
                'snr_2': 10,
                'rssi_2': -48,
                'gw_label_2': 'Falk Laird home',
                'dr': '125000/7',
                'cr': '4/5',
                'f_mhz': 905.3,
                'airtime_ms': 107,
                'gtw_count': 2,
                'label': 'The NO device',
                'domain': 'falk'}}
        res = extract.extract_feature(lorawan_webhook_example)
        self.assertDictEqual(res, expected)

    def test_wo_payload_decoder(self):
        """
        Test whether upstream payload decoder can be used.
        """
        lorawan_webhook_example_modified = deepcopy(lorawan_webhook_example)
        body = json.loads(lorawan_webhook_example_modified['body'])
        end_device_ids = body['end_device_ids']
        end_device_ids['application_ids']['application_id'] = 'fooapp'
        end_device_ids['device_id'] = 'foodev'
        body['uplink_message']['decoded_payload'] = {
            'x': -122.27557,
            'y': 37.8418}
        lorawan_webhook_example_modified['body'] = json.dumps(body)
        expected = {
            'geometry': {'x': -122.27557, 'y': 37.8418,
            'spatialReference': {'wkid': 4326}},
            'attributes': {
                'rec_tm_utc': '2021-08-25 19:22:58',
                'pl_tm_utc': None,
                'tr_tm_utc': '2021-08-25 19:22:58',
                'tm_valid': True,
                'buffered': False,
                'app': 'fooapp',
                'dev': 'foodev',
                'snr': 10,
                'f_port': 1,
                'gateway_1': 'foo',
                'snr_1': 10,
                'rssi_1': -30,
                'gw_label_1': None,
                'gateway_2': 'laird-rg191-296af5',
                'snr_2': 10,
                'rssi_2': -48,
                'gw_label_2': 'Falk Laird home',
                'dr': '125000/7',
                'cr': '4/5',
                'f_mhz': 905.3,
                'airtime_ms': 107,
                'gtw_count': 2,
                'label': 'foodev',
                'domain': None}}
        res = extract.extract_feature(lorawan_webhook_example_modified)
        self.assertDictEqual(res, expected)

    def test_wo_payload_decoder_w_time(self):
        lorawan_webhook_example_modified = deepcopy(lorawan_webhook_example)
        body = json.loads(lorawan_webhook_example_modified['body'])
        end_device_ids = body['end_device_ids']
        end_device_ids['application_ids']['application_id'] = 'fooapp'
        end_device_ids['device_id'] = 'foodev'
        body['uplink_message']['decoded_payload'] = {
            'x': -122.27557, 'y': 37.8418, 'time': '2021-08-25 19:22:00'}
        lorawan_webhook_example_modified['body'] = json.dumps(body)
        expected = {
            'geometry': {'x': -122.27557, 'y': 37.8418,
            'spatialReference': {'wkid': 4326}},
            'attributes': {
                'rec_tm_utc': '2021-08-25 19:22:58',
                'pl_tm_utc': '2021-08-25 19:22:00',
                'tr_tm_utc': '2021-08-25 19:22:00',
                'tm_valid': True,
                'buffered': False,
                'app': 'fooapp',
                'dev': 'foodev',
                'snr': 10,
                'f_port': 1,
                'gateway_1': 'foo',
                'snr_1': 10,
                'rssi_1': -30,
                'gw_label_1': None,
                'gateway_2': 'laird-rg191-296af5',
                'snr_2': 10,
                'rssi_2': -48,
                'gw_label_2': 'Falk Laird home',
                'dr': '125000/7',
                'cr': '4/5',
                'f_mhz': 905.3,
                'airtime_ms': 107,
                'gtw_count': 2,
                'label': 'foodev',
                'domain': None}}
        res = extract.extract_feature(lorawan_webhook_example_modified)
        self.assertDictEqual(res, expected)

    def test_wo_payload_decoder_nonsensical(self):
        lorawan_webhook_example_modified = deepcopy(lorawan_webhook_example)
        body = json.loads(lorawan_webhook_example_modified['body'])
        end_device_ids = body['end_device_ids']
        end_device_ids['application_ids']['application_id'] = 'fooapp'
        end_device_ids['device_id'] = 'foodev'
        body['uplink_message']['decoded_payload'] = {'a': 1, 'b': 2, 'c': 3}
        lorawan_webhook_example_modified['body'] = json.dumps(body)
        self.assertEqual(
            extract.extract_feature(lorawan_webhook_example_modified), {})

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

    def test_get_time(self):
        # test from UTC string as provided from network server
        example_time = '2021-08-25T19:22:58.780515972Z'
        res = extract.get_time(example_time)
        self.assertEqual(res,
            datetime(2021, 8, 25, 19, 22, 58, tzinfo=tz.gettz('UTC')))

    def test_get_time_dt_already(self):
        # test when time is already time
        example_time = datetime(2021, 8, 25, 19, 22, 58)
        res = extract.get_time(example_time)
        self.assertEqual(res,
            datetime(2021, 8, 25, 19, 22, 58, tzinfo=tz.gettz('UTC')))

    def test_get_time_alternative_format(self):
        # test with simpler format
        example_time = '2021-08-25 19:22:58'
        res = extract.get_time(example_time)
        self.assertEqual(res,
            datetime(2021, 8, 25, 19, 22, 58, tzinfo=tz.gettz('UTC')))
