from django.test import TestCase

from dump1090_collector.models import Aircraft, Airline, Airport, FlightData

from dump1090_collector.flight_storage import (
    get_or_create_aircraft,
    get_or_create_airline,
    get_or_create_airport,
    store_data,
)


class TestFlightStorage(TestCase):
    def test_get_or_create_aircraft_with_registration(self):
        """Should create or return an aircraft based on registration"""
        aircraft_info = {
            'registration': 'N12345',
            'type': 'B737',
            'icao_type': 'B737',
            'manufacturer': 'Boeing',
        }
        flight_hex = 'abc123'

        aircraft = get_or_create_aircraft(aircraft_info, flight_hex)
        self.assertEqual(Aircraft.objects.count(), 1)
        self.assertEqual(aircraft.registration, 'N12345')
        self.assertEqual(aircraft.hex_id, 'abc123')
        self.assertEqual(aircraft.aircraft_type, 'B737')

        same_aircraft = get_or_create_aircraft(aircraft_info, flight_hex='zzz999')
        self.assertEqual(Aircraft.objects.count(), 1)
        self.assertEqual(same_aircraft.id, aircraft.id)

    def test_get_or_create_aircraft_without_registration(self):
        """Should fallback to hex_id if no registration is available"""
        aircraft_info = {
            'type': 'A320',
            'icao_type': 'A320',
            'manufacturer': 'Airbus',
        }
        flight_hex = 'def456'

        aircraft = get_or_create_aircraft(aircraft_info, flight_hex)
        self.assertEqual(Aircraft.objects.count(), 1)
        self.assertEqual(aircraft.hex_id, 'def456')
        self.assertEqual(aircraft.registration, '')
        self.assertEqual(aircraft.aircraft_type, 'A320')

    def test_get_or_create_airline(self):
        """Should create or get an airline record based on icao + iata"""
        airline_info = {
            'icao': 'UAL',
            'iata': 'UA',
            'name': 'United Airlines',
            'country': 'USA',
        }
        airline = get_or_create_airline(airline_info)
        self.assertEqual(Airline.objects.count(), 1)
        self.assertEqual(airline.icao, 'UAL')
        self.assertEqual(airline.iata, 'UA')
        self.assertEqual(airline.name, 'United Airlines')

        same_airline = get_or_create_airline(airline_info)
        self.assertEqual(Airline.objects.count(), 1)
        self.assertEqual(same_airline.id, airline.id)

    def test_get_or_create_airport(self):
        """Should return airport by iata_code or icao_code, else create new"""
        airport_info = {
            'iata_code': 'SFO',
            'icao_code': 'KSFO',
            'name': 'San Francisco Intl',
        }
        airport = get_or_create_airport(airport_info)
        self.assertEqual(Airport.objects.count(), 1)
        self.assertEqual(airport.iata_code, 'SFO')
        self.assertEqual(airport.icao_code, 'KSFO')
        self.assertEqual(airport.name, 'San Francisco Intl')

        same_airport_info = {
            'iata_code': 'SFO',
            'icao_code': 'KSFO',
            'name': 'Some Other Name',
        }
        same_airport = get_or_create_airport(same_airport_info)
        self.assertEqual(Airport.objects.count(), 1)
        self.assertEqual(same_airport.id, airport.id)

    def test_store_data_creates_flightdata(self):
        """store_data should create a FlightData row, linking foreign keys"""
        flight = {
            'hex': 'a1b2c3',
            'squawk': '1170',
            'flight': 'UAL1012',
            'lat': 37.615223,
            'lon': -122.389977,
            'validposition': 1,
            'altitude': 35000,
            'vert_rate': 100,
            'track': 90,
            'validtrack': 1,
            'speed': 500,
            'messages': 100,
            'seen': 2
        }
        adsbdb_aircraft_data = {
            'response': {
                'aircraft': {
                    'registration': 'N98765',
                    'type': 'B737',
                    'manufacturer': 'Boeing',
                }
            }
        }
        adsbdb_callsign_data = {
            'response': {
                'flightroute': {
                    'airline': {
                        'name': 'United Airlines',
                        'icao': 'UAL',
                        'iata': 'UA',
                    },
                    'origin': {
                        'iata_code': 'SFO',
                        'icao_code': 'KSFO',
                        'name': 'San Francisco Intl',
                    },
                    'destination': {
                        'iata_code': 'LAX',
                        'icao_code': 'KLAX',
                        'name': 'Los Angeles Intl',
                    },
                }
            }
        }

        flight_data = store_data(flight, adsbdb_aircraft_data, adsbdb_callsign_data)

        self.assertEqual(FlightData.objects.count(), 1)
        self.assertEqual(flight_data.flight_callsign, 'UAL1012')
        self.assertEqual(flight_data.altitude, 35000)
        self.assertTrue(flight_data.valid_position)

        # Check foreign keys
        self.assertIsNotNone(flight_data.aircraft)
        self.assertEqual(flight_data.aircraft.registration, 'N98765')
        self.assertIsNotNone(flight_data.airline)
        self.assertEqual(flight_data.airline.name, 'United Airlines')
        self.assertIsNotNone(flight_data.origin_airport)
        self.assertIsNotNone(flight_data.destination_airport)
        # Confirm airport codes
        self.assertEqual(flight_data.origin_airport.iata_code, 'SFO')
        self.assertEqual(flight_data.destination_airport.iata_code, 'LAX')
