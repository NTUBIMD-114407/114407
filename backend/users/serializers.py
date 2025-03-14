from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Business, BusinessPhoto, Review, MetroLine, MetroStation

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class MetroLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetroLine
        fields = ['id', 'code', 'name', 'color']

class MetroStationSerializer(serializers.ModelSerializer):
    line = MetroLineSerializer(read_only=True)
    
    class Meta:
        model = MetroStation
        fields = ['id', 'line', 'code', 'name', 'latitude', 'longitude']

class BusinessPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessPhoto
        fields = ['id', 'photo_url', 'width', 'height']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'author_name', 'rating', 'text', 'time', 'language']

class BusinessSerializer(serializers.ModelSerializer):
    photos = BusinessPhotoSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    nearest_station = MetroStationSerializer(read_only=True)
    
    class Meta:
        model = Business
        fields = [
            'id', 'google_place_id', 'name', 'address', 
            'latitude', 'longitude', 'phone', 'website',
            'rating', 'rating_count', 'business_status',
            'types', 'opening_hours', 'last_updated', 
            'photos', 'reviews', 'nearest_station',
            'distance_to_station'
        ] 