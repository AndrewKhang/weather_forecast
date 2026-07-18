from django.shortcuts import render
import requests
import os, json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from weather import cache
from weather.models import SearchHistory, FavoriteCity
from .serializers import FavoriteCitySerializer
# Create your views here.
def index(request):
    return render(request, 'index.html')
@api_view(['GET'])
def get_weather(request):
    city = request.GET.get('city', 'Hanoi')
    cached = cache.connection.get(f"weather:{city}")
    if cached:
         # Redis chỉ lưu string, nên phải convert dict <-> string
        data = json.loads(cached)# loads: string → dict (đọc từ Redis)
        SearchHistory.objects.create(city=city, country=data["country"])
        return Response(data)
    api_key = os.getenv('OPENWEATHER_API_KEY')
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    response = requests.get(url)
    data = response.json()
    result={
        "city": data["name"],
        "country": data["sys"]["country"],
        "temp": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"],
        "icon": data["weather"][0]["icon"],
        "wind_speed": data["wind"]["speed"]
     }
    SearchHistory.objects.create(city=city, country=data["sys"]["country"])
    cache.connection.set(f"weather:{city}",json.dumps(result),ex=600) # dumps: dict → string (lưu vào Redis)
    return Response(result)
    
@api_view(['GET'])
def get_forecast(request):
    city = request.GET.get('city', 'Hanoi')

    cached = cache.connection.get(f"forecast:{city}")
    if cached:
        return Response(json.loads(cached))
    api_key = os.getenv('OPENWEATHER_API_KEY')
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
    
    response = requests.get(url)
    data = response.json()
    forecast_list = data["list"]
    noon_forecasts = [item for item in forecast_list if "12:00:00" in item["dt_txt"]]
    result={
        "city": data["city"]["name"],
        "forecast":noon_forecasts
   }
    cache.connection.set(f"forecast:{city}",json.dumps(result),ex=600)
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
