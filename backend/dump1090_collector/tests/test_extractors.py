import logging
from unittest import mock
from django.test import TestCase
from django.utils import timezone
from dump1090_collector.services.extractors import (
    extract_aircraft_info,
    extract_callsign_info,
    extract_flight_data,
)

class ExtractorsTestCase(TestCase):
    def test_extract_aircraft_info_valid_data(self):
        adsbdb_aircraft_data = {
            'response': {
                'aircraft': {
                    'registration': 'N12345',
                    'type': 'Boeing 737',
                    'icao_type': 'B737',
                }
            }
        }
        expected_aircraft_info = {
            'registration': 'N12345',
            'type': 'Boeing 737',
            'icao_type': 'B737',
        }
        self.assertEqual(extract_aircraft_info(adsbdb_aircraft_data), expected_aircraft_info)

    def test_extract_aircraft_info_invalid_data(self):
        # Test with invalid input types and None/unknown responses
        self.assertEqual(extract_aircraft_info("not a dict"), {})
        self.assertEqual(extract_aircraft_info({'response': "unknown aircraft"}), {})
        self.assertEqual(extract_aircraft_info({'response': None}), {})
        self.assertEqual(extract_aircraft_info({'response': 123}), {})
        self.assertEqual(extract_aircraft_info({'response': []}), {})
        self.assertEqual(extract_aircraft_info({'response': {}}), {})

    def test_extract_callsign_info_valid_data(self):
        adsbdb_callsign_data = {
            'response': {
                'airline': 'United',
                'flightroute': {'origin': 'JFK'}
            }
        }
        expected_callsign_info = {
            'airline': 'United',
            'flightroute': {'origin': 'JFK'}
        }
        self.assertEqual(extract_callsign_info(adsbdb_callsign_data), expected_callsign_info)

    def test_extract_callsign_info_invalid_data(self):
        # Test with invalid input types and None/unknown responses
        self.assertEqual(extract_callsign_info("not a dict"), {})
        self.assertEqual(extract_callsign_info({'response': "unknown callsign"}), {})
        self.assertEqual(extract_callsign_info({'response': None}), {})
        self.assertEqual(extract_callsign_info({'response': 123}), {})
        self.assertEqual(extract_callsign_info({'response': []}), {})
        self.assertEqual(extract_callsign_info({'response': {}}), {})

    def test_extract_flight_data_valid_data(self):
        flight_data = {
            'hex': 'ABCDEF',
            'squawk': 1200,
            'flight': 'UAL123',
            'lat': 34.0522,
            'lon': -118.2437,
            'validposition': 1,
            'altitude': 30000,
            'vert_rate': 1000,
            'track': 270,
            'validtrack': 1,
            'speed': 450,
            'messages': 50,
            'seen': 10,
        }
        extracted_data = extract_flight_data(flight_data)
        self.assertEqual(extracted_data['flight_hex'], 'ABCDEF')
        self.assertEqual(extracted_data['squawk'], 1200)
        self.assertEqual(extracted_data['flight_callsign'], 'UAL123')
        self.assertEqual(extracted_data['lat'], 34.0522)
        self.assertEqual(extracted_data['lon'], -118.2437)
        self.assertTrue(extracted_data['valid_position'])
        self.assertEqual(extracted_data['altitude'], 30000)
        self.assertEqual(extracted_data['vertical_rate'], 1000)
        self.assertEqual(extracted_data['track'], 270)
        self.assertTrue(extracted_data['valid_track'])
        self.assertEqual(extracted_data['speed_in_knots'], 450)
        self.assertEqual(extracted_data['messages_received'], 50)
        self.assertEqual(extracted_data['seen'], 10)
        self.assertIsInstance(extracted_data['timestamp'], timezone.datetime)

