"""
Extract data from request context
"""
# standard library
from datetime import datetime
import json
import re
import time
# third party
from dateutil import tz
# project
from src import decoders

# doing this only california for now, make sure that the same entries exist
# in the Lambda environment
from_tz = tz.gettz('UTC')
to_tz = tz.gettz('America/Los_Angeles')
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


# check whether a device specific decoder exist
DEVICE_MATRIX = {
    'feather-ranger-f3c3': decoders.feather_ranger_f3c3
}


# check whether an application_specific_decoder exist
APPLICATION_MATRIX = {
    'test-n-ranging': decoders.oyster,
    'adeunis-tester': decoders.adeunis,
    'miromico-cargo': decoders.miromico_cargo,
    'miromico-asset-test': decoders.miromico_cargo
}


# device labels`
DEVICE_LABELS = {
    'adeunis-ftd-239db': 'CTS&E Loaner Field tester',
    'adeunis-ftd-23754': 'Marks Adeunis FTD',
    'feather-ranger-f3c3': 'The NO device (Falk)',
    'jldp-oyster-c7a0': 'Blue Kawasaki OHV (JLDP)',
    'jldp-oyster-c7a8': 'Green Honda OHV (JLDP)',
    'oyster-005d93': 'Blue Toyoto 4runner (SCI)',
    'tnc-adeunis-ftd-0235a1': 'The French Connection (JLDP)'
}


def empty_decoder(payload):
    """
    Use this if not decocer found
    """
    return {}


def gps_validate(transformed_message):
    """
    Make sure we are sending a valid GPS fix
    """
    if not -180 < transformed_message.get('geometry', {}).get('x') < 180:
        return False
    if not -90 < transformed_message.get('geometry', {}).get('y') < 90:
        return False
    return True


def transform_time(utc_time, frmt='%Y-%m-%dT%H:%M:%S'):
    """
    transform utc time into local time
    """
    # cutting time string here since strptime does not supports 9 decimal
    # points in seconds, not pretty but quick work around
    # get rid of decimal points, todo: make this more elegant
    print('FROM_TZ', from_tz)
    print('TO_TZ', to_tz)
    # make sure timezones are created (will return None if incorrect tz
    # string provided)
    assert from_tz
    assert to_tz
    utc_time = utc_time.split('.')[0]
    naive_utc = datetime.strptime(utc_time, frmt)
    utc = naive_utc.replace(tzinfo=from_tz)
    return utc.astimezone(to_tz).strftime('%Y-%m-%d %H:%M:%S')


def get_gateways(dic):
    """
    Return gateways, ordered by rssi

    Args:
        dic (dict): uplink message dictionary
    Returns:
        list of tuples containing gateway id and rssi
    """
    rx_metadata = dic.get('rx_metadata', [])
    gateways = [(
        item.get('gateway_ids', {}).get('gateway_id'),
        item.get('snr'), item.get('rssi'))
        for item in rx_metadata]
    gateways.sort(key=lambda x: -x[-1])
    return gateways


def extract_feature(event):
    """
    Extract a minimal dictionary for further processing.

    Args:
        event (object): A API GW Event
    Returns:
        dic
    """
    body = event.get('body', {})
    try:
        dic = json.loads(body)
    except (json.decoder.JSONDecodeError, TypeError) as e:
        return {}
    uplink_message = dic.get('uplink_message', {})
    application = dic.get(
        'end_device_ids', {}).get('application_ids', {}).get('application_id')
    device = dic.get('end_device_ids', {}).get('device_id')
    decoder_function = DEVICE_MATRIX.get(
        device) or APPLICATION_MATRIX.get(application) or empty_decoder
    try:
        decoded = decoder_function(
            uplink_message.get('frm_payload'), uplink_message.get('f_port', 0))
    except (ValueError, IndexError):
        return {}
    if decoded.get('status') != 'ok':
        return {}
    gateways = get_gateways(uplink_message)
    settings = uplink_message.pop('settings', {})
    label = DEVICE_LABELS.get(device) or device
    geometry = {'x': decoded.pop('x'), 'y': decoded.pop('y'),
        'spatialReference': {'wkid': 4326}}
    attributes = {
        'received_t': transform_time(uplink_message.get('received_at')),
        'time': datetime.strftime(decoded.get('time'), '%Y-%m-%d %H:%M:%S'),
        'app':  dic.get('end_device_ids', {}).get('application_ids', {}).get(
            'application_id'),
        'dev': dic.get('end_device_ids', {}).get('device_id'),
        'frames': None,
        'gateway': gateways[0][0] if gateways else None,
        'rssi': gateways[0][2] if gateways else 0,
        'dr': settings.get('data_rate_index'),
        'cr': settings.get('coding_rate'),
        'snr': gateways[0][1] if gateways else 0,
        'f_mhz' : int(settings.get('frequency', '0'))/1E+6,
        'airtime_ms': int(float(
            re.sub(r'[^0-9.]', '',
            uplink_message.get('consumed_airtime', '0'))) * 1E+3),
        'gtw_count': len(gateways)}
    return {
        'geometry': geometry, 'attributes': attributes}
