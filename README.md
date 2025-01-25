# FlightSpy

## Update DB
docker-compose exec web python backend/manage.py makemigrations dump1090_collector
docker exec -it web python manage.py makemigrations
docker exec -it web python manage.py migrate
