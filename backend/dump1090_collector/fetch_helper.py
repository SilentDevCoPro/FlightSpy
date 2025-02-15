import requests
import logging


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
    return fetch_json('http://dump1090:8080/dump1090/data.json')


def fetch_adsbdbAircraftData(hex_id) -> dict:
    return fetch_json(f'https://api.adsbdb.com/v0/aircraft/{hex_id}')


def fetch_adsbdbCallsignData(flight) -> dict:
    return fetch_json(f'https://api.adsbdb.com/v0/callsign/{flight.strip()}')
