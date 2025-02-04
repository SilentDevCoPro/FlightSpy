from django.test import TestCase
from django.utils import timezone
from dump1090_collector.models import Aircraft, Airline, Airport, FlightData
from dump1090_collector.services.services import get_or_create_aircraft, get_or_create_airline, get_or_create_airport
from dump1090_collector.services.extractors import extract_aircraft_info, extract_callsign_info, extract_flight_data
from dump1090_collector.services.store_data import store_data

class ServicesTest(TestCase):
    def test_get_or_create_aircraft_with_registration(self):
        aircraft_info = {
            'registration': 'ABC123',
            'type': 'Type1',
            'icao_type': 'Icao1',
            'manufacturer': 'Manufacturer1',
            'mode_s': 'ModeS1',
            'registered_owner_country_iso_name': 'US',
            'registered_owner_country_name': 'United States',
            'registered_owner_operator_flag_code': 'Code1',
            'registered_owner': 'Owner1',
            'url_photo': 'http://photo.url',
            'url_photo_thumbnail': 'http://thumb.url',
        }
        flight_hex = 'HEX123'
        aircraft = get_or_create_aircraft(aircraft_info, flight_hex)
        self.assertEqual(aircraft.registration, 'ABC123')
        self.assertEqual(aircraft.hex_id, flight_hex)
        updated_info = aircraft_info.copy()
        updated_info['manufacturer'] = 'Manufacturer2'
        aircraft_updated = get_or_create_aircraft(updated_info, flight_hex)
        self.assertEqual(aircraft_updated.manufacturer, 'Manufacturer2')
        # Create a duplicate to test warning path
        Aircraft.objects.create(registration='ABC123', hex_id='HEX999')
        aircraft_dup = get_or_create_aircraft(aircraft_info, flight_hex)
        self.assertEqual(aircraft_dup.registration, 'ABC123')

    def test_get_or_create_aircraft_without_registration(self):
        aircraft_info = {
            'registration': '',
            'type': 'Type1',
            'icao_type': 'Icao1',
            'manufacturer': 'Manufacturer1',
            'mode_s': 'ModeS1',
            'registered_owner_country_iso_name': 'US',
            'registered_owner_country_name': 'United States',
            'registered_owner_operator_flag_code': 'Code1',
            'registered_owner': 'Owner1',
            'url_photo': 'http://photo.url',
            'url_photo_thumbnail': 'http://thumb.url',
        }
        flight_hex = 'HEX456'
        aircraft = get_or_create_aircraft(aircraft_info, flight_hex)
        self.assertEqual(aircraft.registration, '')
        self.assertEqual(aircraft.hex_id, flight_hex)

    def test_get_or_create_airline(self):
        airline_info = {
            'name': 'Airline1',
            'icao': 'ICAO1',
            'iata': 'IATA1',
            'country': 'Country1',
            'country_iso': 'C1',
            'callsign': 'Call1',
        }
        airline = get_or_create_airline(airline_info)
        self.assertEqual(airline.name, 'Airline1')
        duplicate_airline = get_or_create_airline(airline_info)
        self.assertEqual(airline.id, duplicate_airline.id)

    def test_get_or_create_airport(self):
        airport_info = {
            'iata_code': 'IATA1',
            'icao_code': 'ICAO1',
            'name': 'Airport1',
            'country_iso_name': 'US',
            'country_name': 'United States',
            'elevation': 100,
            'latitude': 40.0,
            'longitude': -75.0,
            'municipality': 'City1',
        }
        airport = get_or_create_airport(airport_info)
        self.assertEqual(airport.iata_code, 'IATA1')
        airport2 = get_or_create_airport(airport_info)
        self.assertEqual(airport.id, airport2.id)

