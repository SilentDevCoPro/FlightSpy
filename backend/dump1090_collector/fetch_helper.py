import requests
import logging


def fetch_json(url: str, timeout=10) -> dict:
    response = None
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        
        # Ensure we always return a dictionary
        if isinstance(data, dict):
            return data
        else:
            logging.error(f"Unexpected non-dictionary response from {url}: {data}")
            return {"response": str(data)}
            
    except requests.exceptions.RequestException as e:
        if response is not None:
            try:
                content = response.json()
                if isinstance(content, dict):
                    resp_value = content.get("response", "")
                    if resp_value in ["unknown callsign", "unknown aircraft"]:
                        logging.info(f"{resp_value} from {url}: {content}")
                        return content
                    else:
                        logging.error(f"Request to {url} failed: {e}. Response content: {content}")
                else:
                    logging.error(f"Non-dictionary response from {url}: {content}")
                    return {"response": str(content)}
            except ValueError:
                logging.error(f"Invalid JSON response from {url}: {response.text}")
                return {"response": response.text}
        else:
            logging.error(f"No response returned from {url}. Error: {e}")
        return {}


def fetch_dump1090_data() -> dict:
    return fetch_json('http://dump1090:8080/data/aircraft.json')


def fetch_adsbdbAircraftData(hex_id) -> dict:
    return fetch_json(f'https://api.adsbdb.com/v0/aircraft/{hex_id}')


def fetch_adsbdbCallsignData(flight) -> dict:
    return fetch_json(f'https://api.adsbdb.com/v0/callsign/{flight.strip()}')
