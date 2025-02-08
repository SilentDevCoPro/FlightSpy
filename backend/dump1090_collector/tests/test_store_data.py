from unittest import mock
from django.test import TestCase
from django.utils import timezone
from dump1090_collector.models import FlightData, Aircraft, Airline, Airport
from dump1090_collector.services.store_data import store_data


class StoreDataTestCase(TestCase):
    @mock.patch('dump1090_collector.services.store_data.extract_aircraft_info')
    @mock.patch('dump1090_collector.services.store_data.extract_callsign_info')
    @mock.patch('dump1090_collector.services.store_data.extract_flight_data')
    @mock.patch('dump1090_collector.services.store_data.get_or_create_aircraft')
    @mock.patch('dump1090_collector.services.store_data.get_or_create_airline')
    @mock.patch('dump1090_collector.services.store_data.get_or_create_airport')
    def test_store_data_success(self, mock_get_or_create_airport, mock_get_or_create_airline, mock_get_or_create_aircraft, mock_extract_flight_data, mock_extract_callsign_info, mock_extract_aircraft_info):
        # Mock the data returned by the extractors and services
        mock_extract_aircraft_info.return_value = {'registration': 'N12345', 'type': 'Boeing 737'}
        mock_extract_callsign_info.return_value = {'flightroute': {'airline': {'name': 'United', 'icao': 'UAL', 'iata': 'UA'}, 'origin': {'iata_code': 'JFK'}, 'destination': {'iata_code': 'LAX'}}}
        mock_extract_flight_data.return_value = {
            'flight_hex': 'ABCDEF',
            'squawk': 1200,
            'flight_callsign': 'UAL123',
            'lat': 34.0522,
            'lon': -118.2437,
            'valid_position': True,
            'altitude': 30000,
            'vertical_rate': 1000,
            'track': 270,
            'valid_track': True,
            'speed_in_knots': 450,
            'messages_received': 50,
            'seen': 10,
            'timestamp': timezone.now(),
        }

        mock_get_or_create_aircraft.return_value = Aircraft.objects.create(registration='N12345', hex_id='ABCDEF')
        mock_get_or_create_airline.return_value = Airline.objects.create(name='United', icao='UAL', iata='UA')
        mock_get_or_create_airport.side_effect = [Airport.objects.create(iata_code='JFK'), Airport.objects.create(iata_code='LAX')]

        # Call the function
        flight = {'hex': 'ABCDEF'}
        adsbdb_aircraft_data = {}
        adsbdb_callsign_data = {}
        flight_data = store_data(flight, adsbdb_aircraft_data, adsbdb_callsign_data)

        # Assertions
        self.assertEqual(FlightData.objects.count(), 1)
        self.assertEqual(flight_data.flight_callsign, 'UAL123')
        self.assertEqual(flight_data.aircraft.registration, 'N12345')
        self.assertEqual(flight_data.airline.name, 'United')
        self.assertEqual(flight_data.origin_airport.iata_code, 'JFK')
        self.assertEqual(flight_data.destination_airport.iata_code, 'LAX')

        mock_extract_aircraft_info.assert_called_once_with(adsbdb_aircraft_data)
        mock_extract_callsign_info.assert_called_once_with(adsbdb_callsign_data)
        mock_extract_flight_data.assert_called_once_with(flight)
        mock_get_or_create_aircraft.assert_called_once_with({'registration': 'N12345', 'type': 'Boeing 737'}, 'ABCDEF')
        mock_get_or_create_airline.assert_called_once_with({'name': 'United', 'icao': 'UAL', 'iata': 'UA'})
        self.assertEqual(mock_get_or_create_airport.call_count, 2)
        mock_get_or_create_airport.assert_has_calls([
            mock.call({'iata_code': 'JFK'}),
            mock.call({'iata_code': 'LAX'})
        ])
