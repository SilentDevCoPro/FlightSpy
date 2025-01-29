from django.apps import AppConfig
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Q
import requests
import time
import threading
import logging 
import json

from dump1090_collector.flight_storage import store_data

polling_time = 10

def poll_dump1090():
    while True:
        dump1090_data = fetch_dump1090_data()

        for flight in dump1090_data:
            adsbdb_aircraft_data = {}
            adsbdb_callsign_data = {}    
            
            if flight['hex']:
                flight_hex = flight['hex']
                cached_aircraft_data = cache.get(flight_hex)
                
                if cached_aircraft_data:
                    adsbdb_aircraft_data = json.loads(cached_aircraft_data)
                    logging.error(f'Cache HIT! {flight_hex}')
                else:
                    adsbdb_aircraft_data = fetch_adsbdbAircraftData(flight_hex)
                    cache.set(flight_hex, json.dumps(adsbdb_aircraft_data), timeout=600)
                    logging.error(f'Cache Miss! API CALLED {flight_hex}')
                    
            if flight['flight']:
                flight_code = flight['flight']
                cached_callsign_data = cache.get(flight_code)

                if cached_callsign_data:
                    adsbdb_callsign_data = json.loads(cached_callsign_data)
                else:
                    adsbdb_callsign_data = fetch_adsbdbCallsignData(flight_code)
                    cache.set(flight_code, json.dumps(adsbdb_callsign_data), timeout=600)
                
            if adsbdb_aircraft_data and adsbdb_callsign_data:
                if adsbdb_callsign_data.get('response') != 'unknown callsign' and adsbdb_callsign_data.get('response'):
                    logging.error(f'\nstoring flight data{flight}') 
                    logging.error(f'storing aircraft data {adsbdb_aircraft_data}')
                    logging.error(f'storing callsign data {adsbdb_aircraft_data}\n')
                    store_data(flight, adsbdb_aircraft_data, adsbdb_aircraft_data)
                else:
                    logging.error(f'Failed to store data unknown callsign')
                    
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
        thread = threading.Thread(target=poll_dump1090, args=(), daemon=True)
        thread.start()

