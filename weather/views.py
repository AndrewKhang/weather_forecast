from django.shortcuts import render
from groq import Groq
import requests
import os, json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from weather import cache
from weather.models import SearchHistory, FavoriteCity
from .serializers import FavoriteCitySerializer
from unidecode import unidecode
# Create your views here.
def index(request):
    return render(request, 'index.html')
@api_view(['GET'])
def get_weather(request):
    city = unidecode(request.GET.get('city', 'Hanoi'))
    cached = cache.connection.get(f"weather:{city}")
    if cached:
        data = json.loads(cached)
        SearchHistory.objects.create(city=city, country=data["country"])
        return Response(data)
    
    api_key = os.getenv('OPENWEATHER_API_KEY')
    url = f"https://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=no"
    
    response = requests.get(url)
    data = response.json()
    
    if "error" in data:
        return Response({"error": "City not found"}, status=404)
    
    result = {
        "city": data["location"]["name"],
        "country": data["location"]["country"],
        "temp": data["current"]["temp_c"],
        "feels_like": data["current"]["feelslike_c"],
        "humidity": data["current"]["humidity"],
        "description": data["current"]["condition"]["text"],
        "icon": "https:" + data["current"]["condition"]["icon"],
        "wind_speed": data["current"]["wind_kph"],
        "wind_dir": data["current"]["wind_dir"],
        "uv": data["current"]["uv"],
        "coord": {"lat": data["location"]["lat"], "lon": data["location"]["lon"]},
    }
    SearchHistory.objects.create(city=city, country=result["country"])
    cache.connection.set(f"weather:{city}", json.dumps(result), ex=600)
    return Response(result)
    
@api_view(['GET'])
def get_forecast(request):
    city = unidecode(request.GET.get('city', 'Hanoi'))
    cached = cache.connection.get(f"forecast:{city}")
    if cached:
        return Response(json.loads(cached))
    
    api_key = os.getenv('OPENWEATHER_API_KEY')
    url = f"https://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=5&aqi=no&alerts=no"
    
    response = requests.get(url)
    data = response.json()
    
    if "error" in data:
        return Response({"error": "City not found"}, status=404)
    
    forecast_days = []
    for day in data["forecast"]["forecastday"]:
        forecast_days.append({
            "date": day["date"],
            "maxtemp": day["day"]["maxtemp_c"],
            "mintemp": day["day"]["mintemp_c"],
            "avgtemp": day["day"]["avgtemp_c"],
            "condition": day["day"]["condition"]["text"],
            "icon": "https:" + day["day"]["condition"]["icon"],
            "chance_of_rain": day["day"]["daily_chance_of_rain"],
            "sunrise": day["astro"]["sunrise"],
            "sunset": day["astro"]["sunset"],
            "hours": day["hour"]  # 24 hourly entries
        })
    
    result = {
        "city": data["location"]["name"],
        "forecast": forecast_days
    }
    cache.connection.set(f"forecast:{city}", json.dumps(result), ex=600)
    return Response(result)
# POST /api/favorites/ — thêm city vào favorite
# GET /api/favorites/ — lấy danh sách favorites
# DELETE /api/favorites/{city}/ — xóa favorite


@api_view(['GET'])
def get_favorites(request):
    favorites = FavoriteCity.objects.all()
    serializer = FavoriteCitySerializer(favorites, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def add_favorite(request):
    serializer = FavoriteCitySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
def delete_favorite(request, city):
    favorite = FavoriteCity.objects.filter(city=city).first()
    if not favorite:
        return Response({"message": "City not found"}, status=404)
    favorite.delete()
    return Response({"message": f"{city} has been removed from favorites"}, status=204)



@api_view(['POST'])
def chat(request):
    message = request.data.get('message')
    context = request.data.get('weather_context')
    
    client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    
    response = client.chat.completions.create(
     model="openai/gpt-oss-20b",
    messages=[
        {"role": "system", "content": f"""You are a weather assistant for WeatherIQ.

WEATHER DATA:
{context}

YOUR ROLE:
- Help users plan their day or trip based on real weather data above
- Answer in the same language the user used
- Be concise: 2-4 sentences max

BEHAVIOR:
- Good weather → suggest outdoor activities, local attractions, best time to go out
- Rainy/stormy → suggest indoor alternatives, warn about flooding or traffic
- Hot & humid → remind about hydration, sun protection, light clothing
- If user asks about a trip → give day-by-day weather summary + packing tips
- Always ground advice in the actual weather data, not generic tips
- Never greet, never ask follow-up questions, answer directly"""},
        {"role": "user", "content": message}
    ],
    max_tokens=500
)
    
    return Response({"reply": response.choices[0].message.content})