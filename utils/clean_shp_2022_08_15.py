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


UTC_ZONE = tz.gettz('UTC')
LA_ZONE = tz.gettz('America/Los_Angeles')
# PST seems to have daylight saving build, redefinig it since it is fixed
PST_ZONE = tz.tzoffset('PST', -28800) # tz.gettz('PST')
BASE_PATH = os.path.abspath(os.path.join('..', '..', 'data'))
DATA = os.path.join(BASE_PATH, 'lora_tracking_2a', 'lora_tracking_2.shp')
NEW = os.path.join(BASE_PATH, 'lora_tracking_3')
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

DISCARD_LIST = [
    'd3ab8843-e530-4ce8-bc0e-a3bbffe037e6',
    'aac015bd-fd36-491d-b84e-ad091eff73b4']

RECORD_TEMPLATE = {
    'GlobalID': None,
    'rec_tm_utc': None,
    'pl_tm_utc': None,
    'tr_tm_utc': None,
    'buffered': None,
    'tm_valid': None,
    'time': None,
    'received_t': None,
    'app': None,
    'dev': None,
    'frames': None,
    'dr': None,
    'cr': None,
    'snr': None,
    'f_mhz': None,
    'airtime_ms': None,
    'gtw_count': None,
    'label': None,
    'domain': None,
    'gateway_1': None,
    'rssi_1': None,
    'gw_label_1': None,
    'snr_1': None,
    'gateway_2': None,
    'rssi_2': None,
    'gw_label_2': None,
    'snr_2': None,
    'gateway_3': None,
    'rssi_3': None,
    'gw_label_3': None,
    'snr_3': None,
    'gateway_4': None,
    'rssi_4': None,
    'gw_label_4': None,
    'snr_4': None,
    'gateway_5': None,
    'rssi_5': None,
    'gw_label_5': None,
    'snr_5': None}

DOMAIN_LOOKUP = {
    'adeunis-ftd-23754': 'wa',
    'miromico-007a4f': 'jldp',
    'miromico-007a2f': 'jldp',
    'miromico-007a2e': 'jldp',
    'miromico-007a2d': 'jldp',
    'miromico-007a2c': 'jldp',
    'miromico-007a2b': 'sci',
    'miromico-007a2a': 'sci',
    'miromico-007a29': 'jldp',
    'miromico-007a26': 'jldp',
    'miromico-007a30': 'jldp',
    'miromico-007a25': 'jldp',
    '9876b6115b69': 'staten',
    'raspverry_pi_ranger': 'falk',
    '3939353476387418': 'falk',
    'feather_ranger': 'falk',
    'feather_ranger_2': 'falk',
    'feather-ranger-f3c3': 'falk',
    'oyster-005d93': 'sci',
    'jldp-oyster-c7a8': 'jldp',
    'jldp-oyster-c7a0': 'jldp',
    'tnc-mmico-cargo-007a4f': 'jldp',
    'tnc-mmico-tracker2-007a4e': 'jldp',
    'tnc-adeunis-ftd-0235a1': 'jldp'}

LABEL_LOOKUP = {
    'adeunis-ftd-23754': 'Mark Goering tester',
    'feather-ranger-f3c3': 'The NO device',
    'miromico-007a4f': 'JLDP test device (lost)',
    'miromico-007a2f': 'JLDP #4 flatbed',
    'miromico-007a2e': 'JLDP #7 Silverado',
    'miromico-007a2d': 'JLDP #10 flatbed',
    'miromico-007a2c': 'JLDP blue UTV',
    'miromico-007a29': 'JLDP #2 Colorado',
    'miromico-007a26': 'JLDP #5 flatbed',
    'miromico-007a30': 'JLDP green UTV',
    'miromico-007a25': 'JLDP black utv',
    'oyster-005d93': 'SCI Blue 4runner',
    'jldp-oyster-c7a8': 'JLDP Green Honda OHV',
    'jldp-oyster-c7a0': 'JLDP Blue Kawasaki OHV',
    'tnc-adeunis-ftd-0235a1': 'JLDP Kelly signal tester'}

GATEWAY_LOOKUP = {
    'dragino-dlos8-28260': 'TIS Dragino Mark home',
    'c0ee40ffff296af5': 'Falk Laird home',
    'laird-rg191-296af5': 'Falk Laird home',
    'laird-rg1xx-293ebd': 'SCI Laird Diablo',
    'laird-rg1xx-294d3c': 'SCI Laird Main Ranch',
    'laird-rg1xx-294f2e': 'Staten Laird Office',
    'laird_rg191_outdoor_staten': 'Staten Laird Office',
    'lorix-one-0a8a23': 'TIS LorixOne Spare',
    'lorix-one-0b6395': 'SCI LorixOne Centinela',
    'lorix-one-206f01': 'JLDP LorixOne Sutter Peak',
    'lorix-one-207446': 'JLDP LorixOne Jamala HQ',
    'lorix-one-20d3a6': 'JLDP LorixOne Relay Ridge',
    'lorix-one-207d24': 'SCI LorixOne Valley Peak',
    'lorix-one-20bb57': 'JLDP Bunker Hill',
    'lorix-one-2ddd4e': 'JLDP LorixOne unplaced',
    'lorix-one-2ef2c4': 'JLDP LorixOne Kelly home',
    'lorix-one-2e1135': 'JLDP LorixOne unplaced',
    'lorix-one-2eb3b1': 'SCI LorixOne Diablo 2',
    'lorix-one-2e901c': 'JLDP LorixOne unplaced',
    'lorix-one-2de697': 'Maui LorixOne Waikamoi',
    'lorix-one-2e89bd': 'JLDP LorixOne Cojo Water tanks',
    'eui-58a0cbfffe801686': 'TTN indoor starter'}


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
    properties = RECORD_TEMPLATE
    # copy old data
    for item in properties:
        properties[item] = feature.get('properties', {}).get(item)
    # assign labels
    device = properties.get('dev', '')
    properties['label'] = LABEL_LOOKUP.get(device) or device
    properties['domain'] = DOMAIN_LOOKUP.get(device, '')
    for item in ('1', '2', '3', '4', '5'):
        gateway = properties.get('gateway_' + item)
        properties['gw_label_' + item] = GATEWAY_LOOKUP.get(gateway) or gateway
    # deal with date
    time_dic = determine_time(properties)
    properties.update(time_dic)
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
            'time', 'received_t']:
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
            ('GlobalID', 'str:38'),
            ('rec_tm_utc', 'str:20'),
            ('pl_tm_utc', 'str:20'),
            ('tr_tm_utc', 'str:20'),
            ('buffered', 'int'),
            ('tm_valid', 'int')
        ] + list(old_properties.items()) + new_gw_info + [
        # move these legacy fields to the end for future removal
            ('snr', 'str:10'), ('time', 'str:20'), ('received_t', 'str:20') ]
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
