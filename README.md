# FlightSpy ✈️🕵️

[![Django](https://img.shields.io/badge/Django-5.1.5-brightgreen.svg)](https://www.djangoproject.com/)
[![Docker](https://img.shields.io/badge/Docker-27.3.1-blue.svg)](https://www.docker.com/)
[![Postgres](https://img.shields.io/badge/PostgreSQL-15.0-blue)](https://www.postgresql.org/)
[![Docker Compose](https://www.docker.com/wp-content/uploads/2022/03/Moby-logo.png)](https://docs.docker.com/compose/)
[![Redis](https://img.shields.io/badge/Redis-7.0--alpine-red.svg)](https://redis.io/)

**Real-time Aircraft Tracking & Data Enrichment System**

FlightSpy is a sophisticated aircraft monitoring solution that combines ADSB receiver data with commercial flight information. The system polls a Dump1090 instance, enriches aircraft data with [ADSBDB](https://www.adsbdb.com/) API, and provides persistent storage with analytics capabilities.


---

## 🌟 Features

- Real-time ADSB aircraft tracking
- Data enrichment with commercial flight details
- Dockerized microservices architecture
- PostgreSQL database for persistent storage
- Redis caching for improved performance
- Scalable Django backend
- REST API integration with ADSBDB

---

## 🚀 Quick Start

### Prerequisites
1. **Hardware & Data Source**:
   - ADSB receiver feeding data to [Dump1090](https://github.com/flightaware/dump1090).
   - Raspberry Pi5 (This was tested and run on the Pi5, I'm sure it will work with most Linux distros)


### Installation
#### Installation process is NOT thoroughly tested at this stage, please report any problems/fixs!
1. Clone repository:
 ```
   git clone https://github.com/yourusername/flightspy.git
   cd flightspy
```

2. Script permissions
```
   chmod +x setup.sh scripts/*.sh
```

3. Run setup
```
   ./setup.sh
```
### Finished
IF all went well, the script will give you the information to access your fancy new locally hosted ADSB data!

## For the nerds the want to learn/contribute to the project

### 🔧 System Architecture

FlightSpy is built on a robust and scalable architecture designed to process, enrich, and store real-time aircraft data. Here's how it works:

1. **Data Collection**:
   - An **ADSB receiver** captures raw aircraft signals (e.g., position, altitude, speed) from nearby aircraft.

2. **Data Processing**:
   - The raw data is sent to a **computer** running [Dump1090](https://github.com/flightaware/dump1090), which decodes and transforms the ADSB signals into a readable format (e.g., JSON).

3. **Data Polling**:
   - **FlightSpy** periodically polls the Dump1090 server to retrieve the latest aircraft data.

4. **Data Enrichment**:
   - FlightSpy uses the [ADSBDB API](https://www.adsbdb.com/) to enrich the Dump1090 data with additional details, such as aircraft type, registration, airline, and flight route.

5. **Caching**:
   - To optimize performance and reduce API calls to ADSBDB, **Redis** is used as a caching layer. This ensures frequently requested data is served quickly without overloading external APIs.

6. **Data Storage**:
   - All enriched data is stored in a **PostgreSQL** database for persistent storage, enabling historical analysis and querying.

7. **Future Enhancements**:
   - Planned updates include a **live map interface** that will display aircraft locations, flight paths, and detailed information in real-time, providing an interactive and visually engaging experience.

---

### 📡 API Integration
FlightSpy integrates with ADSBDB API for aircraft data enrichment. Ensure you have read their documents
before making any code changes [ADSBDB Website](https://www.adsbdb.com/).

---
## Database Actions
```
# Reset database
docker exec web python backend/manage.py flush

# Backup db
docker exec -t db pg_dump -U ${POSTGRES_USER} -d ${POSTGRES_DB} > backup.sql

# Restore db
docker exec -i db psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} < backup.sql
```

---

### 🧪 Testing
```
# Run all tests
docker compose run --rm web python backend/manage.py test dump1090_collector.tests

# Specific test case
docker compose run --rm web python backend/manage.py test dump1090_collector.tests.example
```

---
