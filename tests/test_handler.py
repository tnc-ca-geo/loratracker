# standard library
from copy import deepcopy
import json
import os
import sys
from types import SimpleNamespace
from unittest import TestCase, mock
# testing
from tests.example_data import lorawan_webhook_example
# project
# Make sure that the webhook directory is on the path for testing, this is
# necessary in order not to put the test code on AWS LAMBDA
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(root, 'webhook'))
sys.path.append(os.path.join(root, 'layers', 'shared'))
from webhook import app


class TestHelpers(TestCase):

    def test_parse_ago_response(self):
        example_response = SimpleNamespace(content=(
                b'{"addResults":[{"objectId":43978,"uniqueId":43978,'
                b'"globalId":null,"success":true}]}'), status_code=200)
        res = app.parse_ago_response(example_response)
        self.assertEqual(res, (200, {'addResults': [{
            'objectId': 43978, 'uniqueId': 43978, 'globalId': None,
            'success': True}]}))

    def test_parse_success(self):
        example = {'addResults': [{
            'objectId': 43978, 'uniqueId': 43978, 'globalId': None,
            'success': True}]}
        self.assertEqual(app.parse_success(example), [43978])


class TestHandler(TestCase):

    @mock.patch('app.ago.FeatureService')
    def test_lambda_handler_valid(self, FeatureService):
        instance = FeatureService.return_value
        instance.post_records.return_value = SimpleNamespace(
            status_code=200,
            content=(
                b'{"addResults":[{"objectId":43978,"uniqueId":43978,'
                b'"globalId":null,"success":true}]}'))
        res = app.lambda_handler(lorawan_webhook_example, {})
        self.assertEqual(res['body'], '{"message": "Added [43978]"}')
        self.assertEqual(res['statusCode'], 201)

    @mock.patch('app.ago.FeatureService')
    def test_lambda_handler_ago_reject(self, FeatureService):
        instance = FeatureService.return_value
        instance.post_records.return_value = SimpleNamespace(
            status_code=200,
            content=(
                b'{"addResults":[{"objectId":-1,"uniqueId":-1,"globalId":null,'
                b'"success":false,"error":{"code":1000,"description":"Attribute '
                b'\'tm_valid\' has an invalid value of \'True\'. The value '
                b'should be data type esriFieldTypeDouble."}}]}'))
        res = app.lambda_handler(lorawan_webhook_example, {})
        self.assertEqual(res['body'], (
            '{"message": "Record could not be added to AGO. See Cloudwatch '
            'log for details."}'))
        self.assertEqual(res['statusCode'], 422)

    def test_lambda_handler_invalid(self):
        modified_example = deepcopy(lorawan_webhook_example)
        body_dic = json.loads(modified_example['body'])
        # butchering it radically
        body_dic['uplink_message']['frm_payload'] = ''
        modified_example['body'] = json.dumps(body_dic)
        res = app.lambda_handler(modified_example, {})
        self.assertEqual(res['body'], '{"message": "invalid GPS fix"}')
        self.assertEqual(res['statusCode'], 200)
