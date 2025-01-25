from django.apps import AppConfig
from django.utils import timezone
import requests
import time
import threading
import logging



def store_data(FlightData, dump1090_aircraft_data, aircraft_data, callsign_data):
    aircraft_data = aircraft_data or {}
    callsign_data = callsign_data or {}
    
    valid_position = bool(dump1090_aircraft_data.get('validposition', 0))
    valid_track = bool(dump1090_aircraft_data.get('validtrack', 0))
    timestamp = timezone.now()
    
    logging.error(f'aircraft data: {aircraft_data}')
    logging.error(f'callsign data: {callsign_data}')
    
    flight_data = FlightData.objects.create(
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

        # Additional fields from adsbdb aircraft data
        aircraft_type=aircraft_data.get('response', {}).get('aircraft', {}).get('type', None),
        icao_type=aircraft_data.get('response', {}).get('aircraft', {}).get('icao_type', None),
        manufacturer=aircraft_data.get('response', {}).get('aircraft', {}).get('manufacturer', None),
        mode_s=aircraft_data.get('response', {}).get('aircraft', {}).get('mode_s', None),
        registration=aircraft_data.get('response', {}).get('aircraft', {}).get('registration', None),
        registered_owner_country_iso_name=aircraft_data.get('response', {}).get('aircraft', {}).get('registered_owner_country_iso_name', None),
        registered_owner_country_name=aircraft_data.get('response', {}).get('aircraft', {}).get('registered_owner_country_name', None),
        registered_owner_operator_flag_code=aircraft_data.get('response', {}).get('aircraft', {}).get('registered_owner_operator_flag_code', None),
        registered_owner=aircraft_data.get('response', {}).get('aircraft', {}).get('registered_owner', None),
        url_photo=aircraft_data.get('response', {}).get('aircraft', {}).get('url_photo', None),
        url_photo_thumbnail=aircraft_data.get('response', {}).get('aircraft', {}).get('url_photo_thumbnail', None),


        # Additional fields from adsbdb callsign data
        callsign=callsign_data.get('callsign', None),
        callsign_icao=callsign_data.get('callsign_icao', None),
        callsign_iata=callsign_data.get('callsign_iata', None),
        airline=callsign_data.get('airline', {}).get('name', None),
        origin=callsign_data.get('origin', {}).get('name', None),
        destination=callsign_data.get('destination', {}).get('name', None),
    )
    
    logging.error(
        f"Created FlightData with ID {flight_data.id}: "
        f"aircraft_type={flight_data.aircraft_type}, "
        f"icao_type={flight_data.icao_type}, "
        f"manufacturer={flight_data.manufacturer}, "
        f"mode_s={flight_data.mode_s}, "
        f"registration={flight_data.registration}, "
        f"owner_country_iso_name={flight_data.registered_owner_country_iso_name}, "
        f"owner_country_name={flight_data.registered_owner_country_name}, "
        f"owner_operator_flag_code={flight_data.registered_owner_operator_flag_code}, "
        f"registered_owner={flight_data.registered_owner}, "
        f"url_photo={flight_data.url_photo}, "
        f"url_photo_thumbnail={flight_data.url_photo_thumbnail}, "
        f"callsign={flight_data.callsign}, "
        f"callsign_icao={flight_data.callsign_icao}, "
        f"callsign_iata={flight_data.callsign_iata}, "
        f"airline={flight_data.airline}, "
        f"origin={flight_data.origin}, "
        f"destination={flight_data.destination}"
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
                adsbdb_callsign_data = fetch_adsbdbCallsignData(flight['flight'].strip())
            
            if adsbdb_aircraft_data or adsbdb_callsign_data:
                data = store_data(FlightData, flight, adsbdb_aircraft_data, adsbdb_callsign_data)
                logging.error(f'Data stored: {data}')
                    
            
                
        time.sleep(5)
        
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

