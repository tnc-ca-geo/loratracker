# standard library
import json
# project
import src.extract as extract
import src.ago as ago


def parse_ago_response(response):
    """
    Convert a AGO response in a tuple of status_code and json-parsed response.

    Args:
        response(bytes): JSON string in bytes (utf-8 encoded)
    Returns:
        tuple(int, dict)
    """
    try:
        jsn = json.loads(response.content.decode('utf-8'))
    except json.decoder.JSONDecodeError:
        return None
    return response.status_code, jsn


def parse_success(dic):
    """
    Parse AGO response for success. Returns list of items created in AGO.

    Args:
        dic(dict): Parsed response as dict
    Returns:
        list(int)
    """
    res = []
    results = dic.get('addResults', [])
    for item in results:
        if item.get('success'):
            res.append(item['objectId'])
    return res



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
        response = service.post_records([feature])
        _, parsed = parse_ago_response(response)
        success = parse_success(parsed)
        if success:
            return {'statusCode': 201, 'body':
                json.dumps({'message': 'Added ' + str(success)})}
        else:
            # output to Cloudwatch for debugging
            print('INVALID RECORD ', feature)
            print('AGO ERROR RESPONSE: ', response.content)
            return {'statusCode': 422, 'body': json.dumps({
                'message': 'Record could not be added to AGO. '
                'See Cloudwatch log for details.'})}
    # Respond with 200 so that health check at TTI does not report problems.
    return {
        'statusCode': 200, 'body': json.dumps({'message': 'invalid GPS fix'})}
