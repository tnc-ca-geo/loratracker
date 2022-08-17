# standard library
import json
import os
import sys
# third party
import pytest
# testing
from tests.example_data import lorawan_webhook_example
# project
# Make sure that the webhook directory is on the path for testing, this is
# necessary in order not to put the test code on AWS LAMBDA
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(root, 'webhook'))
sys.path.append(os.path.join(root, 'layers', 'shared'))
from webhook import app


# @pytest.fixture()
# def apigw_event():
#    """
#    Generates API GW Event
#    """
#    return lorawan_webhook_example


# def test_lambda_handler(apigw_event, mocker):
#    ret = app.lambda_handler(apigw_event, "")
#    data = json.loads(ret["body"])
#    assert ret["statusCode"] == 200
#    assert "message" in ret["body"]
#    assert data["message"] == "ok"
