from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from .models import Station, Restaurant, MetroLine
from .serializers import StationSerializer, RestaurantSerializer, MetroLineSerializer

# Create your views here.

@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_metro_lines(request):
    """獲取所有捷運線"""
    lines = MetroLine.objects.all()
    serializer = MetroLineSerializer(lines, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_stations_by_line(request, line_id):
    """獲取指定捷運線的所有站點"""
    line = get_object_or_404(MetroLine, id=line_id)
    stations = Station.objects.filter(metro_line=line)
    serializer = StationSerializer(stations, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_nearby_restaurants(request, station_id):
    """獲取指定捷運站附近的餐廳"""
    station = get_object_or_404(Station, id=station_id)
    restaurants = station.nearby_restaurants.all()
    serializer = RestaurantSerializer(restaurants, many=True)
    return Response(serializer.data)
