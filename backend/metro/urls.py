from django.urls import path
from . import views


urlpatterns = [
    path("lines/", views.get_all_metro_lines, name="metro-lines"),
    path("lines/<int:line_id>/stations/", views.get_stations_by_line, name="stations-by-line"),
    path("stations/<int:station_id>/restaurants/", views.get_nearby_restaurants, name="nearby-restaurants"),
    path("restaurants/<int:restaurant_id>/", views.get_restaurant_details, name="restaurant-details"),
    path("restaurants/<int:restaurant_id>/reviews/", views.get_restaurant_reviews, name="restaurant-reviews"),
    path("track-info/", views.get_track_info, name="track-info"),
    path("latest-trains/", views.get_latest_train_info, name="latest-trains"),
    path("accounts/user/", views.get_user_info, name="user-info"),
    path('api/restaurants/<int:restaurant_id>/reviews/', views.create_restaurant_review, name='create_restaurant_review'),
    path('api/checkin-reviews/', views.create_checkin_review_api, name='create_checkin_review'),
    path('api/checkin-reviews/<int:review_id>/', views.update_checkin_review_api, name='update_checkin_review'),
    path('api/checkin-reviews/list/', views.get_checkin_reviews_api, name='get_checkin_reviews'),
    path('api/restaurant-reviews/', views.create_restaurant_review, name='create_restaurant_review'),
    path('api/restaurant-reviews/<int:review_id>/', views.update_restaurant_review, name='update_restaurant_review'),
    path('api/metro-lines/restaurants/', views.get_all_metro_line_restaurants, name='get_all_metro_line_restaurants'),
    path('api/restaurants/', views.get_all_restaurants, name='get_all_restaurants'),
    path('api/restaurants/top10/', views.get_top10_restaurants, name='get_top10_restaurants'),
    path('restaurants/search/', views.search_restaurants, name='search-restaurants'),
    path('reviews/', views.get_reviews, name='reviews'),
    path('api/top-checkin-restaurants/', views.get_top_checkin_restaurants, name='top_checkin_restaurants'),
    path('api/restaurants/night/', views.night_restaurants, name='night-restaurants'),
    path('api/metro-route/', views.get_metro_route, name='get_metro_route'),
    path('station/<str:station_id>/first-last-trains/', views.get_station_first_last_trains, name='station-first-last-trains'),
    path('api/station-by-name/<str:station_name>/first-last-trains/', views.get_station_by_name_first_last_trains, name='station-by-name-first-last-trains'),
    path('api/station-last-five-trains/', views.get_station_last_five_trains, name='station-last-five-trains'),

    # Category-based restaurant filters
    path('api/restaurants/by-station-and-category/', views.get_restaurants_by_station_and_category, name='restaurants_by_station_and_category'),
    path('api/restaurants/by-line-and-category/', views.get_restaurants_by_line_and_category, name='restaurants_by_line_and_category'),
    path('api/restaurants/by-station-line-and-category/', views.get_restaurants_by_station_line_and_category, name='restaurants_by_station_line_and_category'),

    # Bars
    path('bars/', views.BarViewSet.as_view({'get': 'list'}), name='bars-list'),
    path('bars/<int:pk>/', views.BarViewSet.as_view({'get': 'retrieve'}), name='bars-detail'),
    path('bars/by-station/', views.get_bars_by_station, name='bars-by-station'),
    path('bars/by-line/', views.get_bars_by_line, name='bars-by-line'),
    path('bars/<int:bar_id>/reviews/', views.get_bar_reviews, name='bar-reviews'),
    path('api/bars/<int:bar_id>/reviews/', views.create_bar_review, name='create_bar_review'),
    path('api/bar-reviews/<int:review_id>/', views.update_bar_review, name='update_bar_review'),
    path('api/bars/night/', views.night_bars, name='night-bars'),
    
    # 打卡評論喜歡/收藏功能
    path('api/checkin-reviews/<int:review_id>/like/', views.toggle_checkin_review_like, name='toggle_checkin_review_like'),
    path('api/checkin-reviews/<int:review_id>/favorite/', views.toggle_checkin_review_favorite, name='toggle_checkin_review_favorite'),
    path('api/checkin-reviews/<int:review_id>/stats/', views.get_checkin_review_stats, name='get_checkin_review_stats'),
    
    # 通知功能
    path('api/notifications/', views.get_user_notifications, name='get_user_notifications'),
    path('api/notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('api/notifications/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('api/notifications/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    
    # 用戶收藏列表
    path('api/user/favorites/', views.get_user_favorites, name='get_user_favorites'),
]