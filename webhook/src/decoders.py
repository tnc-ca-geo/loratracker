import base64
from datetime import datetime


NOT_A_LOCATION = {'status': 'error', 'msg': 'not a location message'}


def adeunis(payload, port=0):
    # https://www.adeunis.com/wp-content/uploads/2020/03/User_Guide_FTD_LoRaWAN_US902-928_V1.0.1.pdf
    # first we have to determine in which frame we are in, only the first
    # one has location
    bytes = base64.b64decode(payload)
    if bytes[0] & 0b01110000:
        latDeg = ((bytes[1] & 0xf0) >> 4) * 10 + (bytes[1] & 0xf)
        latMin = (
            ((bytes[2] & 0xf0) >> 4) * 10 + (bytes[2] & 0xf) +
            ((bytes[3] & 0xf0) >> 4) * .1 + (bytes[3] & 0xf) * .01  +
            ((bytes[4] & 0xf0) >> 4) * .001 + (bytes[4] & 0xf) * .0001 +
            ((bytes[5] & 0xf0) >> 4) * .00001)/60
        sign = -1 if bytes[5] & 0x1 else 1
        lat = int(((latDeg * sign) + (latMin * sign)) * 100000)/100000
        lonDeg = (
            ((bytes[5] & 0xf0) >> 4) * 100 + (bytes[5] & 0xf) * 10 +
            ((bytes[6] & 0xf0) >> 4))
        lonMin = (
            (bytes[6] & 0xf) * 10 + ((bytes[7] & 0xf0) >> 4) +
            (bytes[7] & 0xf) * .1 + ((bytes[8] & 0xf0) >> 4) * .01)/60
        sign = -1 if bytes[8] & 0x1 else 1
        lon = int((lonDeg + lonMin) * 100000)/100000 * sign
        reception = ['', 'good', 'average', 'poor'][(bytes[9] & 0xf0) >> 4]
        satellites = (bytes[9] & 0xf)
        return {
            'triggeredByAccelerometer': bytes[0] & 0x4 != 0,
            'triggeredByPushButton': bytes[0] & 0x8 != 0,
            'gpsAvailable': bytes[0] & 0x16 != 0,
            'x': lon,
            'y': lat,
            'receptionQuality': reception,
            'numberOfSatellites': satellites,
            'status': 'ok'}
    return NOT_A_LOCATION


def feather_ranger_f3c3(payload, port=0):
    text = base64.b64decode(payload).decode('utf-8')
    fields = text.split(',')
    return {
        'x': float(fields[0]),
        'y': float(fields[1]),
        'time': datetime.strptime(fields[2][0:18], '%Y-%m-%d %H:%M:%S'),
        'status': 'ok'}


def miromico_cargo(payload, port=0):
    # standard location message on port 103
    # https://docs.miromico.ch/tracker/dev/
    if port == 103:
        bytes = base64.b64decode(payload)
        dat = (bytes[ 0] << 24 | bytes[ 1] << 16 | bytes[ 2] << 8 | bytes[ 3])
        tim = (bytes[ 4] << 24 | bytes[ 5] << 16 | bytes[ 6] << 8 | bytes[ 7])
        time = datetime(
            year = dat % 100 + 2000, month = int(dat/100) % 100,
            day = int(dat/10000), hour = int(tim/10000),
            minute = int(tim/100) % 100, second = tim % 100)
        lat = (bytes[ 8] << 24 | bytes[ 9] << 16 | bytes[10] << 8 | bytes[11])
        lon = (bytes[12] << 24 | bytes[13] << 16 | bytes[14] << 8 | bytes[15])
        alt = (bytes[16] << 24 | bytes[17] << 16 | bytes[18] << 8 | bytes[19])
        if lat > 0x7FFFFFFF: lat = -(0xFFFFFFFF - lat + 1)
        if lon > 0x7FFFFFFF: lon = -(0xFFFFFFFF - lon + 1)
        if alt > 0x7FFFFFFF: alt = -(0xFFFFFFFF - alt + 1)
        return {
            'time': time, 'status': 'ok', 'x': lon/100000, 'y': lat/100000,
            'altM': alt/100}
    return NOT_A_LOCATION


def oyster(payload, port=0):
    """
    Oyster payload decoder. Currently incomplete implementation, only port 1
    messages. There is a port 4 location message that uses less precision.
    """
    bytes = base64.b64decode(payload)
    ret = {}
    location = {}
    warnings = {}
    if port == 1:
        latitude = (
            bytes[0] + bytes[1] * 256 + bytes[2] * 65536 +
            bytes[3] * 16777216)
        if latitude >= 0x80000000:
            latitude -= 0x100000000
        latitude /= 1e7
        longitude = (
            bytes[4] + bytes[5] * 256 + bytes[6] * 65536 +
            bytes[7] * 16777216)
        if longitude >= 0x80000000:
            longitude -= 0x100000000
        longitude /= 1e7
        return {
            'type': 'position', 'status': 'ok', 'inTrip': bytes[8] & 0x1 != 0,
            'fixFailed':  bytes[8] & 0x2 != 0,
            'batV': int(bytes[10] * 0.025 * 100)/100,
            'x': longitude, 'y': latitude, 'heading': (bytes[8] >> 2) * 5.625,
            'speedKmh': bytes[9]}
    return NOT_A_LOCATION
