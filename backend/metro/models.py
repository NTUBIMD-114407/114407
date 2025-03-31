from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User

class MetroLine(models.Model):
    """捷運線路"""
    name = models.CharField(max_length=100, unique=True)  # 捷運線名稱
    color = models.CharField(max_length=20)  # 捷運線顏色
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Station(models.Model):
    """捷運站"""
    name = models.CharField(max_length=100)  # 站名
    metro_line = models.ForeignKey(MetroLine, on_delete=models.CASCADE, related_name='stations')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)  # 緯度
    longitude = models.DecimalField(max_digits=9, decimal_places=6)  # 經度
    station_code = models.CharField(max_length=10)  # 站點代碼
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.metro_line.name} - {self.name}"

class Restaurant(models.Model):
    """餐廳"""
    name = models.CharField(max_length=200)  # 店家名稱
    address = models.CharField(max_length=500)  # 地址
    latitude = models.DecimalField(max_digits=9, decimal_places=6)  # 緯度
    longitude = models.DecimalField(max_digits=9, decimal_places=6)  # 經度
    phone = models.CharField(max_length=20, blank=True, null=True)  # 電話
    google_place_id = models.CharField(max_length=100, unique=True)  # Google Places ID
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)  # Google 評分
    price_level = models.IntegerField(null=True, blank=True)  # 價格等級
    website = models.URLField(blank=True, null=True)  # 網站
    nearby_stations = models.ManyToManyField(Station, related_name='nearby_restaurants')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Review(models.Model):
    """評論"""
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')
   
    reviewer_name = models.CharField(max_length=100, blank=True, null=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['-created_at']


    def __str__(self):
        return f"{self.restaurant.name} - {self.rating}星 ({self.reviewer_name or '匿名'})"




