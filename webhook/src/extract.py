"""
Extract data from request context
"""
# standard library
import json
from pprint import pprint


def extract_gps_message(event):
    """
    Extract a minimal dictionary for further processing.

    Args:
        event (object): A API GW Event
    Returns:
        dic
    """
    ret = {}
    body = event.get('body', {})
    try:
        dic = json.loads(body)
    except json.decoder.JSONDecodeError as e:
        return {}
    ret.update(dic.get('uplink_message', {}).get('decoded_payload', {}))
    return ret
