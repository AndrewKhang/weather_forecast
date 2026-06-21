from django.urls import path
from . import views

urlpatterns = [
    path('weather/', views.get_weather),
    path('forecast/', views.get_forecast),
]
