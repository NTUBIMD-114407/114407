from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    UserSerializer, BusinessSerializer, ReviewSerializer,
    MetroLineSerializer, MetroStationSerializer
)
from .models import Business, Review, MetroLine, MetroStation
from django.db.models import F, ExpressionWrapper, FloatField
from django.db.models.functions import Power, Sqrt
import requests
import os
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import json
from dotenv import load_dotenv
from pathlib import Path
import traceback
import base64
import hashlib
import hmac

# 載入環境變數
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)

User = get_user_model()

# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': '註冊成功',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({
            'message': '找不到此使用者'
        }, status=status.HTTP_404_NOT_FOUND)

    if not user.check_password(password):
        return Response({
            'message': '密碼錯誤'
        }, status=status.HTTP_400_BAD_REQUEST)

    refresh = RefreshToken.for_user(user)
    return Response({
        'message': '登入成功',
        'token': str(refresh.access_token)
    })

class MetroLineViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MetroLine.objects.all()
    serializer_class = MetroLineSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def stations(self, request, pk=None):
        line = self.get_object()
        stations = line.stations.all()
        serializer = MetroStationSerializer(stations, many=True)
        return Response(serializer.data)

class MetroStationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MetroStation.objects.all()
    serializer_class = MetroStationSerializer
    permission_classes = [IsAuthenticated]
    
    # 用於儲存所有車站的即時資料
    _metro_data_cache = {}
    _last_update_time = None
    
    def _fetch_metro_api_data(self):
        """從台北捷運 API 獲取所有車站的即時資料"""
        try:
            username = os.getenv('METRO_API_USERNAME')
            password = os.getenv('METRO_API_PASSWORD')
            
            if not username or not password:
                print("錯誤：未設定 METRO_API 認證資訊")
                print(f"Username: {'已設定' if username else '未設定'}")
                print(f"Password: {'已設定' if password else '未設定'}")
                return None
            
            url = "https://api.metro.taipei/metroapi/TrackInfo.asmx"
            
            soap_request = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <getTrackInfo xmlns="http://tempuri.org/">
            <userName>{username}</userName>
            <passWord>{password}</passWord>
        </getTrackInfo>
    </soap:Body>
