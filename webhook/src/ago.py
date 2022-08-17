"""
Implement AGO workflow. AGO code has been copied from marshalling yard
"""
# standard library
from datetime import datetime, timedelta
import json
import os
from urllib.parse import urlparse, urlunparse
# third party
import requests
# layer
import lookups


CLIENT_ID = os.environ.get('AGO_CLIENT_ID', 'dN9MvQLsOn6w1Set')
CLIENT_SECRET = os.environ.get('AGO_CLIENT_SECRET')
TOKEN_URL = 'https://www.arcgis.com/sharing/rest/oauth2/token/'
AGO_INSTANCE_URL = 'https://services.arcgis.com/F7DSX1DSNSiWmOqh/'
FEATURE_SERVICE = (
    AGO_INSTANCE_URL + 'arcgis/rest/services/lora_tracking_3/FeatureServer/')


class TokenStore():
    """
    In this class tokens could be stored and recycled. Currently unused.
    """

    def __init__(self, name):
        pass

    def retrieve_token(self):
        return

    def store_token(self, token, unused, expires):
        pass


class TokenAuth(requests.auth.AuthBase):

    def __init__(self):
        self.token_url = None
        self.key = None
        self.password = None
        self.user = None
        self.label = None

    def renew_access_token(self, url, key, secret, pwd, user):
        """
        Implement authorization token request here and map terminology to
        store parameters below.
        """
        raise NotImplementedError

    def get_access_token(self, url, key, secret, pwd=None, user=None):
        """
        Interact with token store.
        """
        token = self.store.retrieve_token()
        if not token:
            resp = self.renew_access_token(url, key, secret, pwd, user)
            token = resp.get('access_token')
            self.store.store_token(token, None, resp.get('expires_in'))
            return {'token': token}
        return token


class ArcgisAuth(TokenAuth):
    """
    Implements ArcGIS authorization.
    """

    def __init__(self):
        self.token_url = TOKEN_URL
        self.client_id = CLIENT_ID
        self.secret = CLIENT_SECRET
        self.store = TokenStore('ago')

    def add_token_to_url(self, url, token):
        """
        Adds token to url. Is there a better way to that?
        """
        snippet = 'token=%s' % token
        url_fragment = '{}&{}' if '?' in url else '{}?{}'
        return url_fragment.format(url, snippet)

    def __call__(self, request):
        token = self.get_access_token(
            self.token_url, self.client_id, self.secret).get('token', None)
        request.url = self.add_token_to_url(request.url, token)
        return request

    def renew_access_token(self, url, key, secret, pwd, user):
        data = {
            'client_id': key, 'client_secret': secret,
            'grant_type': 'client_credentials'}
        res = requests.post(url, data)
        return json.loads(res.content)


class FeatureService():
    auth_class = ArcgisAuth

    def __init__(self, feature=FEATURE_SERVICE, layer=0):
        self.feature = feature
        self.layer = layer

    def post_records(self, records):
        url = '{}/{}/addFeatures/'.format(self.feature, self.layer)
        data = {
            'f': 'json',
            'features': format(json.dumps(records))}
        return requests.post(url, data=data, auth=self.auth_class())

    def delete_records(self, sql_query='', objectIds=None):
        """
        Delete features
        Args:
            sql_query (str): ArcMap SQL query, use single quotes for text
            objectIds (list of int): List of OBJECTIDS.
        Returns:
            requests object
        """
        url = '{}/{}/deleteFeatures/'.format(self.feature, self.layer)
        data = {'f': 'json'}
        if objectIds:
            data['objectIds'] = ','.join([str(item) for item in objectIds])
        if sql_query:
            data['where'] = sql_query
        return requests.post(url, data=data, auth=self.auth_class())


if __name__ == '__main__':
    service = FeatureService(FEATURE_SERVICE)
    geometry = {
        'x': 0, 'y': 0,
        'spatialReference': {'wkid': 4326}}
    records = [{'attributes': {}, 'geometry': geometry}]
    res = service.post_records(records)
    print(res.status_code, res.content)
