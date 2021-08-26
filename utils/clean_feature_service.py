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
    service.delete_records(sql_query='dev IS NULL')
    # service.delete_records(sql_query='received_t > "2021-08-26 15:33:00"')


if __name__ == '__main__':
    main()
