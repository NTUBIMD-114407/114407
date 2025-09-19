from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User
from django.conf import settings
from django.utils import timezone





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
    latitude = models.DecimalField(max_digits=15, decimal_places=12)  # 緯度
    longitude = models.DecimalField(max_digits=15, decimal_places=12)  # 經度
    station_code = models.CharField(max_length=10)  # 站點代碼
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




    def __str__(self):
        return f"{self.metro_line.name} - {self.name}"


class FoodCategory(models.Model):
    """美食分類"""
    name = models.CharField(max_length=50, unique=True, verbose_name='分類名稱')  # 分類名稱
    description = models.TextField(blank=True, null=True, verbose_name='分類描述')  # 分類描述
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = '美食分類'
        verbose_name_plural = '美食分類'
        ordering = ['name']


    def __str__(self):
        return self.name





class BusinessHours(models.Model):
    """餐廳營業時間"""
    DAY_CHOICES = [
        (0, '星期一'),
        (1, '星期二'),
        (2, '星期三'),
        (3, '星期四'),
        (4, '星期五'),
        (5, '星期六'),
        (6, '星期日'),
    ]
   
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, related_name='business_hours')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)  # 星期幾
    open_time = models.TimeField()  # 開店時間
    close_time = models.TimeField()  # 關店時間
    is_closed = models.BooleanField(default=False)  # 是否休息
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = '營業時間'
        verbose_name_plural = '營業時間'
        unique_together = ('restaurant', 'day_of_week')
        ordering = ['day_of_week', 'open_time']



    def __str__(self):
        if self.is_closed:
            return f"{self.get_day_of_week_display()} - 休息"
        return f"{self.get_day_of_week_display()} - {self.open_time.strftime('%H:%M')} ~ {self.close_time.strftime('%H:%M')}"



class Restaurant(models.Model):
    """餐廳"""
    name = models.CharField(max_length=200)  # 店家名稱
    address = models.CharField(max_length=500)  # 地址
    latitude = models.DecimalField(max_digits=15, decimal_places=12)  # 緯度
    longitude = models.DecimalField(max_digits=15, decimal_places=12)  # 經度
    phone = models.CharField(max_length=20, blank=True, null=True)  # 電話
    google_place_id = models.CharField(max_length=100, unique=True)  # Google Places ID
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)  # Google 評分
    price_level = models.IntegerField(null=True, blank=True)  # 價格等級
    website = models.URLField(blank=True, null=True)  # 網站
    image = models.CharField(max_length=500, null=True, blank=True)  # Google Places 照片參考值
    nearby_stations = models.ManyToManyField(Station, related_name='nearby_restaurants')
    categories = models.ManyToManyField(FoodCategory, related_name='restaurants', verbose_name='美食分類')  # 新增美食分類
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_review_update = models.DateTimeField(null=True, blank=True)  # 最後評論更新時間



    def __str__(self):
        return self.name


class Review(models.Model):
    """餐廳評論"""
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    reviewer_name = models.CharField(max_length=100, blank=True, null=True)
    rating = models.IntegerField()  # 評分 (1-5)
    comment = models.TextField(blank=True)  # 評論內容
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.restaurant.name} - {self.rating}星 ({self.reviewer_name or '匿名'})"



# =============================
# 酒吧資料模型（與餐廳結構一致）
# =============================

class BarCategory(models.Model):
    """酒吧分類"""
    name = models.CharField(max_length=50, unique=True, verbose_name='分類名稱')
    description = models.TextField(blank=True, null=True, verbose_name='分類描述')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '酒吧分類'
        verbose_name_plural = '酒吧分類'
        ordering = ['name']

    def __str__(self):
        return self.name


class Bar(models.Model):
    """酒吧"""
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=500)
    latitude = models.DecimalField(max_digits=15, decimal_places=12)
    longitude = models.DecimalField(max_digits=15, decimal_places=12)
    phone = models.CharField(max_length=20, blank=True, null=True)
    google_place_id = models.CharField(max_length=100, unique=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    price_level = models.IntegerField(null=True, blank=True)
    website = models.URLField(blank=True, null=True)
    image = models.CharField(max_length=500, null=True, blank=True)
    nearby_stations = models.ManyToManyField(Station, related_name='nearby_bars')
    categories = models.ManyToManyField(BarCategory, related_name='bars', verbose_name='酒吧分類')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_review_update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class BarBusinessHours(models.Model):
    """酒吧營業時間"""
    DAY_CHOICES = [
        (0, '星期一'),
        (1, '星期二'),
        (2, '星期三'),
        (3, '星期四'),
        (4, '星期五'),
        (5, '星期六'),
        (6, '星期日'),
    ]

    bar = models.ForeignKey('Bar', on_delete=models.CASCADE, related_name='business_hours')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    open_time = models.TimeField()
    close_time = models.TimeField()
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '酒吧營業時間'
        verbose_name_plural = '酒吧營業時間'
        unique_together = ('bar', 'day_of_week')
        ordering = ['day_of_week', 'open_time']

    def __str__(self):
        if self.is_closed:
            return f"{self.get_day_of_week_display()} - 休息"
        return f"{self.get_day_of_week_display()} - {self.open_time.strftime('%H:%M')} ~ {self.close_time.strftime('%H:%M')}"


class BarReview(models.Model):
    """酒吧評論"""
    bar = models.ForeignKey(Bar, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bar_reviews', null=True, blank=True)
    reviewer_name = models.CharField(max_length=100, blank=True, null=True)
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.bar.name} - {self.rating}星 ({self.reviewer_name or '匿名'})"

class TrainInfo(models.Model):
    """列車到站資訊"""
    train_number = models.CharField(max_length=50, blank=True)
    station_name = models.CharField(max_length=100)
    destination_name = models.CharField(max_length=100)
    count_down = models.CharField(max_length=50)
    now_date_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.station_name} -> {self.destination_name} ({self.count_down})"



