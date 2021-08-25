# standard library
import json
# third party
import pytest
# testing
from tests.unit.example_data import lorawan_webhook_example
# project
from webhook import app


@pytest.fixture()
def apigw_event():
    """
    Generates API GW Event
    """
    return lorawan_webhook_example


def test_lambda_handler(apigw_event, mocker):
    ret = app.lambda_handler(apigw_event, "")
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 200
    assert "message" in ret["body"]
    assert data["message"] == "ok"
