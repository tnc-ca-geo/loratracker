"""
Create a new layer from a current downloaded version
"""
from copy import deepcopy
import os
import sys
import fiona


BASE_PATH = os.path.abspath(os.path.join('..', '..', 'data'))
DATA = os.path.join(BASE_PATH, 'lora_tracking', 'lora_tracking.shp')
NEW = os.path.join(BASE_PATH, 'lora_tracking_2')


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
    'tnc-adeunis-ftd-0235a1': 'jldp'
}

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
    'tnc-adeunis-ftd-0235a1': 'JLDP Kelly signal tester',
}


def clean(feature):
    new = deepcopy(feature)
    properties = new['properties']
    properties['gateway_1'] = feature['properties']['gateway']
    properties.pop('gateway')
    properties['rssi_1'] = feature['properties']['rssi']
    properties.pop('rssi')
    for item in ['2', '3', '4', '5']:
        properties['gateway_' + item] = None
        properties['rssi_' + item] = None
    try:
        properties['label'] = LABEL_LOOKUP[properties['dev']]
    except KeyError:
        properties['label'] = properties['dev']
    try:
        properties['domain'] = DOMAIN_LOOKUP[properties['dev']]
    except KeyError:
        print(feature)
        sys.exit(1)
    return new


def validate(feature):
    if not feature['properties']['dev']:
        return False
    return True


def main():
    count = 0
    with fiona.open(DATA) as shapes:
        schema = shapes.schema
        schema['properties']['label'] = 'str:80'
        schema['properties']['domain'] = 'str:80'
        schema['properties'].pop('gateway')
        schema['properties'].pop('rssi')
        for item in ['1', '2', '3', '4', '5']:
            schema['properties']['gateway_' + item] = 'str:80'
            schema['properties']['rssi_' + item] = 'str:80'
        metadata = {
            'driver': shapes.driver, 'crs': shapes.crs, 'schema': schema}
        with fiona.open(NEW, 'w', **metadata) as dest:
            for shape in shapes:
                if validate(shape):
                    count += 1
                    new_shape = clean(shape)
                    dest.write(new_shape)
    print('DONE', count, 'features')


if __name__ == '__main__':
    main()
