# FlightSpy

## Update DB
docker exec -it web python manage.py makemigrations
docker exec -it web python manage.py migrate
