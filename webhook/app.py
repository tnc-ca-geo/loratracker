# pylint:disable=E0401
"""
Webhook for receiving location messages and displaying it on the map. Supports
Miromico and Oyster trackers plus a few custom formats.
"""
# standard library
import json
from typing import Union
# project
from src import extract
from src import ago


def http_response(code:int, response:dict) -> dict:
    """
    Shorthand for API gateway http response dict.

    Args:
        code(int): Response code
        response(dict): Response body dict that will converted to json
    Returns:
        dict
    """
    return {
        'statusCode': code,
        'body': json.dumps(response, separators=[',', ':'])
    }


def parse_ago_response(response:bytes) -> Union[tuple[int, dict], None]:
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


def parse_success(dic:dict) -> list[int]:
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


def lambda_handler(event:dict, _) -> dict:
    """
    Lambda function parsing location message from tracker

    Args:
        event: dict, required
            API Gateway Lambda Proxy Input Format
    Returns:
        API Gateway Lambda Proxy Output Format: dict
    """
    feature = extract.extract_feature(event)
    print('FEATURE', feature)
    if feature:
        service = ago.FeatureService()
        response = service.post_records([feature])
        _, parsed = parse_ago_response(response)
        success = parse_success(parsed)
        if success:
            print('SUCCESS', success)
            return http_response(201, {'message': 'ok', 'items': success})
        # output to Cloudwatch for debugging
        print('AGO ERROR RESPONSE: ', response.content)
        return http_response(422, {
            'message': 'Record could not be added to AGO. '
            'See Cloudwatch log for details.'})
    # Respond with 200 so that health check at TTI does not report problems.
    return http_response(200, {'message': 'invalid GPS fix'})
