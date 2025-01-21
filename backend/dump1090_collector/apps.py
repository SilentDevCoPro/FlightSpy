from django.apps import AppConfig
import requests
import time
import threading
from datetime import datetime
import logging



def store_dump1090_data(aircraft, timestamp, Dump1090FlightData):
    """
    Store one aircraft's Dump1090 info in the database.
    - 'aircraft' is a single dictionary from dump1090 data.
    - 'timestamp' is the current integer timestamp.
    """
    
    hex_value = (aircraft.get('hex') or '')
    
    if not hex_value:
        return None
    
    valid_position = bool(aircraft.get('validposition', 0))
    valid_track = bool(aircraft.get('validtrack', 0))
    
    flight_data = Dump1090FlightData.objects.create(
        hex_id=aircraft.get('hex', ''),
        squawk_code=aircraft.get('squawk', 0),
        flight_callsign=aircraft.get('flight', ''),
        latitude=aircraft.get('lat', 0.0),
        longitude=aircraft.get('lon', 0.0),
        valid_position=valid_position,  
        altitude=aircraft.get('altitude', 0),
        vertical_rate=aircraft.get('vert_rate', 0),
        track=aircraft.get('track', 0),
        valid_track=valid_track,
        speed_in_knots=aircraft.get('speed', 0),
        messages_received=aircraft.get('messages', 0),
        seen=aircraft.get('seen', 0),
        timestamp=timestamp
    )
    return flight_data
    


def poll_dump1090(Dump1090FlightData, AdsbdbAircraftData, AdsbdbCallsignData):
    while True:
        try:
            response = requests.get('http://host.docker.internal:8080/dump1090/data.json')
            response.raise_for_status()
            data = response.json()
            
            current_time = datetime.now()
            timestamp = models.DateTimeField()
            
            for aircraft in data:
                Dump1090FlightData.objects.create(
                    hex_id=aircraft.get('hex', ''),
                    squawk_code=aircraft.get('squawk', 0),
                    flight_callsign=aircraft.get('flight', ''),
                    latitude=aircraft.get('lat', 0.0),
                    longitude=aircraft.get('lon', 0.0),
                    valid_position=bytes([aircraft.get('validposition', 0)]),  
                    altitude=aircraft.get('altitude', 0),
                    vertical_rate=aircraft.get('vert_rate', 0),
                    track=aircraft.get('track', 0),
                    valid_track=bytes([aircraft.get('validtrack', 0)]),
                    speed_in_knots=aircraft.get('speed', 0),
                    messages_received=aircraft.get('messages', 0),
                    seen=aircraft.get('seen', 0),
                    timestamp=timestamp
                )
            
        except Exception as e:
            print("Error polling dump1090: ", e)
        
        time.sleep(5)
        
def fetch_json(url: str, timeout=10) -> dict:
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f'Request to {url} failed {e}')
        return None
    
    try:
        data = response.json()
    except ValueError as e:
        logging.error(f'Error parsing JSON from {url}. Response: {response.text}')
        return None
    
    return data

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
        from .models import Dump1090FlightData, AdsbdbAircraftData, AdsbdbCallsignData
        thread = threading.Thread(target=poll_dump1090, args=(Dump1090FlightData, AdsbdbAircraftData, AdsbdbCallsignData,), daemon=True)
        thread.start()

