from django.urls import path
from . import views

urlpatterns = [
    path("lines/", views.get_all_metro_lines, name="metro-lines"),
    path("lines/<int:line_id>/stations/", views.get_stations_by_line, name="stations-by-line"),
    path("stations/<int:station_id>/restaurants/", views.get_nearby_restaurants, name="nearby-restaurants"),
]


