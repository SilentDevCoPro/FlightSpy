from celery import shared_task
from django.conf import settings
from django.core.cache import cache
from contextlib import suppress
from functools import partial
from concurrent.futures import ThreadPoolExecutor
import json
import logging
from typing import Optional, Dict, Any

from dump1090_collector.fetch_helper import (
    fetch_adsbdbAircraftData,
    fetch_adsbdbCallsignData,
    fetch_dump1090_data,
)
from dump1090_collector.services.store_data import store_data

logger = logging.getLogger(__name__)

# Configuration
POLLING_TIME = getattr(settings, 'DUMP1090_POLLING_TIME', 10)
CACHE_TTL = getattr(settings, 'CACHE_TTL', 600)
MAX_WORKERS = getattr(settings, 'DUMP1090_MAX_WORKERS', 4)


def get_cached_data(key: str, fetch_fn: callable) -> Optional[Dict[str, Any]]:
    """Helper function to handle cache with automatic fetch fallback."""
    cached_data = cache.get(key)
    if cached_data:
        try:
            return json.loads(cached_data)
        except json.JSONDecodeError as e:
            logger.warning("Cache decode error for key %s: %s", key, e)
    
    fresh_data = fetch_fn(key)
    if fresh_data:
        cache.set(key, json.dumps(fresh_data), timeout=CACHE_TTL)
    return fresh_data


def process_flight(flight: Dict[str, Any]) -> None:
    """Process individual flight data with proper error isolation."""
    with suppress(Exception):  # Prevent one bad flight from breaking others
        hex_code = flight.get('hex')
        callsign = flight.get('flight')

        aircraft_data = get_cached_data(hex_code, fetch_adsbdbAircraftData) if hex_code else {}
        callsign_data = get_cached_data(callsign, fetch_adsbdbCallsignData) if callsign else {}

        store_data(flight, aircraft_data, callsign_data)


@shared_task(
    queue='dump1090_queue',
    autoretry_for=(Exception,),
    retry_backoff=30,
    retry_backoff_max=300,
    max_retries=3
)
def poll_dump1090_task():
    """Periodic task to collect and process dump1090 data."""
    try:
        # Fetch and process flights in parallel
        flights = fetch_dump1090_data()
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            list(executor.map(process_flight, flights))

    except Exception as e:
        logger.critical("Polling task failed: %s", e, exc_info=True)
        raise  # Enable Celery auto-retry