from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
import requests
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User



from .models import (
    MetroLine, Station, Restaurant, Review,
    TrainInfo, YouBikeStation, YouBikeHistory,
    CheckinReview, CheckinReviewLike, CheckinReviewFavorite, Notification,
    BusinessHours,User,MetroFirstLastTrain,
    MetroLastFiveTrains,
    BarCategory, Bar, BarReview, BarBusinessHours
)




@admin.register(MetroFirstLastTrain)
class MetroFirstLastTrainAdmin(admin.ModelAdmin):
    list_display = ('station_name', 'first_train_time', 'last_train_time')



@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'date_joined', 'is_staff')



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



@admin.register(BusinessHours)
class BusinessHoursAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'get_day_of_week_display', 'open_time', 'close_time', 'is_closed')
    list_filter = ('day_of_week', 'is_closed')
    search_fields = ('restaurant__name',)
    ordering = ('restaurant__name', 'day_of_week')


class BusinessHoursInline(admin.TabularInline):
    model = BusinessHours
    extra = 7  # 預設顯示一週的營業時間
    max_num = 7  # 最多只能有7天的營業時間


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'rating', 'price_level', 'get_stations', 'view_on_map')
    search_fields = ('name', 'address', 'google_place_id')
    list_filter = ('price_level', 'rating', 'nearby_stations')
    filter_horizontal = ('nearby_stations',)
    readonly_fields = ('created_at', 'updated_at', 'view_on_map', 'fetch_place_info')
    inlines = [BusinessHoursInline]  # 添加營業時間的內聯管理
   
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
        url = f'https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={api_key}&language=zh-TW&fields=name,formatted_address,geometry,formatted_phone_number,rating,website,price_level,opening_hours,types'
       
        try:
            response = requests.get(url)
            data = response.json()
           
            if data['status'] == 'OK':
                result = data['result']
                opening_hours = result.get('opening_hours', {})
                periods = opening_hours.get('periods', [])
               
                # 準備營業時間數據
                business_hours_data = []
                for period in periods:
                    open_day = period.get('open', {}).get('day', 0)
                    open_time = period.get('open', {}).get('time', '0000')
                    close_time = period.get('close', {}).get('time', '0000')
                   
                    # 將時間格式轉換為 HH:MM
                    open_time_formatted = f"{open_time[:2]}:{open_time[2:]}"
                    close_time_formatted = f"{close_time[:2]}:{close_time[2:]}"
                   
                    business_hours_data.append({
                        'day_of_week': open_day,
                        'open_time': open_time_formatted,
                        'close_time': close_time_formatted,
                        'is_closed': False
                    })




                # 處理餐廳類型
                place_types = result.get('types', [])
                food_categories = []
               
                # 類型映射字典
                type_to_category = {
                    'restaurant': '其他料理',
                    'food': '其他料理',
                    'chinese_restaurant': '中式料理',
                    'japanese_restaurant': '日本料理',
                    'korean_restaurant': '韓式料理',
                    'italian_restaurant': '義式料理',
                    'american_restaurant': '美式料理',
                    'thai_restaurant': '泰式料理',
                    'vietnamese_restaurant': '越式料理',
                    'vegetarian_restaurant': '素食',
                    'cafe': '甜點',
                    'bakery': '甜點',
                    'breakfast_restaurant': '早午餐',
                    'hot_pot_restaurant': '火鍋',
                    'barbecue_restaurant': '燒烤',
                    'night_market': '小吃',
                    'beverage_store': '飲料'
                }




                # 根據 Google Places 類型判斷美食分類
                for place_type in place_types:
                    if place_type in type_to_category:
                        category_name = type_to_category[place_type]
                        if category_name not in food_categories:
                            food_categories.append(category_name)
               
                return JsonResponse({
                    'name': result.get('name', ''),
                    'address': result.get('formatted_address', ''),
                    'latitude': result['geometry']['location']['lat'],
                    'longitude': result['geometry']['location']['lng'],
                    'phone': result.get('formatted_phone_number', ''),
                    'rating': result.get('rating', ''),
                    'website': result.get('website', ''),
                    'price_level': result.get('price_level', ''),
                    'business_hours': business_hours_data,
                    'food_categories': food_categories
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
            'function setStatus(message, isError) {{'
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
           
            '        // 填充營業時間'
            '        if (data.business_hours && data.business_hours.length > 0) {{'
            '            const businessHoursContainer = document.querySelector(".tabular.inline-related");'
            '            if (businessHoursContainer) {{'
            '                data.business_hours.forEach((hours, hourIndex) => {{'
            '                    const daySelect = businessHoursContainer.querySelector(`select[name="businesshours_set-${{hourIndex}}-day_of_week"]`);'
            '                    const openTimeInput = businessHoursContainer.querySelector(`input[name="businesshours_set-${{hourIndex}}-open_time"]`);'
            '                    const closeTimeInput = businessHoursContainer.querySelector(`input[name="businesshours_set-${{hourIndex}}-close_time"]`);'
            '                    const isClosedCheckbox = businessHoursContainer.querySelector(`input[name="businesshours_set-${{hourIndex}}-is_closed"]`);'
           
            '                    if (daySelect) daySelect.value = hours.day_of_week;'
            '                    if (openTimeInput) openTimeInput.value = hours.open_time;'
            '                    if (closeTimeInput) closeTimeInput.value = hours.close_time;'
            '                    if (isClosedCheckbox) isClosedCheckbox.checked = hours.is_closed;'
            '                }});'
            '            }}'
            '        }}'




            '        // 填充美食分類'
            '        if (data.food_categories && data.food_categories.length > 0) {{'
            '            const categoriesSelect = document.getElementById("id_categories");'
            '            if (categoriesSelect) {{'
            '                const options = Array.from(categoriesSelect.options);'
            '                options.forEach(option => {{'
            '                    if (data.food_categories.includes(option.text)) {{'
            '                        option.selected = true;'
            '                    }}'
            '                }});'
            '                // 觸發 change 事件以更新多選框的顯示'
            '                const event = new Event("change");'
            '                categoriesSelect.dispatchEvent(event);'
            '            }}'
            '        }}'
           
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


# =============================
# 酒吧後台
# =============================

class BarBusinessHoursInline(admin.TabularInline):
    model = BarBusinessHours
    extra = 7
    max_num = 7


@admin.register(Bar)
class BarAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'rating', 'price_level', 'get_stations')
    search_fields = ('name', 'address', 'google_place_id')
    list_filter = ('price_level', 'rating', 'nearby_stations')
    filter_horizontal = ('nearby_stations', 'categories')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [BarBusinessHoursInline]

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            ('Google Places 資訊', {
                'fields': ('google_place_id',)
            }),
            ('基本資訊', {
                'fields': ('name', 'address', 'phone', 'website', 'categories')
            }),
            ('位置資訊', {
                'fields': ('latitude', 'longitude', 'nearby_stations')
            }),
            ('評分資訊', {
                'fields': ('rating', 'price_level')
            }),
        ]
        if obj:
            fieldsets.append(
                ('時間戳記', {
                    'fields': ('created_at', 'updated_at'),
                    'classes': ('collapse',)
                })
            )
        return fieldsets

    def get_stations(self, obj):
        if obj and obj.pk:
            return ", ".join([station.name for station in obj.nearby_stations.all()])
        return "-"
    get_stations.short_description = '鄰近捷運站'


