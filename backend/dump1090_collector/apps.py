from django.apps import AppConfig
import requests
import time
import threading

def poll_dump1090(FlightData):
    while True:
        try:
            response = requests.get('http://host.docker.internal:8080/dump1090/data.json')
            response.raise_for_status()
            data = response.json()
            
            for aircraft in data:
                FlightData.objects.create(
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
                )
            
        except Exception as e:
            print("Error polling dump1090: ", e)
        
        time.sleep(2)

class Dump1090Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dump1090_collector'
    
    def ready(self):
        from .models import FlightData
        thread = threading.Thread(target=poll_dump1090, args=(FlightData,), daemon=True)
        thread.start()

