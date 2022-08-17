"""
Remove invalid data from the feature service
"""
# standard library
import os
import sys
# add path, somewhat messy but retain clean project structure for the function
# code deployed to AWS Lambda
sys.path.insert(
    0, os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'webhook')))
from src.ago import FeatureService


def main():
    service = FeatureService()
    res = service.delete_records(
        sql_query=
            'received_t > \'2022-08-04 00:00:00\' AND '
            'received_t < \'2022-08-05 00:00:00\' AND '
            'dev = \'tnc-adeunis-ftd-0235a1\'')
    print(res.content)


if __name__ == '__main__':
    main()
