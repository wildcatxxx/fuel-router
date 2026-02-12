## Fuel Route Optimization API

A Django + PostGIS API that calculates the most cost-effective fuel stops along a route within the USA.

### The system:

```
1. Accepts start and end locations

2. Retrieves the driving route

3. Finds optimal fuel stops along the route

4. Calculates total fuel cost

5. Minimizes external API calls

6. Returns results quickly using caching
```

### Problem Statement

**Build an API that:**

Accepts start and finish locations (within the USA)

**Returns:**

- The driving route
- Optimal fuel stop locations
- Total fuel cost
- Assumptions:
- Vehicle range: 500 miles
- Fuel efficiency: 10 miles per gallon
- Fuel prices provided via dataset

### Requirements:

- Latest stable Django
- Minimal routing API calls
- Fast response time
- Loom demo + shared code

### Architecture Overview

```
Client
   ↓
Django REST API
   ↓
RouteService (OpenRouteService – 1 API call)
   ↓
PostGIS (Spatial filtering + optimization)
   ↓
FuelOptimizer (Greedy cost minimization)
   ↓
Caching Layer
   ↓
JSON Response
```

### Tech Stack

- Django (latest stable)
- Django REST Framework
- PostgreSQL + PostGIS
- OpenRouteService API
- Memcached / Redis (caching)
- GeoDjango

### Features

#### Single Routing API Call

Only one external routing request per route.

#### Spatial Query Optimization

- Uses PostGIS PointField(geography=True)
- GIST spatial index
- Route sampling + spatial filtering

#### Cost Optimization Algorithm

Greedy selection of cheapest reachable fuel stop within 500-mile range.

#### Caching Strategy

- Route results cached
- Hashed cache keys (memcached-safe)
- Avoids repeated routing API calls

#### Scalable Design

- Service-layer architecture
- No N+1 spatial queries
- Candidate stops loaded once

### API Endpoint

`POST /api/route/`

```bash
# Request body
# lon, lat order

{
  "start": "-119.7554, 41.7585",
  "end": "-85.3866, 31.2217"
}
```

#### Example Response

```bash
{
  "distance_miles": 2583.25,
  "fuel_stops": [
    {
      "opis_id": "63599",
      "name": "PWI #978",
      "city": "Salt Lake City",
      "state": "UT",
      "price": 3.359,
      "gallons": 41.53,
      "cost": 139.49
    },
    {
      "opis_id": "4700",
      "name": "A C TRUCKSTOP",
      "city": "Laramie",
      "state": "WY",
      "price": 3.079,
      "gallons": 31.9,
      "cost": 98.23
    },
    {
      "opis_id": "72786",
      "name": "QUIKTRIP #333",
      "city": "Newton",
      "state": "KS",
      "price": 2.949,
      "gallons": 48.14,
      "cost": 141.97
    },
    {
      "opis_id": "72653",
      "name": "Quiktrip #7153",
      "city": "Olive Branch",
      "state": "MS",
      "price": 2.916,
      "gallons": 46.66,
      "cost": 136.07
    },
    {
      "opis_id": "72818",
      "name": "QUIKTRIP #7174",
      "city": "Montgomery",
      "state": "AL",
      "price": 2.999,
      "gallons": 26.16,
      "cost": 78.46
    }
  ],
  "total_cost": 594.22
}
```

## Optimization Strategy

#### Assumptions

- Max range: 500 miles
- 10 MPG
- Minimize total fuel cost

#### Algorithm

- Retrieve route geometry
- Sample route points
- Find truck stops within buffer distance
- Order stops by distance from start
- While destination not reached:
- Identify stops reachable within 500 miles
- Select cheapest
- Refuel
- Continue

  ```
  This greedy approach works efficiently under fixed MPG and price-per-gallon conditions.
  ```

## Performance Strategy

- Minimize External Calls
  - Only one call to OpenRouteService per route

- Spatial Index
  ```
  CREATE INDEX truckstop_location_gix
  ON fuel_truckstop
  USING GIST (location);
  ```
- Caching
  - Hashed key strategy:

  ```bash
  import hashlib
  def build_cache_key(start, end):
      raw = f"{round(start[0],4)}_{round(start[1],4)}-{round(end[0],4)}_{round(end[1],4)}"
      return "route_" + hashlib.md5(raw.encode()).hexdigest()
  ```

- Route Sampling
  ```
  Route sampled every ~20 points to reduce spatial queries.
  ```

## Setup Instructions

### Clone Repository

```
git clone <repo-url>
cd fuel-router
```

### Create Virtual Environment

```
python -m venv .venv
source .venv/bin/activate
```

### Install Dependencies

```
pip install -r requirements.txt
```

### Setup PostgreSQL + PostGIS

```
CREATE DATABASE fuel_router;
CREATE EXTENSION postgis;
```

### Run Migrations

```
python manage.py migrate
```

### Add Environment Variables

```
DEBUG=True
SECRET_KEY = app-secret-key'

DB_NAME = database-name
DB_USER = database-user
DB_PASSWORD = database-password
DB_HOST = database-host
DB_PORT = database-port

OPENROUTE_API_KEY = open-route-secret-key

```

### Run Server

```
python manage.py runserver
```

### Load Fuel Data

```bash
python manage.py load_fuel_data fuel_data.csv
```

## Scalability Considerations

**If scaled to 1M+ truck stops:**

- Pre-cluster by region
- Use bounding-box prefilter
- Use ST_LineLocatePoint for route-relative ordering
- Redis cluster for distributed caching
- Async precomputation for common routes

## Testing

**Test via Postman:**

```
Method: POST
URL: http://localhost:8000/api/route/
Body: JSON
```
