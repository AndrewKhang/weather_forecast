from django.urls import path
from . import views

urlpatterns = [
    path('weather/', views.get_weather),
    path('forecast/', views.get_forecast),
    path('favorites/', views.get_favorites),
    path('favorites/', views.get_favorites),
    path('favorites/add/', views.add_favorite),
    path('favorites/<str:city>/', views.delete_favorite),
]
