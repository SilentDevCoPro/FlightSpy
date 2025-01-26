from django.apps import AppConfig
from django.utils import timezone
import requests
import time
import threading
import logging

polling_time = 10

def store_data(FlightData, dump1090_aircraft_data, aircraft_data, callsign_data):
    
    valid_position = bool(dump1090_aircraft_data.get('validposition', 0))
    valid_track = bool(dump1090_aircraft_data.get('validtrack', 0))
    
    timestamp = timezone.now()

    aircraft_info = aircraft_data.get('response', {}).get('aircraft', {})
    flightroute_info = callsign_data.get('response', {}).get('flightroute', {})
    
    flight_data = FlightData.objects.create(
        # Primary dump1090 fields
        hex_id=dump1090_aircraft_data.get('hex', ''),
        squawk_code=dump1090_aircraft_data.get('squawk', 0),
        flight_callsign=dump1090_aircraft_data.get('flight', ''),
        latitude=dump1090_aircraft_data.get('lat', 0.0),
        longitude=dump1090_aircraft_data.get('lon', 0.0),
        valid_position=valid_position,
        altitude=dump1090_aircraft_data.get('altitude', 0),
        vertical_rate=dump1090_aircraft_data.get('vert_rate', 0),
        track=dump1090_aircraft_data.get('track', 0),
        valid_track=valid_track,
        speed_in_knots=dump1090_aircraft_data.get('speed', 0),
        messages_received=dump1090_aircraft_data.get('messages', 0),
        seen=dump1090_aircraft_data.get('seen', 0),
        timestamp=timestamp,

        # Aircraft data (from adsbdb)
        aircraft_type=aircraft_info.get('type', ''),
        icao_type=aircraft_info.get('icao_type', ''),
        manufacturer=aircraft_info.get('manufacturer', ''),
        mode_s=aircraft_info.get('mode_s', ''),
        registration=aircraft_info.get('registration', ''),
        registered_owner_country_iso_name=aircraft_info.get('registered_owner_country_iso_name', ''),
        registered_owner_country_name=aircraft_info.get('registered_owner_country_name', ''),
        registered_owner_operator_flag_code=aircraft_info.get('registered_owner_operator_flag_code', ''),
        registered_owner=aircraft_info.get('registered_owner', ''),
        url_photo=aircraft_info.get('url_photo', ''),
        url_photo_thumbnail=aircraft_info.get('url_photo_thumbnail', ''),

        # Callsign/flight route data (from adsbdb)
        callsign=flightroute_info.get('callsign', ''),
        callsign_icao=flightroute_info.get('callsign_icao', ''),
        callsign_iata=flightroute_info.get('callsign_iata', ''),
        airline_name=flightroute_info.get('airline', {}).get('name', ''),
        airline_icao=flightroute_info.get('airline', {}).get('icao', ''),
        airline_iata=flightroute_info.get('airline', {}).get('iata', ''),
        airline_country=flightroute_info.get('airline', {}).get('country', ''),
        airline_country_iso=flightroute_info.get('airline', {}).get('country_iso', ''),
        airline_callsign=flightroute_info.get('airline', {}).get('callsign', ''),
        origin_name=flightroute_info.get('origin', {}).get('name', ''),
        origin_country_iso_name=flightroute_info.get('origin', {}).get('country_iso_name', ''),
        origin_country_name=flightroute_info.get('origin', {}).get('country_name', ''),
        origin_elevation=flightroute_info.get('origin', {}).get('elevation', 0),
        origin_iata_code=flightroute_info.get('origin', {}).get('iata_code', ''),
        origin_icao_code=flightroute_info.get('origin', {}).get('icao_code', ''),
        origin_latitude=flightroute_info.get('origin', {}).get('latitude', 0),
        origin_longitude=flightroute_info.get('origin', {}).get('longitude', 0),
        origin_municipality=flightroute_info.get('origin', {}).get('municipality', ''),
        destination=flightroute_info.get('destination', {}).get('name', ''),
        destination_country_iso_name=flightroute_info.get('destination', {}).get('country_iso_name', ''),
        destination_country_name=flightroute_info.get('destination', {}).get('country_name', ''),
        destination_elevation=flightroute_info.get('destination', {}).get('elevation', 0),
        destination_iata_code=flightroute_info.get('destination', {}).get('iata_code', ''),
        destination_icao_code=flightroute_info.get('destination', {}).get('icao_code', ''),
        destination_latitude=flightroute_info.get('destination', {}).get('latitude', 0),
        destination_longitude=flightroute_info.get('destination', {}).get('longitude', 0),
        destination_municipality=flightroute_info.get('destination', {}).get('municipality', ''),
    )

    return flight_data
    


def poll_dump1090(FlightData):
    while True:
        dump1090_data = fetch_dump1090_data()

        
        for flight in dump1090_data:
            adsbdb_aircraft_data = {}
            adsbdb_callsign_data = {}    
            
            if flight['hex']:
                adsbdb_aircraft_data = fetch_adsbdbAircraftData(flight['hex'])
            if flight['flight']:
                adsbdb_callsign_data = fetch_adsbdbCallsignData(flight['flight'])
            if adsbdb_aircraft_data and adsbdb_callsign_data:
                if adsbdb_callsign_data.get('response') != 'unknown callsign':
                    store_data(FlightData, flight, adsbdb_aircraft_data, adsbdb_callsign_data)
                    
            
                
        time.sleep(polling_time)
        
def fetch_json(url: str, timeout=10) -> dict:
    response = None
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if response is not None:
            try:
                content = response.json()
            except ValueError:
                content = {}
            
            resp_value = content.get("response", "")
            if resp_value == "unknown callsign":
                logging.info(f"Unknown callsign from {url}: {content}")
                return content
            elif resp_value == "unknown aircraft":
                logging.info(f"Unknown aircraft from {url}: {content}")
                return content
            else:
                logging.error(f"Request to {url} failed: {e}. Response content: {content}")
        else:
            logging.error(f"No response returned from {url}. Error: {e}")
        return {}

def fetch_dump1090_data() -> list:
    return fetch_json('http://host.docker.internal:8080/dump1090/data.json')

def fetch_adsbdbAircraftData(hex_id) -> dict:
    return fetch_json(f'https://api.adsbdb.com/v0/aircraft/{hex_id}')
    
def fetch_adsbdbCallsignData(flight) -> dict:
    return fetch_json(f'https://api.adsbdb.com/v0/callsign/{flight.strip()}')

class Dump1090Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dump1090_collector'
    
    def ready(self):
        from .models import FlightData
        thread = threading.Thread(target=poll_dump1090, args=(FlightData,), daemon=True)
        thread.start()

