from django.contrib import admin
from django.http import JsonResponse
from .models import CustomUser, MetroLine, MetroStation, Business, BusinessPhoto, Review
import requests
import os
from django.urls import path
from django.shortcuts import render

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_staff', 'is_active')
    search_fields = ('email',)

@admin.register(MetroLine)
class MetroLineAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'color')
    search_fields = ('code', 'name')

@admin.register(MetroStation)
class MetroStationAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'line', 'latitude', 'longitude')
    list_filter = ('line',)
    search_fields = ('code', 'name')

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'rating', 'nearest_station', 'distance_to_station')
    list_filter = ('nearest_station__line', 'business_status')
    search_fields = ('name', 'address')
    fields = ('google_place_id', 'name', 'address', 'latitude', 'longitude', 
             'phone', 'website', 'rating', 'rating_count', 'business_status',
             'types', 'opening_hours', 'nearest_station', 'distance_to_station')
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('fetch-place-details/', self.fetch_place_details, name='fetch-place-details'),
        ]
        return custom_urls + urls

    def fetch_place_details(self, request):
        place_id = request.GET.get('place_id')
        if not place_id:
            return JsonResponse({'error': '需要提供 place_id'}, status=400)

        # 使用新的 API Key
        api_key = 'AIzaSyAdx3uArkvYTuOJx0hjFxRfxxqWgy5yvNY'
        if not api_key:
            print("API Key not found in environment variables!")  # 調試用
            return JsonResponse({'error': '未設定 Google Maps API Key'}, status=500)

        print(f"Using API Key: {api_key[:5]}...")  # 只顯示前5個字符，用於調試

        url = f"https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            'place_id': place_id,
            'key': api_key,
            'fields': 'name,formatted_address,geometry,formatted_phone_number,website,rating,user_ratings_total,business_status,types,opening_hours',
            'language': 'zh-TW'  # 設定回傳語言為繁體中文
        }
        
        try:
            response = requests.get(url, params=params)
            print(f"API URL: {response.url}")  # 調試用（注意：URL 中會包含 API key）
            data = response.json()
            
            print("Google Places API Response:", data)  # 調試用
            
            if data.get('status') != 'OK':
                return JsonResponse({
                    'error': f'無法獲取商家資訊: {data.get("status")} - {data.get("error_message", "未知錯誤")}'
                }, status=400)

            result = data['result']
            return JsonResponse({
                'name': result.get('name', ''),
                'address': result.get('formatted_address', ''),
                'latitude': result['geometry']['location']['lat'],
                'longitude': result['geometry']['location']['lng'],
                'phone': result.get('formatted_phone_number', ''),
                'website': result.get('website', ''),
                'rating': result.get('rating'),
                'rating_count': result.get('user_ratings_total', 0),
                'business_status': result.get('business_status', ''),
                'types': result.get('types', []),
                'opening_hours': result.get('opening_hours', {})
            })
        except requests.RequestException as e:
            print("API Request Error:", str(e))  # 調試用
            return JsonResponse({'error': f'API 請求錯誤: {str(e)}'}, status=500)
        except KeyError as e:
            print("Data Processing Error:", str(e))  # 調試用
            return JsonResponse({'error': f'資料處理錯誤: {str(e)}'}, status=500)
        except Exception as e:
            print("Unexpected Error:", str(e))  # 調試用
            return JsonResponse({'error': f'未預期的錯誤: {str(e)}'}, status=500)

    class Media:
        js = ('admin/js/business_admin.js',)

@admin.register(BusinessPhoto)
class BusinessPhotoAdmin(admin.ModelAdmin):
    list_display = ('business', 'photo_url', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('business__name',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('business', 'author_name', 'rating', 'time')
    list_filter = ('rating', 'language')
    search_fields = ('business__name', 'author_name', 'text')
