# Weather Dashboard API

A weather forecast API built with Django REST Framework, consuming the OpenWeatherMap API with Redis caching to minimize external API calls.

---

## Features

- **Current weather** — temperature, humidity, wind speed, and conditions for any city
- **5-day forecast** — daily forecast at noon, parsed from OpenWeatherMap's 3-hour interval data
- **Redis caching** — weather and forecast data cached per city (10-minute TTL) to avoid hitting external API rate limits

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django + Django REST Framework |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| External API | OpenWeatherMap |
| Containerization | Docker + Docker Compose |
| Language | Python 3.14 |

---

## Project Structure

```
weather_dashboard/
├── core/
│   ├── settings.py       # Django settings, installed apps, DB config
│   └── urls.py            # Main URL router
├── weather/
│   ├── views.py           # get_weather, get_forecast views
│   ├── urls.py             # App-level routes
│   └── cache.py            # Redis connection setup
├── docker-compose.yml
├── requirements.txt
└── .env
```

---

## Setup

### Prerequisites

- Docker Desktop
- Python 3.14
- OpenWeatherMap API key (free tier at [openweathermap.org](https://openweathermap.org))

### Run locally

```bash
# Clone repo
git clone https://github.com/AndrewKhang/weather_forecast.git
cd weather_dashboard

# Create virtual environment
python -m venv venv
venv\Scripts\Activate.ps1        # PowerShell

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL and Redis containers
docker-compose up -d

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

API available at `http://127.0.0.1:8000/api/`

---

## Environment Variables

Create a `.env` file in the project root:

```env
DB_NAME=weather_db
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5434

REDIS_HOST=localhost
REDIS_PORT=6380

OPENWEATHER_API_KEY=your_openweathermap_api_key
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/weather/?city={city}` | Get current weather for a city |
| `GET` | `/api/forecast/?city={city}` | Get 5-day forecast for a city |

### GET /api/weather/?city=Hanoi

Response:

```json
{
  "city": "Hanoi",
  "country": "VN",
  "temp": 35.24,
  "feels_like": 41.25,
  "humidity": 50,
  "description": "overcast clouds",
  "icon": "04d",
  "wind_speed": 2.42
}
```

### GET /api/forecast/?city=Hanoi

Response:

```json
{
  "city": "Hanoi",
  "forecast": [
    {
      "dt_txt": "2026-06-21 12:00:00",
      "main": { "temp": 34.27, "humidity": 51, "...": "..." },
      "weather": [{ "description": "broken clouds", "icon": "04n" }]
    }
  ]
}
```

`city` defaults to `"Hanoi"` if not provided.

---

## Architecture Notes

**Caching strategy** — both endpoints follow the cache-aside pattern: check Redis first (`weather:{city}` / `forecast:{city}`), return cached data on hit, otherwise call OpenWeatherMap, cache the result with a 10-minute TTL, then return it. This protects against OpenWeatherMap's free-tier rate limit (60 calls/minute) and reduces response time on repeated requests for the same city.

**Forecast parsing** — OpenWeatherMap's free `/forecast` endpoint returns data in 3-hour intervals (40 entries covering 5 days). The API filters this down to one entry per day at 12:00, using a list comprehension on `dt_txt`.

**JSON serialization for Redis** — since Redis only stores strings, cached data is serialized with `json.dumps()` before storing and deserialized with `json.loads()` on retrieval.

---

## Roadmap

- [ ] Search history and favorite cities (PostgreSQL models)
- [ ] Frontend dashboard with forecast chart
- [ ] Deploy to Render
