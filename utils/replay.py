"""
Replay data from S3
"""
import argparse
from datetime import datetime
import json
import os
import sys
import boto3
# add path for AGO access
# sys.path.append(os.path.abspath(os.path.join('..', 'webhook', 'src')))
# import ago
import requests


BUCKET = 'iot-rawdata'
PREFIX = 'lorawan/tnc/{app}/{dev}'
TIME_SCHEMA = '%Y-%m-%dT%H:%MZ'
KEY_TIME_SCHEMA = '%Y-%m-%d'
LORA_TIME_SCHEMA = '%Y-%m-%dT%H:%M:%S.%fZ'
API_ENDPOINT = 'https://eezdsmxmh1.execute-api.us-west-1.amazonaws.com/dev/hook'


def post_record(args, record):
    headers = {'x-api-key': args.key}
    res = requests.post(API_ENDPOINT, data=record, headers=headers)
    print(res)


def get_date_from_key(key):
    # TODO improve with regex
    return key[-14:-4]


def time_from_arg(args_timestring):
    try:
        return datetime.strptime(args_timestring, TIME_SCHEMA)
    except (TypeError, ValueError):
        return None


def timestring_for_key(args_timestring):
    value = time_from_arg(args_timestring)
    if value:
        return datetime.strftime(value, KEY_TIME_SCHEMA)
    return None


def filename_generator(args, client):
    after = timestring_for_key(args.after)
    before = timestring_for_key(args.before)
    if (args.before and not before) or (args.after and not after):
        print('Invalid date format')
        sys.exit(1)
    objects = client.list_objects_v2(Bucket=BUCKET,
        Prefix=PREFIX.format(app=args.application, dev=args.device))
    for object in objects.get('Contents', []):
        key = object.get('Key')
        if 'hash' not in key:
            date = get_date_from_key(key)
            if (not after or date>=after) and (not before or date<=before):
                yield key


def extract_received_t(line):
    dic = json.loads(line.decode('utf-8'))
    time_string = dic.get('received_at')
    # this is an annoying workaround because Python time conversion cannot
    # handle microsecs
    return datetime.strptime(time_string[0:19], LORA_TIME_SCHEMA[0:17])


def record_generator(args, client):
    for key in filename_generator(args, client):
        before = time_from_arg(args.before)
        after = time_from_arg(args.after)
        obj = client.get_object(Bucket=BUCKET, Key=key)
        for line in obj.get('Body').read().split(b'\n'):
            if line:
                received = extract_received_t(line)
                if (not before or received < before) and (not after or received > after):
                    print(args.application, args.device, received)
                    yield line


def main(args):
    client = boto3.client('s3')
    ct = 0
    for record in record_generator(args, client):
        post_record(args, record)
        ct += 1
    print(ct, 'records transferred')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Replaying data from S3 to AGO')
    parser.add_argument(
        '-a', '--application', help='TTI application name', type=str,
        default=None)
    parser.add_argument(
        '-d', '--device', help='Device name', type=str, default=None)
    parser.add_argument(
        '-k', '--key', help='AWS API key', type=str, default=None)
    parser.add_argument(
        '--after', help='After date YYYY-MM-DDTHH:MM:SSZ', default=None)
    parser.add_argument(
        '--before', help='Before date YYYY-MM-DDTHH:MM:SSZ', default=None)
    parser.add_argument(
        '--limit', help='Number of records', default=None)
    args = parser.parse_args()
    main(args)
