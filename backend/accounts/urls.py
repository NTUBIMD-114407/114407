from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('check-auth/', views.check_auth, name='check-auth'),
    path('profile/', views.profile, name='profile'),
    path('profile/avatar/', views.upload_avatar, name='upload-avatar'),
]


