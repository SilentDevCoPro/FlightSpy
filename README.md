# FlightSpy

## Update DB
docker-compose exec web python backend/manage.py makemigrations dump1090_collector
docker-compose exec web python backend/manage.py migrate dump1090_collector


## If you want to clear DB
docker-compose exec web python backend/manage.py flush
