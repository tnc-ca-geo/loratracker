from datetime import datetime
import os
import sys
from unittest import TestCase
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(root, 'webhook'))
from webhook.src import decoders


# TODO: add tests and handling for decoder errors
class TestDecoders(TestCase):

    def test_adeunis(self):
        # expected 47.6789, -122.39283333333333
        payload_example = b'EEdAc0ASIjVxJA=='
        self.assertEqual(
        decoders.adeunis(payload_example), {
            'triggeredByAccelerometer': False, 'triggeredByPushButton': False,
            'numberOfSatellites': 4, 'gpsAvailable': True, 'status': 'ok',
            'x': -122.39283, 'y': 47.6789, 'receptionQuality': 'average'})

    def test_adeunis_fail(self):
        # different message type
        payload_example = 'D/////A='
        self.assertEqual(
            decoders.adeunis(payload_example), {
                'status': 'error', 'msg': 'not a location message'})

    def test_feather_ranger_f3c3(self):
        payload_example = (
            b'LTExOS43MTY5NSwgMzMuOTk1OTcsMjAyMi0wNS0xMyAyMzo1OTozMQAA')
        self.assertEqual(
            decoders.feather_ranger_f3c3(payload_example), {
                'x': -119.71695, 'y': 33.99597,
                'time': datetime(2022, 5, 13, 23, 59, 3), 'status': 'ok'})

    def test_miromico_cargo(self):
        # expected 34.45691, -120.45353
        payload_example = b'AADIFQAAZTcANJO7/0gz1wAAAu4='
        self.assertEqual(
            decoders.miromico_cargo(payload_example, 103), {
                'x': -120.45353, 'y': 34.45691, 'status': 'ok', 'altM': 7.5,
                'time': datetime(2021, 12, 5, 2, 59, 11)})

    def test_miromico_fail(self):
        payload_example = b'AADIFQAAZTcANJO7/0gz1wAAAu4='
        self.assertEqual(
            decoders.miromico_cargo(payload_example, 101), {
            'status': 'error', 'msg': 'not a location message'})

    def test_oyster(self):
        payload_example = b'osuSFIeBM7haAK4='
        self.assertEqual(
            decoders.oyster(payload_example, 1), {
                'type': 'position', 'status': 'ok', 'inTrip': False,
                'fixFailed': True, 'batV': 4.35,  'y': 34.5164706,
                'x': -120.4584057, 'heading': 123.75, 'speedKmh': 0})

    def test_oyster_fail(self):
        payload_example = b'osuSFIeBM7haAK4='
        # error depends on requested port
        self.assertEqual(
            decoders.oyster(payload_example, 2), {
                'status': 'error', 'msg': 'not a location message'})
