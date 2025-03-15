from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'metro/lines', views.MetroLineViewSet)
router.register(r'metro/stations', views.MetroStationViewSet)
router.register(r'businesses', views.BusinessViewSet)

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('', include(router.urls)),
] 