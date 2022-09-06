"""
Extract data from request context
"""
# standard library
from datetime import datetime, timedelta
import json
import re
import time
# third party
from dateutil import tz
# project
from src import decoders
import lookups
import settings


# check whether a device specific decoder exist
DEVICE_MATRIX = {
    'feather-ranger-f3c3': decoders.feather_ranger_f3c3}


# check whether an application_specific_decoder exist
APPLICATION_MATRIX = {
    'test-n-ranging': decoders.oyster,
    'adeunis-tester': decoders.adeunis,
    'miromico-cargo': decoders.miromico_cargo,
    'miromico-asset-test': decoders.miromico_cargo}


def gps_validate(transformed_message):
    """
    Make sure we are sending a valid GPS fix
    """
    if not -180 < transformed_message.get('geometry', {}).get('x') < 180:
        return False
    if not -90 < transformed_message.get('geometry', {}).get('y') < 90:
        return False
    return True


def get_time(utc_tm_st_dt, frmt=settings.TIME_FORMAT, zone=settings.UTC_ZONE):
    """
    CLean up time. We don't convert to local time anymore.

    Args:
        utc_tm_st_or_dt(str): Time string as received from the server.
            Clean millis
        utc_tm_st_or_dt(datetime): Alternatively we can accept a datetime object
    Returns:
        datetime
    """
    assert zone
    # test whether we already have the right time format
    if isinstance(utc_tm_st_dt, datetime):
        return utc_tm_st_dt.replace(tzinfo=zone)
    # check whether we can convert using a particular format
    for item in ['%Y-%m-%dT%H:%M:%S', frmt]:
        try:
            utc_tm_st_dt = utc_tm_st_dt.split('.')[0]
            naive_utc = datetime.strptime(utc_tm_st_dt, item)
        except (ValueError, AttributeError):
            continue
        else:
            return naive_utc.replace(tzinfo=zone)


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
        device) or APPLICATION_MATRIX.get(application)
    # use the network decoder if this stack does not provide a decoder function
    # it needs at least 'x' and 'y' fields, 'time' is optionial
    if not decoder_function:
        decoded = uplink_message.get('decoded_payload')
    else:
        try:
            decoded = decoder_function(
                uplink_message.get('frm_payload'),
                uplink_message.get('f_port', 0))
        except (ValueError, IndexError):
            return {}
        if decoded.get('status') != 'ok':
            return {}
    lora_settings = uplink_message.pop('settings', {})
    label = lookups.DEVICE_LABELS.get(device) or device
    try:
        geometry = {'x': decoded.pop('x'), 'y': decoded.pop('y'),
            'spatialReference': {'wkid': 4326}}
    except KeyError:
        return {}
    lora = lora_settings.get('data_rate', {}).get('lora', {})
    rec_tm = get_time(uplink_message.get('received_at'))
    # this is currently pretty naive and has to be handled by decoder
    rec_tm_str = rec_tm.strftime(settings.TIME_FORMAT)
    pl_tm = get_time(decoded.get('time'))
    try:
        pl_tm_str = pl_tm.strftime(settings.TIME_FORMAT)
    except AttributeError:
        pl_tm_str = None
    attributes = {
        'rec_tm_utc': rec_tm_str,
        'pl_tm_utc': pl_tm_str,
        'tr_tm_utc': pl_tm_str if pl_tm_str else rec_tm_str,
        'tr_tm_src': 'gps' if pl_tm_str else 'network',
        'tm_valid': 1,
        # we consider data buffered if it arrives more than one minutes after
        # measuring
        'buffered': rec_tm - pl_tm > timedelta(minutes=2) if pl_tm_str else False,
        # indicate whether we determine time from gps or network
        # TODP: 'rtc' might be a third possibility we did not come accross yet
        'app':  dic.get('end_device_ids', {}).get('application_ids', {}).get(
            'application_id'),
        'dev': device,
        'f_port': uplink_message.get('f_port', 0),
        'dr': (
            str(lora.get('bandwidth', '')) + '/' +
            str(lora.get('spreading_factor', ''))),
        'cr': lora_settings.get('coding_rate'),
        'f_mhz' : int(lora_settings.get('frequency', '0'))/1E+6,
        'airtime_ms': int(float(
            re.sub(r'[^0-9.]', '',
            uplink_message.get('consumed_airtime', '0'))) * 1E+3),
        'domain': lookups.DOMAINS.get(device),
        'label': label}
    gateways = get_gateways(uplink_message)
    attributes['gtw_count'] = len(gateways)
    # this is currently here for backward compatibility
    # TODO: remove after data migration
    # attributes['snr'] = gateways[0][1]
    for idx in range(0, attributes['gtw_count']):
        index = str(idx+1)
        try:
            attributes['gateway_' + index] = gateways[idx][0]
            attributes['snr_' + index] = gateways[idx][1]
            attributes['rssi_' + index] = gateways[idx][2]
            attributes['gw_label_' + index] = lookups.GATEWAY_LABELS.get(
                gateways[idx][0])
        except IndexError:
            print('GATEWAY EXTRACT FAILED')
    return {'geometry': geometry, 'attributes': attributes}