@admin.register(BarCategory)
class BarCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(BarReview)
class BarReviewAdmin(admin.ModelAdmin):
    list_display = ('bar', 'reviewer_name', 'rating', 'created_at')
    search_fields = ('bar__name', 'reviewer_name', 'comment')
    list_filter = ('rating', 'created_at', 'bar')


@admin.register(YouBikeStation)
class YouBikeStationAdmin(admin.ModelAdmin):
    list_display = ('name', 'station_id', 'available_bikes', 'available_spaces', 'total_spaces', 'last_update')
    list_filter = ('last_update',)
    search_fields = ('name', 'station_id', 'address')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('nearby_stations',)




@admin.register(YouBikeHistory)
class YouBikeHistoryAdmin(admin.ModelAdmin):
    list_display = ('station', 'available_bikes', 'available_spaces', 'timestamp', 'weather', 'temperature')
    list_filter = ('day_of_week', 'hour', 'is_holiday', 'weather')
    search_fields = ('station__name', 'station__station_id')
    readonly_fields = ('timestamp',)



@admin.register(CheckinReview)
class CheckinReviewAdmin(admin.ModelAdmin):
    list_display = ('restaurant_name', 'metro_line', 'reviewer_name', 'rating', 'created_at')
    list_filter = ('rating', 'created_at', 'metro_line')
    search_fields = ('restaurant_name', 'reviewer_name', 'comment')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CheckinReviewLike)
class CheckinReviewLikeAdmin(admin.ModelAdmin):
    list_display = ('review', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('review__restaurant_name', 'user__username')
    ordering = ('-created_at',)


@admin.register(CheckinReviewFavorite)
class CheckinReviewFavoriteAdmin(admin.ModelAdmin):
    list_display = ('review', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('review__restaurant_name', 'user__username')
    ordering = ('-created_at',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sender', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'sender__username', 'title', 'content')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')



# 保留現有的其他模型註冊
admin.site.register(TrainInfo)



@admin.register(MetroLastFiveTrains)
class MetroLastFiveTrainsAdmin(admin.ModelAdmin):
    list_display = ('station_name', 'line_no', 'trip_head_sign', 'train_type', 'train_time', 'train_sequence')
    list_filter = ('line_no', 'trip_head_sign', 'train_type', 'train_sequence')
    search_fields = ('station_name', 'station_id')
    ordering = ('line_no', 'station_id', 'train_sequence')
