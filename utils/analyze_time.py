from datetime import datetime, timedelta
from dateutil import tz
import os
import fiona


UTC_ZONE = tz.gettz('UTC')
BASE_PATH = os.path.abspath(os.path.join('..', '..', 'data'))
DATA = os.path.join(BASE_PATH, 'lora_tracking_2a', 'lora_tracking_2.shp')
NEW = os.path.join(BASE_PATH, 'lora_tracking_3')
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def main():
    distribution = {}
    with fiona.open(NEW) as features:
        for feature in features:
            received = feature.get('properties', {}).get('rec_tm_utc')
            payload = feature.get('properties', {}).get('pl_tm_utc')
            received_time = datetime.strptime(
                received, TIME_FORMAT).replace(tzinfo=UTC_ZONE)
            payload_time = datetime.strptime(
                payload, TIME_FORMAT).replace(tzinfo=UTC_ZONE) if payload else None
            if payload_time:
                print(received_time - payload_time)
            hour = received_time.hour
            year = received_time.year
            if not year in distribution:
                distribution[year] = {}
            if not hour in distribution[year]:
                distribution[year][hour] = 0
            distribution[year][hour] += 1
    print(distribution)


if __name__ == '__main__':
    main()