class YouBikeStation(models.Model):
    """YouBike 站點"""
    station_id = models.CharField(max_length=10, unique=True)  # 站點代碼
    name = models.CharField(max_length=100)  # 站點名稱
    total_spaces = models.IntegerField()  # 總停車格數
    available_spaces = models.IntegerField()  # 可停車格數
    available_bikes = models.IntegerField()  # 可借車輛數
    latitude = models.DecimalField(max_digits=15, decimal_places=12)  # 緯度
    longitude = models.DecimalField(max_digits=15, decimal_places=12)  # 經度
    address = models.CharField(max_length=200)  # 地址
    nearby_stations = models.ManyToManyField(Station, related_name='nearby_youbike_stations')  # 附近的捷運站
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_update = models.DateTimeField(null=True, blank=True)  # 最後更新時間


    class Meta:
        verbose_name = 'YouBike 站點'
        verbose_name_plural = 'YouBike 站點'
        ordering = ['name']


    def __str__(self):
        return f"{self.name} ({self.available_bikes}/{self.total_spaces})"


    def update_status(self, available_bikes, available_spaces):
        """更新站點狀態"""
        self.available_bikes = available_bikes
        self.available_spaces = available_spaces
        self.last_update = timezone.now()
        self.save()
        # 創建歷史記錄
        YouBikeHistory.create_from_station(self)


class YouBikeHistory(models.Model):
    """YouBike 歷史數據"""
    station = models.ForeignKey(YouBikeStation, on_delete=models.CASCADE, related_name='history')
    available_bikes = models.IntegerField()  # 可借車輛數
    available_spaces = models.IntegerField()  # 可停車格數
    timestamp = models.DateTimeField()  # 記錄時間
    day_of_week = models.IntegerField()  # 星期幾 (0-6, 0是星期一)
    hour = models.IntegerField()  # 小時 (0-23)
    minute = models.IntegerField(default=0)  # 分鐘 (0-59)
    is_holiday = models.BooleanField(default=False)  # 是否為假日
    weather = models.CharField(max_length=50, blank=True, null=True)  # 天氣狀況
    temperature = models.FloatField(null=True, blank=True)  # 溫度

    class Meta:
        verbose_name = 'YouBike 歷史記錄'
        verbose_name_plural = 'YouBike 歷史記錄'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['station', 'timestamp']),
            models.Index(fields=['day_of_week', 'hour']),
        ]



    def __str__(self):
        return f"{self.station.name} - {self.timestamp} ({self.available_bikes}台可借)"


    @classmethod
    def create_from_station(cls, station, weather=None, temperature=None):
        """從站點創建歷史記錄"""
        now = timezone.now()
       
        return cls.objects.create(
            station=station,
            available_bikes=station.available_bikes,
            available_spaces=station.available_spaces,
            timestamp=now,
            day_of_week=now.weekday(),
            hour=now.hour,
            minute=now.minute,
            is_holiday=cls._is_holiday(now),
            weather=weather,
            temperature=temperature
        )


    @staticmethod
    def _is_holiday(date):
        """判斷是否為假日"""
        return date.weekday() >= 5  # 簡單判斷週末

