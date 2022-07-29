# standard library
import json
# project
import src.extract as extract
import src.ago as ago


def lambda_handler(event, context):
    """
    Lambda function parsing location message from tracker

    Args:
        event: dict, required
            API Gateway Lambda Proxy Input Format
            Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format
        context: object, required
            Lambda Context runtime methods and attributes
            Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html
    Returns:
        API Gateway Lambda Proxy Output Format: dict
        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    feature = extract.extract_feature(event)
    if feature:
        service = ago.FeatureService()
        service.post_records([feature])
        return {"statusCode": 200, "body": json.dumps({"message": "ok"})}
    return {"statusCode": 200, "body": json.dumps({"message": "invalid GPS fix"})}
