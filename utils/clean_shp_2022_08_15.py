"""
Create a new layer from a current downloaded version
"""
from collections import OrderedDict
from copy import deepcopy
from datetime import datetime, timedelta
from time import sleep
import os
import sys
from dateutil import tz
import fiona
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(root, 'layers', 'shared'))
import lookups
from schema import RECORD_TEMPLATE
from settings import UTC_ZONE, TIME_FORMAT


LA_ZONE = tz.gettz('America/Los_Angeles')
# PST seems to have daylight saving build, redefinig it since it is fixed
PST_ZONE = tz.tzoffset('PST', -28800) # tz.gettz('PST')
BASE_PATH = os.path.abspath(os.path.join('..', '..', 'data'))
DATA = os.path.join(BASE_PATH, 'lora_tracking_2a', 'lora_tracking_2.shp')
NEW = os.path.join(BASE_PATH, 'lora_tracking_3')


DISCARD_LIST = [
    'd3ab8843-e530-4ce8-bc0e-a3bbffe037e6',
    'aac015bd-fd36-491d-b84e-ad091eff73b4']


def clean_time_field(timestring):
    if timestring[-1] == '.':
        timestring = timestring[:-1]
    return timestring


def transform_time(time, from_tz=LA_ZONE, to_tz=UTC_ZONE):
    assert from_tz
    assert to_tz
    utc = time.replace(tzinfo=from_tz)
    return utc.astimezone(to_tz)


def get_datetime(timestring, tzinfo=None):
    try:
        dtm = datetime.strptime(clean_time_field(timestring), TIME_FORMAT)
    except (TypeError, ValueError):
        return None
    if tzinfo:
        dtm = dtm.replace(tzinfo=tzinfo)
    return dtm


def determine_time(properties):
    """
    Try to determine whether time is UTC or not, this is quiet tricky since we
    changed that around a lot during the existence of this app.

    Args:
        properties(dic): The property dic of a feature
    Returns:
        dic
    """
    ret = {
        'buffered': False, 'tm_valid': False, 'pl_tm_utc': None,
        'tr_tm_utc': None, 'rec_tm_utc': None}
    # initialize variables that might or might not be touched by the below
    pl_tm_utc = rec_tm_utc = None
    received = get_datetime(properties['received_t'], tzinfo=UTC_ZONE)
    difference = None
    # we assume tme as utc (which is not correct in many cases; we will
    # check later, first we need to assign a tz to do correct math)
    tme = get_datetime(properties['time'], tzinfo=UTC_ZONE)
    ############################################################################
    if received < datetime(2021, 1, 1, tzinfo=UTC_ZONE):
        rec_tm_utc = received
        if tme:
            pl_tm_utc = transform_time(tme, from_tz=PST_ZONE)
            dla = rec_tm_utc - pl_tm_utc
            if timedelta(minutes=2) > dla  > timedelta(minutes=-2):
                ret['tm_valid'] = True
    ############################################################################
    # all data from 2021-08-26 has been invalidated since the format changes
    # several time during that day
    ############################################################################
    elif (
        datetime(2021, 1, 1, tzinfo=UTC_ZONE) < received <
        datetime(2021, 8, 26, tzinfo=UTC_ZONE)
    ):
        rec_tm_utc = received
        if tme:
            pl_tm_utc = transform_time(tme, from_tz=LA_ZONE)
            dla = rec_tm_utc - pl_tm_utc
            if timedelta(minutes=2) > dla  > timedelta(minutes=-2):
                ret['tm_valid'] = True
    ############################################################################
    elif (
        datetime(2021, 8, 27, tzinfo=UTC_ZONE) < received <
        datetime(2021, 12, 13, tzinfo=UTC_ZONE)
    ):
        rec_tm_utc = transform_time(received)
        if tme:
            pl_tm_utc = transform_time(tme)
            dla = rec_tm_utc - pl_tm_utc
            if timedelta(minutes=2) > dla  > timedelta(minutes=-2):
                ret['tm_valid'] = True
    ############################################################################
    elif (
        datetime(2021, 10, 14, tzinfo=UTC_ZONE) < received <
        datetime(2021, 10, 29, tzinfo=UTC_ZONE)
    ):
        rec_tm_utc = transform_time(received, from_tz=LA_ZONE)
        if tme:
            pl_tm_utc = transform_time(tme, from_tz=LA_ZONE)
            dla = rec_tm_utc - pl_tm_utc
            if timedelta(minutes=2) > dla > timedelta(minutes=-2):
                ret['tm_valid'] = True
    ############################################################################
    elif datetime(2021, 12, 13, tzinfo=UTC_ZONE) < received:
        rec_tm_utc = transform_time(received)
        ret['tm_valid'] = True
        if tme:
            pl_tm_utc = tme
            dla = rec_tm_utc - pl_tm_utc
            if timedelta(minutes=2) > dla > timedelta(minutes=-2):
                pass
            else:
                ret['buffered'] = True
    ############################################################################
    else:
        print(properties)
        sys.exit(1)
    ############################################################################
    if pl_tm_utc and pl_tm_utc > rec_tm_utc:
        pl_tm_utc, rec_tm_utc = rec_tm_utc, pl_tm_utc
    if pl_tm_utc:
        if pl_tm_utc == rec_tm_utc:
            pl_tm_utc = None
        else:
            ret['pl_tm_utc'] = pl_tm_utc.strftime(TIME_FORMAT)
    if rec_tm_utc:
        ret['rec_tm_utc'] = rec_tm_utc.strftime(TIME_FORMAT)
    # tracker time is payload time if exist else received time
    ret['tr_tm_utc'] = ret[
       'pl_tm_utc'] if ret.get('pl_tm_utc') else ret.get('rec_tm_utc')
    return ret


