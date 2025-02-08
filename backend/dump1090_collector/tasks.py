from celery import shared_task
from django.conf import settings
from django.core.cache import cache
import json
from dump1090_collector.fetch_helper import (
    fetch_adsbdbAircraftData,
    fetch_adsbdbCallsignData,
    fetch_dump1090_data,
)
from dump1090_collector.services.store_data import store_data
import logging
import time
import os

polling_time = getattr(settings, 'DUMP1090_POLLING_TIME', 10)
cache_ttl = getattr(settings, 'CACHE_TTL', 600)


@shared_task(queue='dump1090_queue')
def poll_dump1090_task():
    time.sleep(10)
    if not os.environ.get('CELERY_WORKER_RUNNING'):
        logging.error("Task called in non-Celery context - ignoring")
        return

    while True:
        try:
            dump1090_data = fetch_dump1090_data()
            for flight in dump1090_data:
                adsbdb_aircraft_data = {}
                adsbdb_callsign_data = {}

                if flight.get('hex'):
                    flight_hex = flight['hex']
                    cached_aircraft_data = cache.get(flight_hex)

                    if cached_aircraft_data:
                        try:
                            adsbdb_aircraft_data = json.loads(cached_aircraft_data)
                        except Exception as e:
                            logging.error("Error decoding cached aircraft data for hex %s: %s", flight_hex, e)
                            adsbdb_aircraft_data = {}
                    else:
                        adsbdb_aircraft_data = fetch_adsbdbAircraftData(flight_hex)
                        cache.set(flight_hex, json.dumps(adsbdb_aircraft_data), timeout=cache_ttl)

                if flight.get('flight'):
                    flight_code = flight['flight']
                    cached_callsign_data = cache.get(flight_code)

                    if cached_callsign_data:
                        try:
                            adsbdb_callsign_data = json.loads(cached_callsign_data)
                        except Exception as e:
                            logging.error("Error decoding cached callsign data for flight %s: %s", flight_code, e)
                            adsbdb_callsign_data = {}
                    else:
                        adsbdb_callsign_data = fetch_adsbdbCallsignData(flight_code)
                        cache.set(flight_code, json.dumps(adsbdb_callsign_data), timeout=cache_ttl)

                store_data(flight, adsbdb_aircraft_data, adsbdb_callsign_data)

            time.sleep(polling_time)
        except Exception as e:
            logging.error("Critical error in poll_dump1090_task: %s", e)
            time.sleep(30)
