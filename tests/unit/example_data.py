"""
Some data to play around with
"""
# standard library
import json


lorawan_webhook_example = {
    'resource': '/hook',
    'path': '/hook',
    'httpMethod': 'POST',
    'headers': {},
    'multiValueHeaders': {},
    'queryStringParameters': None,
    'multiValueQueryStringParameters': None,
    'pathParameters': None,
    'stageVariables': None,
    'requestContext': {
        'resourcePath': '/hook',
        'httpMethod': 'POST',
        'requestTime': '25/Aug/2021:19:22:59 +0000',
        'path': '/dev/hook',
        'protocol': 'HTTP/1.1',
        'stage': 'dev',
        'requestTimeEpoch': 1629919379585,
        'domainName': 'fcf0szps28.execute-api.us-west-1.amazonaws.com',
        'apiId': 'fcf0szps28'},
    'body': json.dumps({
        "end_device_ids": {
            "device_id": "feather-ranger-f3c3",
            "application_ids": {
                "application_id": "test-n-ranging"},
            "dev_eui": "00C82EFB6B82F3C3",
            "dev_addr":"2602136F"},
        "correlation_ids": [],
        "received_at":"2021-08-25T19:22:59.136139872Z",
        "uplink_message": {
            "f_port":1,
            "f_cnt":5,
            "frm_payload":"LTEyMi4yNzU1NywgMzcuODQxODAsMjAyMS0wOC0yNSAxOToyMzowMAAA",
            "decoded_payload":{
                "latitudeDeg":37.8418,
                "longitudeDeg":-122.27557,
                "time":"2021-08-25 19:23:00"},
            "rx_metadata":[{
                "gateway_ids":{
                    "gateway_id":"laird-rg191-296af5",
                    "eui":"C0EE40FFFF296AF5"},
                "timestamp":26882812,
                "rssi":-48,
                "channel_rssi":-48,
                "snr":10,
                "uplink_token":"CiAKHgoSbGFpcmQtcmcxOTEtMjk2YWY1EgjA7kD//ylq9RD85egMGgwIkrGaiQYQyajUrwIg4NDckmQ=",
                "channel_index":7}],
            "settings":{
                "data_rate":{
                    "lora":{
                        "bandwidth":125000,
                        "spreading_factor":7}},
                "data_rate_index":3,
                "coding_rate":"4/5",
                "frequency":"905300000",
                "timestamp":26882812},
            "received_at":"2021-08-25T19:22:58.780515972Z",
            "consumed_airtime":"0.107776s",
            "locations":{
                "frm-payload":{
                    "latitude":37.8418,
                    "longitude":-122.27557,
                    "source":"SOURCE_GPS"}},
            "network_ids":{
                "net_id":"000013",
                "tenant_id":"tnc",
                "cluster_id":"tti-ch-nam1"}},
            'isBase64Encoded': False})}