def clean(feature):
    properties = deepcopy(RECORD_TEMPLATE)
    # copy old data
    for item in properties:
        properties[item] = feature.get('properties', {}).get(item)
    # assign labels
    device = properties.get('dev', '')
    properties['label'] = lookups.DEVICE_LABELS.get(device) or device
    properties['domain'] = lookups.DOMAINS.get(device, '')
    # copy from original since those field are not in the template
    feature_properties = feature.get('properties', {})
    properties['snr_1'] = feature_properties.get('snr')
    properties['tm_old'] = feature_properties.get('time')
    properties['rec_tm_old'] = feature_properties.get('received_t')
    properties['f_port'] = feature_properties.get('frames')
    for item in ('1', '2', '3', '4', '5'):
        gateway = properties.get('gateway_' + item)
        properties['gw_label_' + item] = lookups.GATEWAY_LABELS.get(
            gateway) or gateway
    # deal with date and time
    time_dic = determine_time(feature_properties)
    properties.update(time_dic)
    properties['tr_tm_src'] = 'gps' if properties['pl_tm_utc'] else 'network'
    return {'geometry': feature.get('geometry'), 'properties': properties}


def validate(feature):
    if feature['properties']['GlobalID'] in DISCARD_LIST:
        return False
    if not feature['properties']['dev']:
        return False
    # this is very old and times cannot be validated, we don't even remember
    # what devices this has been
    if feature['properties']['dev'] == '9876b6115b69':
        return False
    if not feature['properties']['gateway_1']:
        return False
    time = feature.get('properties', {}).get('time', '')
    if time and '****' in time:
        return False
    # invalidate data from 2021-08-26 since the format changed several time this
    # day
    received_t = feature.get('properties', {}).get('received_t')
    if '2021-08-26 00:00:00' < received_t < '2021-08-27':
        return False
    return True


def main():
    count = 0
    discarded = 0
    time_valid = 0
    with fiona.open(DATA) as shapes:
        schema = shapes.schema
        old_properties = schema.get('properties')
        for item in [
            'CreationDa', 'EditDate', 'Editor', 'GlobalID', 'Creator', 'snr',
            'time', 'received_t', 'frames']:
            old_properties.pop(item)
        new_gw_info = []
        for idx in range(1, 6):
            old_properties.pop('gateway_' + str(idx))
            old_properties.pop('rssi_' + str(idx))
            old_properties.pop('snr_' + str(idx))
            new_gw_info.append(('gateway_' + str(idx), 'str:80'))
            new_gw_info.append(('gw_label_' + str(idx), 'str:80'))
            new_gw_info.append(('rssi_' + str(idx), 'str:10'))
            new_gw_info.append(('snr_' + str(idx), 'str:10'))
        properties_list = [
            # ('GlobalID', 'str:38'),
            ('rec_tm_utc', 'str:20'),
            ('pl_tm_utc', 'str:20'),
            ('tr_tm_utc', 'str:20'),
            ('tr_tm_src', 'str:10'),
            ('f_port', 'int'),
            ('buffered', 'int'),
            ('tm_valid', 'int')
        ] + list(old_properties.items()) + new_gw_info + [
            # move these legacy fields to the end, just to have a record for
            # our time manipulation
            ('tm_old', 'str:20'), ('rec_tm_old', 'str:20')]
        new_properties = OrderedDict([item for item in properties_list])
        schema['properties'] = new_properties
        metadata = {
            'driver': shapes.driver, 'crs': shapes.crs, 'schema': schema}
        with fiona.open(NEW, 'w', **metadata) as dest:
            for shape in shapes:
                if not count % 1000:
                    print(count)
                count += 1
                if validate(shape):
                    new_shape = clean(shape)
                    properties = new_shape.get('properties', {})
                    if properties.get('tm_valid'):
                        time_valid +=1
                    else:
                        pass
                    dest.write(new_shape)
                else:
                    discarded += 1
    print(
        'DONE', count, 'features copied,', time_valid,
        'have validated time,', discarded, 'discarded')


if __name__ == '__main__':
    main()
