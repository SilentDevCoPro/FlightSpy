from django.apps import AppConfig
from django.core.cache import cache
from django.conf import settings
import time
import threading
import json
from dump1090_collector.fetch_helper import fetch_adsbdbAircraftData, fetch_adsbdbCallsignData, fetch_dump1090_data
from dump1090_collector.flight_storage import store_data
import logging

polling_time = getattr(settings, 'DUMP1090_POLLING_TIME', 10)


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
                else:
                    adsbdb_aircraft_data = fetch_adsbdbAircraftData(flight_hex)
                    cache.set(flight_hex, json.dumps(adsbdb_aircraft_data), timeout=600)

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
                    store_data(flight, adsbdb_aircraft_data, adsbdb_callsign_data)
                    logging.error('storing data!')
                else:
                    logging.error(f'no adsb data found: {flight} \n ADSBDB Aircraft: {adsbdb_aircraft_data} \n ADSBDB Callsign {adsbdb_callsign_data}')

        time.sleep(polling_time)


class Dump1090Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dump1090_collector'

    def ready(self):
        thread = threading.Thread(target=poll_dump1090, args=(), daemon=True)
        thread.start()
