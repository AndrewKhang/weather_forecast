import pytest

@pytest.mark.django_db
def test_weather_cache_hit(client, mocker):
    # Mock Redis trả về data có sẵn
    mock_cache = mocker.patch('weather.views.cache.connection')
    mock_cache.get.return_value = '{"city": "Hanoi", "country": "Vietnam", "temp": 32.0, "feels_like": 38.5, "humidity": 75, "description": "Sunny", "icon": "//icon.png", "wind_speed": 14.4, "wind_dir": "SSE", "uv": 7.0, "coord": {"lat": 21.03, "lon": 105.85}}'

    response = client.get('/api/weather/?city=Hanoi')

    assert response.status_code == 200
    assert response.json()['city'] == 'Hanoi'
    assert response.json()['temp'] == 32.0
    mock_cache.get.assert_called_once_with('weather:Hanoi')
    
@pytest.mark.django_db
def test_city_not_found(client, mocker):
    mock_cache = mocker.patch('weather.views.cache.connection')
    mock_cache.get.return_value = None

    mock_requests = mocker.patch('weather.views.requests.get')
    mock_requests.return_value.json.return_value = {"error": "city not found"}

    response = client.get('/api/weather/?city=FakeCity')  

    assert response.status_code == 404
    assert response.json()['error'] == 'City not found'
    
@pytest.mark.django_db
def test_city_found(client, mocker):
    mock_cache = mocker.patch('weather.views.cache.connection')
    mock_cache.get.return_value = None

    mock_requests = mocker.patch('weather.views.requests.get')
    mock_requests.return_value.json.return_value = {
        "location": {"name": "Hanoi", "country": "Vietnam", "lat": 21.03, "lon": 105.85},
        "current": {
            "temp_c": 32.0,
            "feelslike_c": 38.5,
            "humidity": 75,
            "condition": {"text": "Sunny", "icon": "//icon.png"},
            "wind_kph": 14.4,
            "wind_dir": "SSE",
            "uv": 7.0
        }
    }

    response = client.get('/api/weather/?city=Hanoi')  

    assert response.status_code == 200
    assert response.json()['city'] == 'Hanoi'
    mock_cache.set.assert_called_once()
    