from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FlightDataViewSet, AircraftViewSet, AirlineViewSet, AirportViewSet

router = DefaultRouter()
router.register(r'flightdata', FlightDataViewSet)
router.register(r'aircraft', AircraftViewSet)
router.register(r'airlines', AirlineViewSet)
router.register(r'airports', AirportViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
