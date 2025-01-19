from django.apps import AppConfig
import requests
import time
import threading
from datetime import datetime

def poll_dump1090(Dump1090FlightData, AdsbdbAircraftData, AdsbdbCallsignData):
    while True:
        try:
            response = requests.get('http://host.docker.internal:8080/dump1090/data.json')
            response.raise_for_status()
            data = response.json()
            
            current_time = datetime.now()
            timestamp = current_time.time()
            
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
                
                hex_detail_response = requests.get(f'https://api.adsbdb.com/v0/aircraft/{aircraft['hex']}')
                hex_detail_response.raise_for_status()
                
                
                callsign_detail_response = requests.get(f'https://api.adsbdb.com/v0/callsign/{aircraft['flight'].strip()}')
                callsign_detail_response.raise_for_status()
                
                
            
        except Exception as e:
            print("Error polling dump1090: ", e)
        
        time.sleep(5)

class Dump1090Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dump1090_collector'
    
    def ready(self):
        from .models import Dump1090FlightData, AdsbdbAircraftData, AdsbdbCallsignData
        thread = threading.Thread(target=poll_dump1090, args=(Dump1090FlightData, AdsbdbAircraftData, AdsbdbCallsignData,), daemon=True)
        thread.start()

