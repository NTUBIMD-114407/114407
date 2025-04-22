from rest_framework import serializers
from .models import MetroLine, Station, Restaurant, Review

class MetroLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetroLine
        fields = ['id', 'name', 'color']

class StationSerializer(serializers.ModelSerializer):
    metro_line_name = serializers.CharField(source='metro_line.name', read_only=True)
    
    class Meta:
        model = Station
        fields = ['id', 'name', 'metro_line', 'metro_line_name', 'latitude', 'longitude', 'station_code']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'reviewer_name', 'rating', 'comment', 'created_at']

class RestaurantSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'latitude', 'longitude', 'phone', 
                 'rating', 'price_level', 'website', 'reviews', 'average_rating']
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews:
            return None
        return sum(review.rating for review in reviews) / len(reviews) 