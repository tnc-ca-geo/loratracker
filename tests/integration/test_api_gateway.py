# standard library
import os
from unittest import TestCase
# third party
import boto3
import requests

"""
Make sure env variable AWS_SAM_STACK_NAME exists with the name of the stack
we are going to test.
"""

class TestApiGateway(TestCase):
    api_endpoint: str

    @classmethod
    def get_stack_name(cls) -> str:
        stack_name = os.environ.get("AWS_SAM_STACK_NAME")
        if not stack_name:
            raise Exception(
                "Cannot find env var AWS_SAM_STACK_NAME. \n"
                "Please setup this environment variable with the stack name"
                "where we are running integration tests.")
        return stack_name

    @classmethod
    def get_first_value_from_stack(cls, stack_name, key):
        """
        Retrieve a value by key from the stack response.
        """
        client = boto3.client('cloudformation')
        try:
            response = client.describe_stacks(StackName=stack_name)
        except Exception as e:
            raise Exception(
                f'Cannot find stack {stack_name}.\n'
                f'Please make sure stack with the name'
                f' "{stack_name}" exists.') from e
        stack_outputs = response['Stacks'][0]['Outputs']
        outputs = [otp for otp in stack_outputs if otp['OutputKey'] == key]
        return outputs[0]['OutputValue'] if outputs else None

    def setUp(self) -> None:
        """
        Based on the provided env variable AWS_SAM_STACK_NAME,
        here we use cloudformation API to find out what the
        iot-stack URL and the API key is.
        """
        stack_name = TestApiGateway.get_stack_name()
        self.api_endpoint = self.get_first_value_from_stack(
            stack_name, 'IoTApi')
        api_id = self.get_first_value_from_stack(stack_name, 'IoTApiId')
        stage_name = self.get_first_value_from_stack(stack_name, 'StageName')
        client = boto3.client('apigateway')
        keys = client.get_api_keys(includeValues=True).get('items', [])
        stage_key = '{}/{}'.format(api_id, stage_name)
        for item in keys:
            if stage_key in item.get('stageKeys', []):
                self.key = item.get('value')

    def test_api_gateway(self):
        """
        Call the API Gateway endpoint and check the response
        """
        # test unauthorized request
        response = requests.post(self.api_endpoint)
        self.assertEqual(response.status_code, 403)
        response = requests.post(
            self.api_endpoint, headers={'x-api-key': self.key})
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json(), {'message': 'hello world'})