class CheckinReview(models.Model):
    """打卡版評論模型"""
    restaurant_name = models.CharField(max_length=100, verbose_name='餐廳名稱')
    metro_line = models.CharField(max_length=50, verbose_name='捷運線')
    reviewer_name = models.CharField(max_length=50, default='匿名', verbose_name='評論者名稱')
    rating = models.IntegerField(verbose_name='評分')
    comment = models.TextField(blank=True, verbose_name='評論內容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='創建時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新時間')


    class Meta:
        db_table = 'metro_checkinreview'
        verbose_name = '打卡評論'
        verbose_name_plural = '打卡評論'
        ordering = ['-created_at']


    def __str__(self):
        return f'{self.restaurant_name} - {self.reviewer_name}'



class StationID(models.Model):
    """車站ID對照表"""
    station_name = models.CharField(max_length=100)  # 車站名稱
    line_name = models.CharField(max_length=100)     # 線路名稱
    station_id = models.CharField(max_length=20, unique=True)  # 車站ID


    def __str__(self):
        return f"{self.line_name} - {self.station_name} ({self.station_id})"




class MetroFirstLastTrain(models.Model):
    """捷運首末班車資訊"""
    line_no = models.CharField(max_length=10, verbose_name='路線編號')
    line_id = models.CharField(max_length=10, verbose_name='路線ID')
    station_id = models.CharField(max_length=10, verbose_name='站點ID')
    station_name = models.CharField(max_length=100, verbose_name='站點名稱')
    station_name_en = models.CharField(max_length=100, verbose_name='站點英文名稱')
    trip_head_sign = models.CharField(max_length=100, verbose_name='列車方向')
    destination_station_id = models.CharField(max_length=10, verbose_name='目的地站點ID')
    destination_station_name = models.CharField(max_length=100, verbose_name='目的地站點名稱')
    destination_station_name_en = models.CharField(max_length=100, verbose_name='目的地站點英文名稱')
    train_type = models.IntegerField(verbose_name='列車類型')
    first_train_time = models.TimeField(verbose_name='首班車時間')
    last_train_time = models.TimeField(verbose_name='末班車時間')
   
    # 服務日
    monday = models.BooleanField(default=True, verbose_name='週一')
    tuesday = models.BooleanField(default=True, verbose_name='週二')
    wednesday = models.BooleanField(default=True, verbose_name='週三')
    thursday = models.BooleanField(default=True, verbose_name='週四')
    friday = models.BooleanField(default=True, verbose_name='週五')
    saturday = models.BooleanField(default=True, verbose_name='週六')
    sunday = models.BooleanField(default=True, verbose_name='週日')
    national_holidays = models.BooleanField(default=True, verbose_name='國定假日')
   
    src_update_time = models.DateTimeField(verbose_name='來源更新時間')
    update_time = models.DateTimeField(verbose_name='更新時間')
    version_id = models.IntegerField(verbose_name='版本ID')
   
    class Meta:
        verbose_name = '捷運首末班車'
        verbose_name_plural = '捷運首末班車'
        ordering = ['line_no', 'station_id', 'first_train_time']
        unique_together = ['line_no', 'station_id', 'destination_station_id', 'train_type']


    def __str__(self):
        return f"{self.station_name} - {self.trip_head_sign} ({self.first_train_time} - {self.last_train_time})"



class MetroLastFiveTrains(models.Model):
    """捷運末五班車資訊"""
    line_no = models.CharField(max_length=10, verbose_name='路線編號')
    line_id = models.CharField(max_length=10, verbose_name='路線ID')
    station_id = models.CharField(max_length=10, verbose_name='站點ID')
    station_name = models.CharField(max_length=100, verbose_name='站點名稱')
    station_name_en = models.CharField(max_length=100, verbose_name='站點英文名稱')
    trip_head_sign = models.CharField(max_length=100, verbose_name='列車方向')
    destination_station_id = models.CharField(max_length=10, verbose_name='目的地站點ID')
    destination_station_name = models.CharField(max_length=100, verbose_name='目的地站點名稱')
    destination_station_name_en = models.CharField(max_length=100, verbose_name='目的地站點英文名稱')
    train_type = models.IntegerField(verbose_name='列車類型')
    train_time = models.TimeField(verbose_name='列車時間')
    train_sequence = models.IntegerField(verbose_name='班次序號')  # 1-5 表示末五班車的順序
   
    # 服務日
    monday = models.BooleanField(default=True, verbose_name='週一')
    tuesday = models.BooleanField(default=True, verbose_name='週二')
    wednesday = models.BooleanField(default=True, verbose_name='週三')
    thursday = models.BooleanField(default=True, verbose_name='週四')
    friday = models.BooleanField(default=True, verbose_name='週五')
    saturday = models.BooleanField(default=True, verbose_name='週六')
    sunday = models.BooleanField(default=True, verbose_name='週日')
    national_holidays = models.BooleanField(default=True, verbose_name='國定假日')
   
    src_update_time = models.DateTimeField(verbose_name='來源更新時間')
    update_time = models.DateTimeField(verbose_name='更新時間')
    version_id = models.IntegerField(verbose_name='版本ID')
   
    class Meta:
        verbose_name = '捷運末五班車'
        verbose_name_plural = '捷運末五班車'
        ordering = ['line_no', 'station_id', 'train_sequence']
        unique_together = ['line_no', 'station_id', 'destination_station_id', 'train_type', 'train_sequence']


    def __str__(self):
        return f"{self.station_name} - {self.trip_head_sign} ({self.train_time}) - 第{self.train_sequence}班"

