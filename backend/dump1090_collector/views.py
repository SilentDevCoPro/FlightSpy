from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models.functions import Trim

from .models import FlightData, Aircraft, Airline, Airport
from .serializers import FlightDataSerializer, AircraftSerializer, AirlineSerializer, AirportSerializer
from .filters import FlightDataFilter  # Import the custom filter

class FlightDataViewSet(viewsets.ModelViewSet):
    queryset = FlightData.objects.all().order_by('timestamp')
    serializer_class = FlightDataSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = FlightDataFilter

    @action(detail=False, methods=['get'], url_path='flight_path')
    def flight_path(self, request):
        """
        Custom endpoint to retrieve the historical flight positions (flight path)
        for a specific aircraft or flight.

        Provide one of the following query parameters:
          - aircraft_id: the primary key of the Aircraft record
          - flight_callsign: the callsign of the flight

        Example URLs:
          /dump1090_collector/api/flightdata/flight_path/?aircraft_id=1
          /dump1090_collector/api/flightdata/flight_path/?flight_callsign=UAL1012
        """
        aircraft_id = request.query_params.get('aircraft_id', None)
        flight_callsign = request.query_params.get('flight_callsign', None)

        if aircraft_id:
            flight_data_qs = FlightData.objects.filter(aircraft__id=aircraft_id).order_by('timestamp')
        elif flight_callsign:
            flight_callsign = flight_callsign.strip()
            flight_data_qs = FlightData.objects.annotate(
                trimmed_callsign=Trim('flight_callsign')
            ).filter(trimmed_callsign__iexact=flight_callsign).order_by('timestamp')
        else:
            return Response(
                {"error": "Missing query parameter: provide either aircraft_id or flight_callsign."},
                status=400
            )

        serializer = self.get_serializer(flight_data_qs, many=True)
        return Response(serializer.data)

class AircraftViewSet(viewsets.ModelViewSet):
    queryset = Aircraft.objects.all()
    serializer_class = AircraftSerializer

class AirlineViewSet(viewsets.ModelViewSet):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer

class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
