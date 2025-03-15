from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from datetime import datetime

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField('電子信箱', unique=True)
    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class MetroLine(models.Model):
    code = models.CharField('線路代碼', max_length=10, unique=True)  # 例如: BL(板南線), R(淡水信義線)
    name = models.CharField('線路名稱', max_length=50)  # 例如: 板南線
    color = models.CharField('線路顏色', max_length=7)  # 例如: #0070BD

    class Meta:
        verbose_name = '捷運線'
        verbose_name_plural = '捷運線'

    def __str__(self):
        return f'{self.name} ({self.code})'

class MetroStation(models.Model):
    line = models.ForeignKey(MetroLine, on_delete=models.CASCADE, related_name='stations')
    code = models.CharField('站點代碼', max_length=10)  # 例如: BL12
    name = models.CharField('站點名稱', max_length=50)  # 例如: 市政府站
    latitude = models.DecimalField('緯度', max_digits=19, decimal_places=16)
    longitude = models.DecimalField('經度', max_digits=19, decimal_places=16)

    class Meta:
        verbose_name = '捷運站'
        verbose_name_plural = '捷運站'
        unique_together = ['line', 'code']

    def __str__(self):
        return f'{self.name} ({self.code})'

class Business(models.Model):
    google_place_id = models.CharField('Google Place ID', max_length=255, unique=True)
    name = models.CharField('商家名稱', max_length=255)
    address = models.CharField('地址', max_length=255)
    latitude = models.DecimalField('緯度', max_digits=19, decimal_places=16)
    longitude = models.DecimalField('經度', max_digits=19, decimal_places=16)
    phone = models.CharField('電話', max_length=50, blank=True, null=True)
    website = models.URLField('網站', blank=True, null=True)
    rating = models.DecimalField('評分', max_digits=2, decimal_places=1, null=True)
    rating_count = models.IntegerField('評分數量', default=0)
    business_status = models.CharField('營業狀態', max_length=50)
    types = models.JSONField('商家類型', null=True, blank=True)
    opening_hours = models.JSONField('營業時間', null=True, blank=True)
    last_updated = models.DateTimeField('最後更新時間', auto_now=True)
    nearest_station = models.ForeignKey(MetroStation, on_delete=models.SET_NULL, 
                                      null=True, related_name='nearby_businesses')
    distance_to_station = models.IntegerField('離車站距離(公尺)', null=True)

    class Meta:
        verbose_name = '商家'
        verbose_name_plural = '商家'
        indexes = [
            models.Index(fields=['nearest_station', 'distance_to_station']),
            models.Index(fields=['rating', '-rating_count']),
        ]

    def __str__(self):
        return self.name

class BusinessPhoto(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='photos')
    photo_reference = models.CharField('Google 相片參考ID', max_length=255)
    photo_url = models.URLField('相片網址')
    width = models.IntegerField('寬度')
    height = models.IntegerField('高度')
    created_at = models.DateTimeField('建立時間', auto_now_add=True)

    class Meta:
        verbose_name = '商家相片'
        verbose_name_plural = '商家相片'

class Review(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='reviews')
    google_review_id = models.CharField('Google Review ID', max_length=255, unique=True)
    author_name = models.CharField('評論者名稱', max_length=255)
    rating = models.IntegerField('評分')
    text = models.TextField('評論內容')
    time = models.DateTimeField('評論時間')
    language = models.CharField('語言', max_length=10, blank=True)
    profile_photo_url = models.URLField('評論者頭像', blank=True, null=True)
    relative_time_description = models.CharField('相對時間描述', max_length=50, blank=True)
    created_at = models.DateTimeField('建立時間', default=datetime.now)
    updated_at = models.DateTimeField('更新時間', default=datetime.now)

    class Meta:
        verbose_name = '評論'
        verbose_name_plural = '評論'
        ordering = ['-time']
        indexes = [
            models.Index(fields=['business', '-time']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return f'{self.author_name} - {self.rating}星 ({self.time.strftime("%Y-%m-%d")})'

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()
        super().save(*args, **kwargs)
