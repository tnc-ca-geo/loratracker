from unittest import TestCase
from utils.clean_shp_2022_08_15 import determine_time


class TestTimeTransformations(TestCase):

    def test_current_w_payload_time(self):
        test_data = {
            'time': '2022-01-01 18:00:00', 'received_t': '2022-01-01 10:01:00'}
        self.assertEqual(determine_time(test_data), {
            'buffered': False, 'pl_tm_utc': '2022-01-01 18:00:00',
            'rec_tm_utc': '2022-01-01 18:01:00',
            'tr_tm_utc': '2022-01-01 18:00:00', 'tm_valid': True})

    def test_current_wo_payload_time_after_2021(self):
        test_data = {
            'time': None, 'received_t': '2022-01-01 10:01:00'}
        self.assertEqual(determine_time(test_data), {
            'buffered': False, 'tm_valid': True, 'pl_tm_utc': None,
            'rec_tm_utc': '2022-01-01 18:01:00',
            'tr_tm_utc': '2022-01-01 18:01:00'})

    def test_current_w_payload_time_match(self):
        test_data = {
            'time': '2022-01-01 18:00:00', 'received_t': '2022-01-01 10:00:00'}
        self.assertEqual(determine_time(test_data), {
            'buffered': False, 'tm_valid': True, 'pl_tm_utc': None,
            'rec_tm_utc': '2022-01-01 18:00:00',
            'tr_tm_utc': '2022-01-01 18:00:00'})

    def test_w_8_hours_offset(self):
        test_data = {
            'time': '2021-01-01 10:00:00', 'received_t': '2021-01-01 18:01:00'}
        res = determine_time(test_data)
        print(res)
        self.assertEqual(determine_time(test_data), {
            'buffered': False, 'pl_tm_utc': '2021-01-01 18:00:00',
            'rec_tm_utc': '2021-01-01 18:01:00',
            'tr_tm_utc': '2021-01-01 18:00:00', 'tm_valid': True})

    def test_w_8_hours_offset_time_match(self):
        test_data = {
            'time': '2021-01-01 10:00:00', 'received_t': '2021-01-01 18:00:00'}
        self.assertEqual(determine_time(test_data), {
            'buffered': False, 'pl_tm_utc': None,
            'rec_tm_utc': '2021-01-01 18:00:00',
            'tr_tm_utc': '2021-01-01 18:00:00', 'tm_valid': True})

    def test_switched_with_8_hours_offset(self):
        test_data = {
            'time': '2021-01-01 10:02:00', 'received_t': '2021-01-01 18:01:00'}

        self.assertEqual(determine_time(test_data), {
            'buffered': False, 'pl_tm_utc': '2021-01-01 18:01:00',
            'rec_tm_utc': '2021-01-01 18:02:00',
            'tr_tm_utc': '2021-01-01 18:01:00', 'tm_valid': True})

    def test_offset_w_daylight(self):
        test_data = {
            'time': '2021-01-01 10:00:00', 'received_t': '2021-01-01 18:01:00'}
        res = determine_time(test_data)
        print(res)
        self.assertEqual(determine_time(test_data), {
            'buffered': False, 'pl_tm_utc': '2021-01-01 18:00:00',
            'rec_tm_utc': '2021-01-01 18:01:00',
            'tr_tm_utc': '2021-01-01 18:00:00', 'tm_valid': True})

    def test_w_7_hours_offset(self):
        test_data = {
            'time': '2021-04-01 10:00:00', 'received_t': '2021-04-01 17:01:00'}
        res = determine_time(test_data)
        print(res)
        self.assertEqual(determine_time(test_data), {
            'buffered': False, 'pl_tm_utc': '2021-04-01 17:00:00',
            'rec_tm_utc': '2021-04-01 17:01:00',
            'tr_tm_utc': '2021-04-01 17:00:00', 'tm_valid': True})
