from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.


class User(AbstractUser):
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=100, blank=True, null=True)
    GENDER_CHOICES = (
        ("male", "男"),
        ("female", "女"),
        ("other", "其他"),
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    # 添加related_name來解決衝突
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )


    def __str__(self):
        return self.email