</soap:Envelope>"""
            
            headers = {
                'Content-Type': 'text/xml; charset=utf-8',
                'Connection': 'keep-alive'
            }
            
            print(f"正在發送請求至 {url}")
            print("請求標頭：", headers)
            
            response = requests.post(url, data=soap_request, headers=headers)
            print(f"API 回應狀態碼：{response.status_code}")
            print(f"API 回應標頭：{dict(response.headers)}")
            
            if response.status_code != 200:
                print(f"API 請求失敗：{response.status_code}")
                print(f"回應內容：{response.text[:500]}...")
                return None
            
            try:
                content = response.content.decode('utf-8').strip()
                print(f"收到回應，長度：{len(content)} 字元")
                print(f"回應內容前500字元：{content[:500]}")
                
                # 嘗試找到第一個完整的 JSON 陣列
                start_idx = content.find('[')
                if start_idx == -1:
                    print("錯誤：找不到 JSON 陣列起始位置")
                    print("回應內容不包含 JSON 陣列")
                    return None
                
                end_idx = content.find(']', start_idx)
                if end_idx == -1:
                    print("錯誤：找不到 JSON 陣列結束位置")
                    print("回應內容不完整")
                    return None
                
                # 提取完整的 JSON 陣列
                json_content = content[start_idx:end_idx + 1]
                print(f"提取的 JSON 內容長度：{len(json_content)}")
                print(f"JSON 內容前500字元：{json_content[:500]}")
                
                try:
                    data = json.loads(json_content)
                    print(f"成功解析 JSON 資料，共 {len(data)} 筆記錄")
                    print("資料範例：", json.dumps(data[0] if data else {}, ensure_ascii=False, indent=2))
                    return data
                except json.JSONDecodeError as e:
                    print(f"JSON 解析錯誤：{str(e)}")
                    print(f"JSON 內容片段：{json_content[:500]}...")
                    return None
                    
            except Exception as e:
                print(f"處理回應內容時發生錯誤：{str(e)}")
                print(f"回應內容片段：{content[:500]}...")
                return None
            
        except requests.exceptions.RequestException as e:
            print(f"網路請求錯誤：{str(e)}")
            print(f"完整錯誤訊息：{traceback.format_exc()}")
            return None
        except Exception as e:
            print(f"未預期的錯誤：{str(e)}")
            print(traceback.format_exc())
            return None
    
    def _process_metro_data(self, raw_data):
        """處理並組織捷運站資料"""
        if not raw_data:
            print("沒有原始資料可處理")
            return {}
            
        try:
            print("\n開始處理捷運站資料...")
            print(f"原始資料筆數：{len(raw_data)}")
            
            stations_data = {}
            processed_count = 0
            error_count = 0
            
            # 檢查資料結構
            required_fields = ['StationName', 'DestinationName']
            for field in required_fields:
                if not any(field in train for train in raw_data):
                    print(f"警告：資料缺少必要欄位 {field}")
            
            for train in raw_data:
                try:
                    station_name = train.get('StationName', '').strip()
                    if not station_name:
                        print(f"警告：遇到無站名資料：{json.dumps(train, ensure_ascii=False)}")
                        error_count += 1
                        continue
                        
                    if station_name not in stations_data:
                        stations_data[station_name] = {
                            'station_name': station_name,
                            'destinations': {},
                            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        print(f"新增車站：{station_name}")
                    
                    destination = train.get('DestinationName', '').strip()
                    if not destination:
                        print(f"警告：{station_name} 站點缺少目的地資訊")
                        error_count += 1
                        continue
                        
                    if destination not in stations_data[station_name]['destinations']:
                        stations_data[station_name]['destinations'][destination] = []
                        print(f"新增目的地：{station_name} -> {destination}")
                    
                    train_info = {
                        'train_number': train.get('TrainNumber', ''),
                        'countdown': train.get('CountDown', ''),
                        'update_time': train.get('NowDateTime', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    }
                    
                    stations_data[station_name]['destinations'][destination].append(train_info)
                    processed_count += 1
                    
                except KeyError as e:
                    print(f"處理單筆列車資料時發生錯誤：{str(e)}")
                    print(f"問題資料：{json.dumps(train, ensure_ascii=False)}")
                    error_count += 1
                    continue
            
            print(f"\n處理完成：")
            print(f"- 成功處理：{processed_count} 筆")
            print(f"- 錯誤筆數：{error_count} 筆")
            print(f"- 總車站數：{len(stations_data)} 站")
            
            # 對每個方向的列車進行排序
            for station_data in stations_data.values():
                for destination in station_data['destinations'].values():
                    destination.sort(key=lambda x: '0' if x['countdown'] == '列車進站' else x['countdown'])
            
            # 顯示處理後的資料結構
            print("\n處理後的資料結構：")
            target_stations = ['士林站', '善導寺站']
            for station_name in target_stations:
                if station_name in stations_data:
                    print(f"\n{station_name}的即時資料：")
                    print(json.dumps(stations_data[station_name], ensure_ascii=False, indent=2))
                else:
                    print(f"\n找不到 {station_name} 的資料")
                    print(f"目前可用的車站：{', '.join(stations_data.keys())}")
            
            return stations_data
            
        except Exception as e:
            print(f"處理捷運資料時發生錯誤：{str(e)}")
            print(f"完整錯誤訊息：")
            print(traceback.format_exc())
            return {}
    
    def _update_cache_if_needed(self):
        """如果緩存過期，更新緩存資料"""
        current_time = datetime.now()
        
        # 如果是第一次獲取資料，或者距離上次更新超過30秒
        if (self._last_update_time is None or 
            (current_time - self._last_update_time).total_seconds() > 30):
            
            raw_data = self._fetch_metro_api_data()
            if raw_data:
                self._metro_data_cache = self._process_metro_data(raw_data)
                self._last_update_time = current_time
    
    def get_track_info(self, request, station_id):
        """獲取特定車站的即時資料"""
        try:
            station = MetroStation.objects.get(id=station_id)
            print(f"\n正在獲取車站資料：")
            print(f"- ID: {station_id}")
            print(f"- 名稱: {station.name}")
            print(f"- 代碼: {station.code}")
            
            # 更新緩存（如果需要）
            self._update_cache_if_needed()
            
            # 如果緩存中沒有資料，返回錯誤
            if not self._metro_data_cache:
                print("錯誤：緩存中沒有資料")
                return Response({
                    'success': False,
                    'message': '無法獲取捷運資料',
                    'data': None
                })
            
            # 嘗試不同的站名格式
            station_variants = [
                station.name,
                station.name.replace('站', ''),
                f"{station.name}站"
            ]
            
            print(f"嘗試的站名格式：{station_variants}")
            
            # 從緩存中獲取該站資料
            station_data = None
            matched_name = None
            
            for variant in station_variants:
                if variant in self._metro_data_cache:
                    station_data = self._metro_data_cache[variant]
                    matched_name = variant
                    break
            
            if not station_data:
                print(f"錯誤：找不到車站資料")
                print(f"可用的車站：{', '.join(self._metro_data_cache.keys())}")
                return Response({
                    'success': False,
                    'message': '找不到該站的即時資料',
                    'data': None
                })
            
            print(f"找到車站資料：{matched_name}")
            print(f"資料內容：{json.dumps(station_data, ensure_ascii=False, indent=2)}")
            
            return Response({
                'success': True,
                'data': station_data
            })
            
        except MetroStation.DoesNotExist:
            print(f"錯誤：找不到ID為 {station_id} 的車站")
            return Response({
                'success': False,
                'message': '找不到指定的捷運站'
            })
        except Exception as e:
            print(f"處理車站資料時發生錯誤：{str(e)}")
            print(traceback.format_exc())
            return Response({
                'success': False,
                'message': f'發生錯誤: {str(e)}'
            })

    def parse_arrival_time(self, track_info, station_code):
        """解析特定車站的到站時間資訊"""
        try:
            print("\n=== 開始解析到站時間 ===")
            print(f"車站代碼: {station_code}")
            print(f"列車資訊: {json.dumps(track_info, ensure_ascii=False, indent=2)}")
            
            # 用於存儲不同方向的列車資訊
            trains_by_direction = {}
            
            # 尋找符合車站代碼的列車資訊
            for train in track_info:
                if train['StationID'] == station_code:
                    # 取得目的地站名
                    destination = train.get('DestinationStationName', '')
                    # 取得到站時間
                    countdown = train.get('TimeToArrival', '')
                    estimate_time = train.get('EstimateTime', 0)
                    
                    # 轉換到站時間格式
                    arrival_status = countdown
                    if estimate_time == 0:
                        arrival_status = "進站中"
                    elif estimate_time == 1:
                        arrival_status = "即將進站"
                    else:
                        arrival_status = f"{estimate_time} 分鐘"
                    
                    # 整理列車資訊
                    train_info = {
                        'train_id': train.get('TrainID', ''),  # 列車編號
                        'arrival_time': arrival_status,  # 到站時間
                        'estimate_time': estimate_time,  # 預估時間（分鐘）
                        'destination': destination,  # 終點站
                        'timestamp': train.get('UpdateTime', '')  # 時間戳記
                    }
                    
                    # 依方向分組
                    if destination not in trains_by_direction:
                        trains_by_direction[destination] = []
                    trains_by_direction[destination].append(train_info)
            
            print("\n=== 分組後的列車資訊 ===")
            print(json.dumps(trains_by_direction, ensure_ascii=False, indent=2))
            
            # 整理最終回傳格式
            directions = []
            for destination, trains in trains_by_direction.items():
                # 對到站時間排序（根據預估時間）
                trains.sort(key=lambda x: x['estimate_time'])
                
                # 只保留前兩班列車
                trains = trains[:2]
                
                direction_info = {
                    'destination': destination,  # 終點站
                    'trains': trains,  # 列車資訊列表（限制為兩班）
                    'next_train': trains[0] if trains else None  # 下一班列車資訊
                }
                directions.append(direction_info)
            
            return {
                'directions': directions,  # 所有方向的列車資訊
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 資料更新時間
            }
            
        except Exception as e:
            print(f"解析到站時間時發生錯誤：{str(e)}")
            print(traceback.format_exc())
            return {
                'directions': [],
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'error': str(e)
            }

    @action(detail=True, methods=['get'])
    def arrival_time(self, request, pk=None):
        """獲取特定捷運站的到站時間"""
        try:
            station = self.get_object()
            track_info_response = self.get_track_info(request, pk)
            
            if not isinstance(track_info_response, Response):
                return Response({
                    'success': False,
                    'message': '無法獲取資料',
                    'data': None
                })
            
            return track_info_response
            
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': f'處理資料時發生錯誤: {str(e)}',
                    'data': None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """獲取附近捷運站"""
        try:
            user_lat = float(request.query_params.get('lat', 25.0338))
            user_lng = float(request.query_params.get('lng', 121.5646))
        except (TypeError, ValueError):
            return Response(
                {'error': '無效的位置資訊'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 計算與所有捷運站的距離
        stations = MetroStation.objects.annotate(
            distance=ExpressionWrapper(
                Sqrt(
                    Power(F('latitude') - user_lat, 2) +
                    Power(F('longitude') - user_lng, 2)
                ) * 111000,  # 轉換為公尺（大約值）
                output_field=FloatField()
            )
        ).order_by('distance')[:5]  # 只返回最近的5個站

        serializer = self.get_serializer(stations, many=True)
        data = serializer.data
        
        # 添加距離資訊
        for i, station in enumerate(stations):
            data[i]['distance'] = round(station.distance)

        return Response(data)

    @action(detail=True, methods=['get'])
    def nearby_businesses(self, request, pk=None):
        station = self.get_object()
        max_distance = int(request.query_params.get('max_distance', 500))  # 預設 500 公尺
        min_rating = float(request.query_params.get('min_rating', 0))
        
        # 計算距離並篩選商家
        businesses = Business.objects.filter(
            nearest_station=station,
            distance_to_station__lte=max_distance,
            rating__gte=min_rating
        ).order_by('distance_to_station', '-rating')
        
        serializer = BusinessSerializer(businesses, many=True)
        return Response(serializer.data)

class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated]

    def get_place_details(self, place_id):
        api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        url = f"https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            'place_id': place_id,
            'key': api_key,
            'fields': 'name,formatted_address,geometry,formatted_phone_number,website,rating,user_ratings_total,business_status,types,opening_hours,photos,reviews',
            'reviews_sort': 'newest'  # 獲取最新的評論
        }
        
        response = requests.get(url, params=params)
        return response.json()

    def find_nearest_station(self, latitude, longitude):
        # 使用 PostgreSQL 的地理距離計算（如果使用 PostgreSQL）
        # 或使用簡單的歐幾里得距離計算
        stations = MetroStation.objects.annotate(
            distance=ExpressionWrapper(
                Sqrt(
                    Power(F('latitude') - latitude, 2) +
                    Power(F('longitude') - longitude, 2)
                ) * 111000,  # 轉換為公尺（大約值）
                output_field=FloatField()
            )
        ).order_by('distance')

        nearest = stations.first()
        if nearest and nearest.distance <= 500:  # 限制在500公尺內
            return nearest, nearest.distance
        return None, None

    def create(self, request):
        place_id = request.data.get('place_id')
        if not place_id:
            return Response({'error': '需要提供 place_id'}, status=status.HTTP_400_BAD_REQUEST)

        # 檢查是否已存在
        existing_business = Business.objects.filter(google_place_id=place_id).first()
        if existing_business:
            # 如果資料超過24小時才更新
            if existing_business.last_updated < datetime.now() - timedelta(hours=24):
                place_details = self.get_place_details(place_id)
                if place_details.get('status') == 'OK':
                    result = place_details['result']
                    # 更新基本資訊
                    latitude = result['geometry']['location']['lat']
                    longitude = result['geometry']['location']['lng']
                    nearest_station, distance = self.find_nearest_station(latitude, longitude)

                    # 檢查是否在捷運站500公尺範圍內
                    if not nearest_station:
                        return Response(
                            {'error': '此商家不在任何捷運站500公尺範圍內'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    existing_business.name = result.get('name', '')
                    existing_business.address = result.get('formatted_address', '')
                    existing_business.latitude = latitude
                    existing_business.longitude = longitude
                    existing_business.phone = result.get('formatted_phone_number', '')
                    existing_business.website = result.get('website', '')
                    existing_business.rating = result.get('rating')
                    existing_business.rating_count = result.get('user_ratings_total', 0)
                    existing_business.business_status = result.get('business_status', '')
                    existing_business.types = result.get('types', [])
                    existing_business.opening_hours = result.get('opening_hours', {})
                    existing_business.nearest_station = nearest_station
                    existing_business.distance_to_station = distance
                    existing_business.save()

                    # 更新評論
                    if 'reviews' in result:
                        for review_data in result['reviews']:
                            Review.objects.update_or_create(
                                google_review_id=review_data.get('time') + '_' + review_data.get('author_name'),
                                defaults={
                                    'business': existing_business,
                                    'author_name': review_data.get('author_name', ''),
                                    'rating': review_data.get('rating', 3),
                                    'text': review_data.get('text', ''),
                                    'time': datetime.fromtimestamp(review_data.get('time')),
                                    'language': review_data.get('language', '')
                                }
                            )
            
            serializer = self.get_serializer(existing_business)
            return Response(serializer.data)

        # 獲取新的商家資訊
        place_details = self.get_place_details(place_id)
        if place_details.get('status') != 'OK':
            return Response({'error': '無法獲取商家資訊'}, status=status.HTTP_400_BAD_REQUEST)

        result = place_details['result']
        latitude = result['geometry']['location']['lat']
        longitude = result['geometry']['location']['lng']
        nearest_station, distance = self.find_nearest_station(latitude, longitude)

        # 檢查是否在捷運站500公尺範圍內
        if not nearest_station:
            return Response(
                {'error': '此商家不在任何捷運站500公尺範圍內'},
                status=status.HTTP_400_BAD_REQUEST
            )

        business_data = {
            'google_place_id': place_id,
            'name': result.get('name', ''),
            'address': result.get('formatted_address', ''),
            'latitude': latitude,
            'longitude': longitude,
            'phone': result.get('formatted_phone_number', ''),
            'website': result.get('website', ''),
            'rating': result.get('rating'),
            'rating_count': result.get('user_ratings_total', 0),
            'business_status': result.get('business_status', ''),
            'types': result.get('types', []),
            'opening_hours': result.get('opening_hours', {}),
            'nearest_station': nearest_station,
            'distance_to_station': distance
        }

        serializer = self.get_serializer(data=business_data)
        serializer.is_valid(raise_exception=True)
        business = serializer.save()

        # 儲存評論
        if 'reviews' in result:
            for review_data in result['reviews']:
                Review.objects.create(
                    business=business,
                    author_name=review_data.get('author_name', ''),
                    rating=review_data.get('rating', 3),
                    text=review_data.get('text', ''),
                    time=datetime.fromtimestamp(review_data.get('time')),
                    language=review_data.get('language', ''),
                    google_review_id=review_data.get('time') + '_' + review_data.get('author_name')
                )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def fetch_all_reviews(self, request, pk=None):
        """獲取並儲存商家的所有評論"""
        try:
            business = self.get_object()
            
            # 獲取商家詳細資訊，包含評論
            place_details = self.get_place_details(business.google_place_id)
            
            if place_details.get('status') != 'OK':
                return Response({
                    'success': False,
                    'message': '無法獲取商家評論',
                    'error': place_details.get('error_message', '未知錯誤')
                }, status=status.HTTP_400_BAD_REQUEST)

            result = place_details['result']
            reviews_added = 0
            reviews_updated = 0

            # 處理評論
            if 'reviews' in result:
                for review_data in result['reviews']:
                    review_id = f"{review_data.get('time')}_{review_data.get('author_name')}"
                    review, created = Review.objects.update_or_create(
                        google_review_id=review_id,
                        business=business,
                        defaults={
                            'author_name': review_data.get('author_name', ''),
                            'rating': review_data.get('rating', 3),
                            'text': review_data.get('text', ''),
                            'time': datetime.fromtimestamp(review_data.get('time')),
                            'language': review_data.get('language', ''),
                            'profile_photo_url': review_data.get('profile_photo_url', ''),
                            'relative_time_description': review_data.get('relative_time_description', '')
                        }
                    )
                    if created:
                        reviews_added += 1
                    else:
                        reviews_updated += 1

            # 更新商家的評分資訊
            business.rating = result.get('rating')
            business.rating_count = result.get('user_ratings_total', 0)
            business.save()

            return Response({
                'success': True,
                'message': f'成功更新評論資料',
                'data': {
                    'total_reviews': len(result.get('reviews', [])),
                    'new_reviews': reviews_added,
                    'updated_reviews': reviews_updated,
                    'rating': business.rating,
                    'rating_count': business.rating_count
                }
            })

        except Exception as e:
            return Response({
                'success': False,
                'message': f'處理評論時發生錯誤: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
