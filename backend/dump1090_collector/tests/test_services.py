import logging
from django.test import TestCase
from dump1090_collector.models import Aircraft, Airline, Airport
from dump1090_collector.services.services import (
    get_or_create_aircraft,
    get_or_create_airline,
    get_or_create_airport,
)


class ServicesTestCase(TestCase):
    def test_get_or_create_aircraft_new(self):
        aircraft_info = {
            'registration': 'N12345',
            'type': 'Boeing 737',
            'icao_type': 'B737',
        }
        flight_hex = 'ABCDEF'
        aircraft_obj = get_or_create_aircraft(aircraft_info, flight_hex)
        self.assertEqual(Aircraft.objects.count(), 1)
        self.assertEqual(aircraft_obj.registration, 'N12345')
        self.assertEqual(aircraft_obj.hex_id, 'ABCDEF')

    def test_get_or_create_aircraft_existing(self):
        Aircraft.objects.create(registration='N12345', hex_id='ABCDEF', aircraft_type='Old Type')
        aircraft_info = {
            'registration': 'N12345',
            'type': 'Boeing 737',
            'icao_type': 'B737',
        }
        flight_hex = 'ABCDEF'
        aircraft_obj = get_or_create_aircraft(aircraft_info, flight_hex)
        self.assertEqual(Aircraft.objects.count(), 1)
        self.assertEqual(aircraft_obj.registration, 'N12345')
        self.assertEqual(aircraft_obj.aircraft_type, 'Boeing 737')

    def test_get_or_create_aircraft_no_registration(self):
        aircraft_info = {
            'type': 'Boeing 737',
            'icao_type': 'B737',
        }
        flight_hex = 'ABCDEF'
        aircraft_obj = get_or_create_aircraft(aircraft_info, flight_hex)
        self.assertEqual(Aircraft.objects.count(), 1)
        self.assertEqual(aircraft_obj.hex_id, 'ABCDEF')
        self.assertEqual(aircraft_obj.registration, '')

    def test_get_or_create_aircraft_multiple_existing(self):
        # Setup multiple existing Aircraft objects with the same registration
        Aircraft.objects.create(registration='N12345', hex_id='ABCDEF', aircraft_type='Old Type')
        Aircraft.objects.create(registration='N12345', hex_id='123456', aircraft_type='Another Old Type')

        aircraft_info = {
            'registration': 'N12345',
            'type': 'Boeing 737',
            'icao_type': 'B737',
        }
        flight_hex = 'ABCDEF'

        with self.assertLogs(level=logging.WARNING) as cm:
            aircraft_obj = get_or_create_aircraft(aircraft_info, flight_hex)
            self.assertIn("Multiple Aircraft objects found for registration=N12345", cm.output[0])

        self.assertEqual(Aircraft.objects.count(), 2)
        self.assertEqual(aircraft_obj.registration, 'N12345')
        self.assertEqual(aircraft_obj.aircraft_type, 'Boeing 737')

    def test_get_or_create_airline_new(self):
        airline_info = {
            'name': 'United',
            'icao': 'UAL',
            'iata': 'UA',
        }
        airline_obj = get_or_create_airline(airline_info)
        self.assertEqual(Airline.objects.count(), 1)
        self.assertEqual(airline_obj.icao, 'UAL')
        self.assertEqual(airline_obj.iata, 'UA')

    def test_get_or_create_airline_existing(self):
        Airline.objects.create(name='United', icao='UAL', iata='UA', country='USA')
        airline_info = {
            'name': 'United Airlines',
            'icao': 'UAL',
            'iata': 'UA',
            'country': 'United States',
        }
        airline_obj = get_or_create_airline(airline_info)
        self.assertEqual(Airline.objects.count(), 1)
        self.assertEqual(airline_obj.country, 'USA')  # Ensure existing data is returned and not overwritten.

    def test_get_or_create_airport_new(self):
        airport_info = {
            'iata_code': 'JFK',
            'icao_code': 'KJFK',
            'name': 'John F. Kennedy International Airport',
        }
        airport_obj = get_or_create_airport(airport_info)
        self.assertEqual(Airport.objects.count(), 1)
        self.assertEqual(airport_obj.iata_code, 'JFK')
        self.assertEqual(airport_obj.icao_code, 'KJFK')

    def test_get_or_create_airport_existing(self):
        Airport.objects.create(iata_code='JFK', icao_code='KJFK', name='Old Name')
        airport_info = {
            'iata_code': 'JFK',
            'icao_code': 'KJFK',
            'name': 'John F. Kennedy International Airport',
        }
        airport_obj = get_or_create_airport(airport_info)
        self.assertEqual(Airport.objects.count(), 1)
        self.assertEqual(airport_obj.name, 'Old Name')  # Ensure existing data is returned and not overwritten.

    def test_get_or_create_airport_existing_icao(self):
        Airport.objects.create(iata_code='', icao_code='KJFK', name='Old Name')
        airport_info = {
            'iata_code': 'JFK',
            'icao_code': 'KJFK',
            'name': 'John F. Kennedy International Airport',
        }
        airport_obj = get_or_create_airport(airport_info)
        self.assertEqual(Airport.objects.count(), 1)
        self.assertEqual(airport_obj.name, 'Old Name')

    def test_get_or_create_airport_existing_iata(self):
        Airport.objects.create(iata_code='JFK', icao_code='', name='Old Name')
        airport_info = {
            'iata_code': 'JFK',
            'icao_code': 'KJFK',
            'name': 'John F. Kennedy International Airport',
        }
        airport_obj = get_or_create_airport(airport_info)
        self.assertEqual(Airport.objects.count(), 1)
        self.assertEqual(airport_obj.name, 'Old Name')
