from rest_framework import serializers
from .models import MetroLine, Station, Restaurant, Review, MetroFirstLastTrain, MetroLastFiveTrains, Bar, BarReview
from django.conf import settings



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
    average_rating = serializers.SerializerMethodField()
    station_id = serializers.SerializerMethodField()
   
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'latitude', 'longitude', 'phone',
                 'rating', 'price_level', 'website', 'average_rating',
                 'station_id']
   
    def get_average_rating(self, obj):
        # 優化：使用 prefetch_related 後的快取資料
        reviews = obj.reviews.all()
        if not reviews:
            return None
        return round(sum(review.rating for review in reviews) / len(reviews), 1)
   
    def get_station_id(self, obj):
        # 優化：使用 prefetch_related 後的快取資料
        nearby_stations = obj.nearby_stations.all()
        if nearby_stations.exists():
            return nearby_stations.first().id
        return None



class MetroFirstLastTrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetroFirstLastTrain
        fields = [
            'line_no', 'line_id', 'station_id', 'station_name', 'station_name_en',
            'trip_head_sign', 'destination_station_id', 'destination_station_name',
            'destination_station_name_en', 'train_type', 'first_train_time',
            'last_train_time', 'monday', 'tuesday', 'wednesday', 'thursday',
            'friday', 'saturday', 'sunday', 'national_holidays'
        ]


class MetroLastFiveTrainsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetroLastFiveTrains
        fields = [
            'line_no',
            'station_id',
            'station_name',
            'destination_station_id',
            'destination_station_name',
            'train_type',
            'train_sequence',
            'train_time',
            'trip_head_sign',
            'monday',
            'tuesday',
            'wednesday',
            'thursday',
            'friday',
            'saturday',
            'sunday',
            'national_holidays'
        ]


class BarReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = BarReview
        fields = ['id', 'reviewer_name', 'rating', 'comment', 'created_at']


class BarSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    station_id = serializers.SerializerMethodField()

    class Meta:
        model = Bar
        fields = ['id', 'name', 'address', 'latitude', 'longitude', 'phone',
                 'rating', 'price_level', 'website', 'average_rating', 'station_id']

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews:
            return None
        return sum(review.rating for review in reviews) / len(reviews)

    def get_station_id(self, obj):
        nearby_stations = obj.nearby_stations.all()
        if nearby_stations.exists():
            return nearby_stations.first().id
        return None