class ExtractorsTest(TestCase):
    def test_extract_aircraft_info_valid(self):
        data = {
            'response': {
                'aircraft': {
                    'registration': 'ABC123',
                    'type': 'Type1'
                }
            }
        }
        result = extract_aircraft_info(data)
        self.assertEqual(result.get('registration'), 'ABC123')
        self.assertEqual(result.get('type'), 'Type1')

    def test_extract_aircraft_info_invalid(self):
        result = extract_aircraft_info("not a dict")
        self.assertEqual(result, {})

    def test_extract_callsign_info_valid(self):
        data = {
            'response': {
                'flightroute': {
                    'airline': {'name': 'Airline1'},
                    'origin': {'iata_code': 'IATA1', 'icao_code': 'ICAO1', 'name': 'Origin'},
                    'destination': {'iata_code': 'IATA2', 'icao_code': 'ICAO2', 'name': 'Destination'},
                }
            }
        }
        result = extract_callsign_info(data)
        self.assertIn('flightroute', result)

    def test_extract_callsign_info_invalid(self):
        result = extract_callsign_info(123)
        self.assertEqual(result, {})

    def test_extract_flight_data(self):
        flight = {
            'hex': 'HEX789',
            'squawk': 100,
            'flight': 'FL123',
            'lat': 50.0,
            'lon': 8.0,
            'validposition': 1,
            'altitude': 30000,
            'vert_rate': 500,
            'track': 90,
            'validtrack': 1,
            'speed': 450,
            'messages': 20,
            'seen': 5,
        }
        result = extract_flight_data(flight)
        self.assertEqual(result["flight_hex"], "HEX789")
        self.assertEqual(result["squawk"], 100)
        self.assertEqual(result["flight_callsign"], "FL123")
        self.assertEqual(result["lat"], 50.0)
        self.assertEqual(result["lon"], 8.0)
        self.assertTrue(result["valid_position"])
        self.assertEqual(result["altitude"], 30000)
        self.assertEqual(result["vertical_rate"], 500)
        self.assertEqual(result["track"], 90)
        self.assertTrue(result["valid_track"])
        self.assertEqual(result["speed_in_knots"], 450)
        self.assertEqual(result["messages_received"], 20)
        self.assertEqual(result["seen"], 5)
        self.assertIsNotNone(result["timestamp"])

class StoreDataTest(TestCase):
    def test_store_data(self):
        flight = {
            'hex': 'HEX101',
            'squawk': 200,
            'flight': 'FL101',
            'lat': 55.0,
            'lon': 9.0,
            'validposition': 1,
            'altitude': 32000,
            'vert_rate': 600,
            'track': 180,
            'validtrack': 1,
            'speed': 500,
            'messages': 30,
            'seen': 10,
        }
        adsbdb_aircraft_data = {
            'response': {
                'aircraft': {
                    'registration': 'REG101',
                    'type': 'Type101',
                    'icao_type': 'ICAO101',
                    'manufacturer': 'Manu101',
                    'mode_s': 'ModeS101',
                    'registered_owner_country_iso_name': 'GB',
                    'registered_owner_country_name': 'United Kingdom',
                    'registered_owner_operator_flag_code': 'Flag101',
                    'registered_owner': 'Owner101',
                    'url_photo': 'http://photo101.url',
                    'url_photo_thumbnail': 'http://thumb101.url',
                }
            }
        }
        adsbdb_callsign_data = {
            'response': {
                'flightroute': {
                    'airline': {
                        'name': 'Airline101',
                        'icao': 'ICAO101',
                        'iata': 'IATA1',  # changed to a value within 5 characters
                        'country': 'Country101',
                        'country_iso': 'C101',
                        'callsign': 'Call101',
                    },
                    'origin': {
                        'iata_code': 'ORI',  # changed from 'ORI101'
                        'icao_code': 'ORICAO101',
                        'name': 'Origin Airport',
                        'country_iso_name': 'GB',
                        'country_name': 'United Kingdom',
                        'elevation': 50,
                        'latitude': 51.5,
                        'longitude': -0.1,
                        'municipality': 'City101',
                    },
                    'destination': {
                        'iata_code': 'DES',  # changed from 'DES101'
                        'icao_code': 'DESICAO101',
                        'name': 'Destination Airport',
                        'country_iso_name': 'FR',
                        'country_name': 'France',
                        'elevation': 100,
                        'latitude': 48.8,
                        'longitude': 2.3,
                        'municipality': 'City102',
                    },
                }
            }
        }
        flight_data = store_data(flight, adsbdb_aircraft_data, adsbdb_callsign_data)
        self.assertEqual(flight_data.flight_callsign, 'FL101')
        self.assertEqual(flight_data.squawk_code, 200)
        self.assertEqual(flight_data.latitude, 55.0)
        self.assertEqual(flight_data.longitude, 9.0)
        self.assertTrue(flight_data.valid_position)
        self.assertEqual(flight_data.altitude, 32000)
        self.assertEqual(flight_data.vertical_rate, 600)
        self.assertEqual(flight_data.track, 180)
        self.assertTrue(flight_data.valid_track)
        self.assertEqual(flight_data.speed_in_knots, 500)
        self.assertEqual(flight_data.messages_received, 30)
        self.assertEqual(flight_data.seen, 10)
        self.assertIsNotNone(flight_data.timestamp)
        self.assertEqual(flight_data.aircraft.registration, 'REG101')
        self.assertEqual(flight_data.aircraft.manufacturer, 'Manu101')
        self.assertEqual(flight_data.airline.name, 'Airline101')
        self.assertEqual(flight_data.origin_airport.iata_code, 'ORI')
        self.assertEqual(flight_data.destination_airport.iata_code, 'DES')

