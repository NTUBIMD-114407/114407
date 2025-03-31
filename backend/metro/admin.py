from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
import requests
from .models import MetroLine, Station, Restaurant, Review

@admin.register(MetroLine)
class MetroLineAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at',)

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('name', 'metro_line', 'station_code', 'latitude', 'longitude')
    search_fields = ('name', 'station_code')
    list_filter = ('metro_line',)

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'rating', 'price_level', 'get_stations', 'view_on_map')
    search_fields = ('name', 'address', 'google_place_id')
    list_filter = ('price_level', 'rating', 'nearby_stations')
    filter_horizontal = ('nearby_stations',)
    readonly_fields = ('created_at', 'updated_at', 'view_on_map', 'fetch_place_info')
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            ('Google Places 資訊', {
                'fields': ('google_place_id', 'fetch_place_info')
            }),
            ('基本資訊', {
                'fields': ('name', 'address', 'phone', 'website')
            }),
            ('位置資訊', {
                'fields': ('latitude', 'longitude', 'nearby_stations')
            }),
            ('評分資訊', {
                'fields': ('rating', 'price_level')
            }),
        ]
        
        if obj:  # 如果是編輯現有對象
            fieldsets.append(
                ('時間戳記', {
                    'fields': ('created_at', 'updated_at'),
                    'classes': ('collapse',)
                })
            )
            fieldsets[2][1]['fields'] = ('latitude', 'longitude', 'nearby_stations', 'view_on_map')
            
        return fieldsets

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('fetch_place_details/', 
                 self.admin_site.admin_view(self.fetch_place_details),
                 name='fetch-place-details'),
        ]
        return custom_urls + urls

    def fetch_place_details(self, request):
        place_id = request.GET.get('place_id')
        if not place_id:
            return JsonResponse({'error': '請提供 Place ID'}, status=400)

        api_key = settings.GOOGLE_PLACES_API_KEY
        url = f'https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={api_key}&language=zh-TW'
        
        try:
            response = requests.get(url)
            data = response.json()
            
            if data['status'] == 'OK':
                result = data['result']
                return JsonResponse({
                    'name': result.get('name', ''),
                    'address': result.get('formatted_address', ''),
                    'latitude': result['geometry']['location']['lat'],
                    'longitude': result['geometry']['location']['lng'],
                    'phone': result.get('formatted_phone_number', ''),
                    'rating': result.get('rating', ''),
                    'website': result.get('website', ''),
                    'price_level': result.get('price_level', '')
                })
            else:
                return JsonResponse({'error': f'無法獲取地點資訊: {data.get("status")}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'發生錯誤: {str(e)}'}, status=500)

    def fetch_place_info(self, obj):
        return format_html(
            '<div class="place-info-container">'
            '<button type="button" onclick="fetchPlaceInfo()" class="button" style="background-color: #79aec8; padding: 10px 15px; color: white; border: none; border-radius: 4px; cursor: pointer;">自動填充資訊</button>'
            '<div id="place-info-status" style="margin-top: 10px;"></div>'
            '<script>'
            'function setStatus(message, isError ) {{'
            '    const statusDiv = document.getElementById("place-info-status");'
            '    statusDiv.style.color = isError ? "red" : "green";'
            '    statusDiv.textContent = message;'
            '}}'
            'function fetchPlaceInfo() {{'
            '    const placeIdInput = document.getElementById("id_google_place_id");'
            '    if (!placeIdInput) {{'
            '        setStatus("找不到 Place ID 輸入欄位", true);'
            '        return;'
            '    }}'
            '    const place_id = placeIdInput.value.trim();'
            '    if (!place_id) {{'
            '        setStatus("請先輸入 Place ID", true);'
            '        return;'
            '    }}'
            '    setStatus("正在獲取資料...");'
            '    fetch("/admin/metro/restaurant/fetch_place_details/?place_id=" + encodeURIComponent(place_id))'
            '    .then(response => {{'
            '        if (!response.ok) {{'
            '            return response.json().then(data => {{'
            '                throw new Error(data.error || "獲取資料失敗");'
            '            }});'
            '        }}'
            '        return response.json();'
            '    }})'
            '    .then(data => {{'
            '        if (data.error) {{'
            '            throw new Error(data.error);'
            '        }}'
            '        const fields = {{'
            '            "name": "id_name",'
            '            "address": "id_address",'
            '            "latitude": "id_latitude",'
            '            "longitude": "id_longitude",'
            '            "phone": "id_phone",'
            '            "rating": "id_rating",'
            '            "website": "id_website",'
            '            "price_level": "id_price_level"'
            '        }};'
            '        Object.entries(fields).forEach(([key, elementId]) => {{'
            '            const element = document.getElementById(elementId);'
            '            if (element && data[key] !== undefined && data[key] !== null) {{'
            '                element.value = data[key];'
            '            }}'
            '        }});'
            '        setStatus("資料已成功填充！");'
            '    }})'
            '    .catch(error => {{'
            '        console.error("錯誤:", error);'
            '        setStatus(error.message, true);'
            '    }});'
            '}}'
            '</script>'
            '</div>'
        )
    fetch_place_info.short_description = '自動填充'

    def get_stations(self, obj):
        if obj and obj.pk:
            return ", ".join([station.name for station in obj.nearby_stations.all()])
        return "-"
    get_stations.short_description = '鄰近捷運站'

    def view_on_map(self, obj):
        if obj and obj.pk and obj.google_place_id:
            place_url = f"https://www.google.com/maps/place/?q=place_id:{obj.google_place_id}"
            coord_url = f"https://www.google.com/maps/search/?api=1&query={obj.latitude},{obj.longitude}"
            return format_html(
                '<a href="{}" target="_blank" style="margin-right: 10px;">查看 Place</a> | '
                '<a href="{}" target="_blank" style="margin-left: 10px;">查看座標</a>',
                place_url, coord_url
            )
        return "尚未設定位置"
    view_on_map.short_description = '在地圖上查看'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'reviewer_name', 'rating', 'created_at')
    search_fields = ('restaurant__name', 'reviewer_name', 'comment')
    list_filter = ('rating', 'created_at', 'restaurant')
