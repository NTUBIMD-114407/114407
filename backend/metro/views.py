from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from .models import Station, Restaurant, MetroLine, TrainInfo, CheckinReview, Review, BusinessHours, StationID, MetroFirstLastTrain, MetroLastFiveTrains, Bar, BarReview
from .serializers import (
    StationSerializer,
    RestaurantSerializer,
    MetroLineSerializer,
    MetroFirstLastTrainSerializer,
    MetroLastFiveTrainsSerializer,
    ReviewSerializer,
    BarSerializer,
    BarReviewSerializer
)
import requests
from xml.etree import ElementTree
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import os
from django.db.models import Avg, Q, F
import json
from .services.review_service import create_review_from_frontend, create_checkin_review, get_checkin_reviews
from django.db import models
from datetime import time
from .services.metro_train_service import get_station_first_last_trains as get_station_first_last_trains_service
from rest_framework import serializers
from rest_framework.decorators import action


class MetroLineViewSet(viewsets.ModelViewSet):
    queryset = MetroLine.objects.all()
    serializer_class = MetroLineSerializer
    permission_classes = [AllowAny]


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = [AllowAny]


class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [AllowAny]


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]


class BarViewSet(viewsets.ModelViewSet):
    queryset = Bar.objects.all()
    serializer_class = BarSerializer
    permission_classes = [AllowAny]


class BarReviewViewSet(viewsets.ModelViewSet):
    queryset = BarReview.objects.all()
    serializer_class = BarReviewSerializer
    permission_classes = [AllowAny]


@api_view(['GET'])
@permission_classes([AllowAny])
def get_bars_by_station(request):
    station_id = request.GET.get('station_id')
    if not station_id:
        return Response({'error': '請提供站點ID'}, status=400)
    try:
        station = Station.objects.get(id=station_id)
        bars = Bar.objects.filter(nearby_stations=station)
        serializer = BarSerializer(bars, many=True)
        return Response(serializer.data)
    except Station.DoesNotExist:
        return Response({'error': '找不到指定的站點'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_bars_by_line(request):
    line_id = request.GET.get('line_id')
    if not line_id:
        return Response({'error': '請提供捷運線編號'}, status=400)
    try:
        line = MetroLine.objects.get(id=line_id)
        stations = Station.objects.filter(metro_line=line)
        bars = Bar.objects.filter(nearby_stations__in=stations).distinct()
        serializer = BarSerializer(bars, many=True)
        return Response(serializer.data)
    except MetroLine.DoesNotExist:
        return Response({'error': '找不到指定的捷運線'}, status=404)
    except Exception as e:
        return Response({'error': f'發生錯誤：{str(e)}'}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_bar_details(request, bar_id):
    bar = get_object_or_404(Bar, id=bar_id)
    serializer = BarSerializer(bar)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_bar_reviews(request, bar_id):
    bar = get_object_or_404(Bar, id=bar_id)
    reviews = bar.reviews.all().order_by('-created_at')
    serializer = BarReviewSerializer(reviews, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_bar_review(request, bar_id):
    required_fields = ['rating']
    for field in required_fields:
        if field not in request.data:
            return Response({'error': f'缺少必要欄位: {field}'}, status=400)
    bar = get_object_or_404(Bar, id=bar_id)
    review = BarReview.objects.create(
        bar=bar,
        reviewer_name=request.data.get('reviewer_name', '匿名'),
        rating=request.data['rating'],
        comment=request.data.get('comment', '')
    )
    return Response({'message': '評論創建成功', 'review_id': review.id}, status=201)


@api_view(['PUT'])
@permission_classes([AllowAny])
def update_bar_review(request, review_id):
    review = get_object_or_404(BarReview, id=review_id)
    rating = request.data.get('rating')
    reviewer_name = request.data.get('reviewer_name')
    comment = request.data.get('comment')
    if rating is not None:
        try:
            rating = int(rating)
        except Exception:
            return Response({'error': '評分必須是整數'}, status=400)
        if rating < 1 or rating > 5:
            return Response({'error': '評分必須是 1-5 的整數'}, status=400)
        review.rating = rating
    if reviewer_name is not None:
        review.reviewer_name = reviewer_name
    if comment is not None:
        review.comment = comment
    review.save()
    return Response({'message': '評論更新成功', 'review_id': review.id})


@api_view(['GET'])
@permission_classes([AllowAny])
def night_bars(request):
    from datetime import time as dt_time
    night_time = dt_time(22, 0)
    bars = Bar.objects.filter(
        business_hours__close_time__gt=night_time,
        business_hours__is_closed=False
    ).distinct()
    results = []
    for bar in bars:
        business_hours = bar.business_hours.all().order_by('day_of_week')
        nearby_stations = [station.name for station in bar.nearby_stations.all()]
        hours_info = []
        for bh in business_hours:
            if bh.is_closed:
                hours_info.append({'day': bh.get_day_of_week_display(), 'hours': '休息'})
            else:
                hours_info.append({'day': bh.get_day_of_week_display(), 'hours': f"{bh.open_time.strftime('%H:%M')} - {bh.close_time.strftime('%H:%M')}"})
        results.append({
            'name': bar.name,
            'stations': nearby_stations,
            'business_hours': hours_info,
            'rating': bar.rating,
            'address': bar.address
        })
    return Response({'count': len(results), 'results': results})


class MetroFirstLastTrainViewSet(viewsets.ModelViewSet):
    queryset = MetroFirstLastTrain.objects.all()
    serializer_class = MetroFirstLastTrainSerializer
    permission_classes = [AllowAny]


class MetroLastFiveTrainsViewSet(viewsets.ModelViewSet):
    queryset = MetroLastFiveTrains.objects.all()
    serializer_class = MetroLastFiveTrainsSerializer
    permission_classes = [AllowAny]


    @action(detail=False, methods=['get'])
    def by_station(self, request):
        station_id = request.query_params.get('station_id')
        if not station_id:
            return Response({'error': 'station_id is required'}, status=status.HTTP_400_BAD_REQUEST)
       
        trains = self.queryset.filter(station_id=station_id)
        serializer = self.get_serializer(trains, many=True)
        return Response(serializer.data)


    @action(detail=False, methods=['get'])
    def by_line(self, request):
        line_no = request.query_params.get('line_no')
        if not line_no:
            return Response({'error': 'line_no is required'}, status=status.HTTP_400_BAD_REQUEST)
       
        trains = self.queryset.filter(line_no=line_no)
        serializer = self.get_serializer(trains, many=True)
        return Response(serializer.data)


    @action(detail=False, methods=['get'])
    def by_station_and_direction(self, request):
        station_id = request.query_params.get('station_id')
        direction = request.query_params.get('direction')
       
        if not station_id or not direction:
            return Response(
                {'error': 'station_id and direction are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
       
        trains = self.queryset.filter(station_id=station_id, direction=direction)
        serializer = self.get_serializer(trains, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_track_info(request):
    """獲取台北捷運列車到站資訊"""
    try:
        # 設定 SOAP 請求標頭
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': 'http://tempuri.org/getTrackInfo',
            'Host': 'api.metro.taipei'
        }
       
        # 從環境變數獲取帳密
        username = os.getenv('METRO_API_USERNAME')
        password = os.getenv('METRO_API_PASSWORD')
       
        if not username or not password:
            return Response({
                'status': 'error',
                'message': '環境變數中缺少 API 帳號或密碼'
            }, status=status.HTTP_400_BAD_REQUEST)
       
        # 移除可能的空白字元
        username = username.strip()
        password = password.strip()
       
        # 建立 SOAP XML 請求
        soap_request = f'''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <getTrackInfo xmlns="http://tempuri.org/">
      <userName>{username}</userName>
      <passWord>{password}</passWord>
    </getTrackInfo>
  </soap:Body>
</soap:Envelope>'''


        # 發送請求
        response = requests.post(
            'https://api.metro.taipei/metroapi/TrackInfo.asmx',
            headers=headers,
            data=soap_request.encode('utf-8'),
            verify=True
        )


        # 檢查回應
        if response.status_code == 200:
            if "您的帳號或密碼錯誤" in response.text:
                return Response({
                    'status': 'error',
                    'message': '帳號或密碼錯誤'
                }, status=status.HTTP_401_UNAUTHORIZED)
           
            try:
                # 從回應中提取 JSON 部分
                response_text = response.text
                json_end = response_text.find('<?xml')
                if json_end != -1:
                    json_data = response_text[:json_end]
                else:
                    json_data = response_text
               
                # 解析 JSON 數據
                trains_data = json.loads(json_data)
               
                # 按照路線分組
                line_groups = {}
                for train in trains_data:
                    station_name = train.get('StationName', '')
                    if not station_name:
                        continue
                       
                    # 根據站名判斷路線
                    from .tasks import get_line_by_station
                    line_name = get_line_by_station(station_name)
                    if not line_name:
                        continue
                       
                    if line_name not in line_groups:
                        line_groups[line_name] = []
                       
                    line_groups[line_name].append({
                        'stationName': station_name,
                        'destinationName': train.get('DestinationName', ''),
                        'countDown': train.get('CountDown', ''),
                        'nowDateTime': train.get('NowDateTime', '')
                    })
               
                return Response({
                    'status': 'success',
                    'data': line_groups
                })
            except ValueError as e:
                return Response({
                    'status': 'error',
                    'message': f'JSON 解析錯誤: {str(e)}',
                    'response_text': response_text[:500]  # 只返回前500個字符
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                'status': 'error',
                'message': f'API 請求失敗: {response.status_code}',
                'response': response.text[:500]  # 只返回前500個字符
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_latest_train_info(request):
    """獲取最新的列車到站資訊"""
    from .tasks import fetch_train_info
   
    # 直接從 API 獲取最新資料
    trains_data = fetch_train_info()
   
    if not trains_data:
        return Response({
            'status': 'error',
            'message': '無法獲取列車資訊'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
    # 按照路線分組
    line_groups = {}
    for train in trains_data:
        station_name = train.get('StationName', '')
        if not station_name:
            continue
           
        # 根據站名判斷路線
        from .tasks import get_line_by_station
        line_name = get_line_by_station(station_name)
        if not line_name:
            continue
           
        if line_name not in line_groups:
            line_groups[line_name] = []
           
        line_groups[line_name].append({
            'stationName': station_name,
            'destinationName': train.get('DestinationName', ''),
            'countDown': train.get('CountDown', ''),
            'nowDateTime': train.get('NowDateTime', '')
        })
   
    return Response({
        'status': 'success',
        'data': line_groups
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_info(request):
    """獲取當前登入用戶的資訊"""
    if request.user.is_authenticated:
        return JsonResponse({
            'isAuthenticated': True,
            'user': {
                'username': request.user.username,
                'email': request.user.email,
                'id': request.user.id
            }
        })
    return JsonResponse({
        'isAuthenticated': False,
        'user': None
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_restaurant_reviews(request, restaurant_id):
    """獲取餐廳的評論"""
    try:
        # 獲取餐廳
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
       
        # 從資料庫獲取評論
        reviews = restaurant.reviews.all().order_by('-created_at')
       
        # 準備回應數據
        reviews_data = []
        for review in reviews:
            review_data = {
                'id': review.id,
                'reviewer_name': review.reviewer_name,
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': review.updated_at.strftime('%Y-%m-%d %H:%M:%S') if review.updated_at else None
            }
            reviews_data.append(review_data)
       
        # 計算平均評分
        total_reviews = reviews.count()
        average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] if total_reviews > 0 else 0
       
        return Response({
            'status': 'success',
            'data': {
                'restaurant_id': restaurant.id,
                'restaurant_name': restaurant.name,
                'total_reviews': total_reviews,
                'average_rating': round(average_rating, 1) if average_rating else 0,
                'reviews': reviews_data
            }
        })
       
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def create_restaurant_review(request, restaurant_id):
    """創建餐廳評論的 API 端點"""
    try:
        # 驗證必要欄位
        required_fields = ['rating']
        for field in required_fields:
            if field not in request.data:
                return Response(
                    {'error': f'缺少必要欄位: {field}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
       
        # 創建評論
        review = create_review_from_frontend(restaurant_id, request.data)
       
        if review is None:
            return Response(
                {'error': '創建評論失敗'},
                status=status.HTTP_400_BAD_REQUEST
            )
           
        return Response({
            'message': '評論創建成功',
            'review_id': review.id
        }, status=status.HTTP_201_CREATED)
       
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def create_checkin_review_api(request):
    """創建打卡評論的 API 端點"""
    try:
        # 驗證必要欄位
        required_fields = ['restaurant_name', 'metro_line', 'rating']
        for field in required_fields:
            if field not in request.data:
                return Response(
                    {'error': f'缺少必要欄位: {field}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
       
        # 創建評論
        review = CheckinReview.objects.create(
            restaurant_name=request.data['restaurant_name'],
            metro_line=request.data['metro_line'],
            reviewer_name=request.data.get('reviewer_name', '匿名'),
            rating=request.data['rating'],
            comment=request.data.get('comment', '')
        )
       
        return Response({
            'message': '評論創建成功',
            'review_id': review.id
        }, status=status.HTTP_201_CREATED)
       
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_checkin_reviews_api(request):
    """獲取打卡版評論列表的 API 端點"""
    try:
        restaurant_name = request.query_params.get('restaurant_name')
        limit = int(request.query_params.get('limit', 10))
       
        if not restaurant_name:
            return Response(
                {'error': '缺少必要參數: restaurant_name'},
                status=status.HTTP_400_BAD_REQUEST
            )
       
        reviews = CheckinReview.objects.filter(
            restaurant_name=restaurant_name
        ).order_by('-created_at')[:limit]
       
        reviews_data = [{
            'id': review.id,
            'restaurant_name': review.restaurant_name,
            'metro_line': review.metro_line,
            'reviewer_name': review.reviewer_name,
            'rating': review.rating,
            'comment': review.comment,
            'created_at': review.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for review in reviews]
       
        return Response({
            'reviews': reviews_data
        }, status=status.HTTP_200_OK)
       
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_top_checkin_restaurants(request):
    """獲取打卡評論數量前 700 名的餐廳"""
    try:
        from django.db.models import Count
        # 獲取打卡評論數量前 700 名的餐廳名稱
        top_restaurants = CheckinReview.objects.values('restaurant_name').annotate(
            review_count=Count('id')
        ).order_by('-review_count')[:700]
       
        # 獲取每個餐廳的詳細資訊
        restaurants_data = []
        for restaurant in top_restaurants:
            # 查找餐廳的詳細資訊
            restaurant_info = Restaurant.objects.filter(name=restaurant['restaurant_name']).first()
            if restaurant_info:
                restaurants_data.append({
                    'restaurant_name': restaurant['restaurant_name'],
                    'review_count': restaurant['review_count'],
                    'address': restaurant_info.address,
                    'phone': restaurant_info.phone,
                    'rating': restaurant_info.rating,
                    'price_level': restaurant_info.price_level,
                    'website': restaurant_info.website
                })
            else:
                # 如果找不到餐廳資訊，只返回基本資訊
                restaurants_data.append({
                    'restaurant_name': restaurant['restaurant_name'],
                    'review_count': restaurant['review_count']
                })
       
        return Response({
            'restaurants': restaurants_data
        }, status=status.HTTP_200_OK)
       
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
def update_checkin_review_api(request, review_id):
    """更新打卡版評論的 API 端點"""
    try:
        # 獲取評論
        review = get_object_or_404(CheckinReview, id=review_id)
       
        # 獲取前端傳來的數據
        rating = request.data.get('rating')
        reviewer_name = request.data.get('reviewer_name')
        comment = request.data.get('comment')
        restaurant_name = request.data.get('restaurant_name')
        metro_line = request.data.get('metro_line')


        # 驗證評分
        if rating is not None:
            if not isinstance(rating, int) or rating < 1 or rating > 5:
                return Response(
                    {"error": "評分必須是 1-5 的整數"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            review.rating = rating


        # 更新其他欄位
        if reviewer_name is not None:
            review.reviewer_name = reviewer_name
        if comment is not None:
            review.comment = comment
        if restaurant_name is not None:
            review.restaurant_name = restaurant_name
        if metro_line is not None:
            review.metro_line = metro_line


        # 保存更新
        review.save()


        return Response({
            'message': '打卡評論更新成功',
            'review_id': review.id
        }, status=status.HTTP_200_OK)
       
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
def update_restaurant_review(request, review_id):
    """更新餐廳評論的 API 端點"""
    try:
        # 獲取評論
        review = get_object_or_404(Review, id=review_id)
       
        # 獲取前端傳來的數據
        rating = request.data.get('rating')
        reviewer_name = request.data.get('reviewer_name')
        comment = request.data.get('comment')


        # 驗證評分
        if rating is not None:
            if not isinstance(rating, int) or rating < 1 or rating > 5:
                return Response(
                    {"error": "評分必須是 1-5 的整數"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            review.rating = rating


        # 更新其他欄位
        if reviewer_name is not None:
            review.reviewer_name = reviewer_name
        if comment is not None:
            review.comment = comment


        # 保存更新
        review.save()


        # 更新餐廳的評分
        reviews = Review.objects.filter(restaurant=review.restaurant)
        review.restaurant.total_ratings = reviews.count()
        review.restaurant.rating = reviews.aggregate(
            avg_rating=models.Avg('rating')
        )['avg_rating'] or 0
        review.restaurant.save()


        return Response({
            'message': '評論更新成功',
            'review_id': review.id
        }, status=status.HTTP_200_OK)
       
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_metro_line_restaurants(request):
    """獲取所有捷運線的餐廳"""
    try:
        # 獲取所有捷運線
        metro_lines = MetroLine.objects.all()
       
        # 準備返回的數據結構
        result = []
       
        for line in metro_lines:
            # 獲取該捷運線的所有站點
            stations = Station.objects.filter(metro_line=line)
           
            # 獲取這些站點附近的所有餐廳
            restaurants = Restaurant.objects.filter(nearby_stations__in=stations).distinct()
           
            # 序列化餐廳數據
            serializer = RestaurantSerializer(restaurants, many=True)
           
            # 添加到結果中
            result.append({
                'metro_line': {
                    'id': line.id,
                    'name': line.name,
                    'color': line.color
                },
                'restaurants': serializer.data
            })
       
        return Response({
            'status': 'success',
            'data': result
        })
       
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_restaurants(request):
    """獲取所有餐廳"""
    try:
        # 獲取所有餐廳
        restaurants = Restaurant.objects.all()
       
        # 序列化餐廳數據
        serializer = RestaurantSerializer(restaurants, many=True)
       
        return Response({
            'status': 'success',
            'data': serializer.data
        })
       
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_restaurants(request):
    """根據餐廳名稱搜索餐廳"""
    name = request.GET.get('name', '')
    if not name:
        return Response({
            'status': 'error',
            'message': '請提供餐廳名稱'
        }, status=status.HTTP_400_BAD_REQUEST)
   
    restaurants = Restaurant.objects.filter(name__icontains=name)
   
    # 準備回應數據
    restaurants_data = []
    for restaurant in restaurants:
        # 獲取餐廳的捷運站信息
        station = restaurant.nearby_stations.first()
       
        restaurant_data = {
            'id': restaurant.id,
            'name': restaurant.name,
            'address': restaurant.address,
            'phone': restaurant.phone,
            'rating': restaurant.rating,
            'station_id': station.id if station else None,
            'station_name': station.name if station else None,
            'metro_line_id': station.metro_line.id if station else None,
            'metro_line_name': station.metro_line.name if station else None,
            'metro_line_color': station.metro_line.color if station else None,
            'created_at': restaurant.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': restaurant.updated_at.strftime('%Y-%m-%d %H:%M:%S') if restaurant.updated_at else None
        }
        restaurants_data.append(restaurant_data)
   
    return Response({
        'status': 'success',
        'data': restaurants_data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_reviews(request):
    """獲取所有評論"""
    try:
        # 獲取所有評論
        reviews = Review.objects.all().order_by('-created_at')
       
        # 準備回應數據
        reviews_data = []
        for review in reviews:
            # 獲取餐廳的捷運站信息
            station = review.restaurant.nearby_stations.first()
            station_name = station.name if station else None
           
            review_data = {
                'id': review.id,
                'restaurant_id': review.restaurant.id,
                'restaurant_name': review.restaurant.name,
                'station_name': station_name,
                'reviewer_name': review.reviewer_name,
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': review.updated_at.strftime('%Y-%m-%d %H:%M:%S') if review.updated_at else None
            }
            reviews_data.append(review_data)
       
        return Response({
            'status': 'success',
            'data': reviews_data
        })
       
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def night_restaurants(request):
    """獲取夜間營業的餐廳（晚上10點後仍在營業）"""
    # 設定晚上10點的時間
    night_time = time(22, 0)  # 22:00
   
    # 查找任一天營業時間超過晚上10點的餐廳
    night_restaurants = Restaurant.objects.filter(
        business_hours__close_time__gt=night_time,  # 關店時間超過晚上10點
        business_hours__is_closed=False  # 不是休息日
    ).distinct()  # 使用distinct避免重複結果
   
    results = []
    for restaurant in night_restaurants:
        # 獲取該餐廳的所有營業時間（包括所有時段）
        business_hours = restaurant.business_hours.all().order_by('day_of_week')
       
        # 獲取鄰近捷運站名稱
        nearby_stations = [station.name for station in restaurant.nearby_stations.all()]
       
        # 格式化營業時間
        hours_info = []
        for bh in business_hours:
            if bh.is_closed:
                hours_info.append({
                    'day': bh.get_day_of_week_display(),
                    'hours': '休息'
                })
            else:
                hours_info.append({
                    'day': bh.get_day_of_week_display(),
                    'hours': f"{bh.open_time.strftime('%H:%M')} - {bh.close_time.strftime('%H:%M')}"
                })
       
        results.append({
            'name': restaurant.name,
            'stations': nearby_stations,
            'business_hours': hours_info,
            'rating': restaurant.rating,
            'address': restaurant.address
        })
   
    return Response({
        'count': len(results),
        'results': results
    })


@api_view(['POST'])
def get_metro_route(request):
    import os
    import json
    start_name = request.data.get('start')
    end_name = request.data.get('end')
    if not start_name or not end_name:
        return Response({'error': '請提供起點和終點車站名'}, status=400)


    try:
        entry_station = StationID.objects.get(station_name=start_name)
        exit_station = StationID.objects.get(station_name=end_name)
    except StationID.DoesNotExist:
        return Response({'error': '查無車站名稱'}, status=404)


    # 從環境變數獲取帳密
    username = os.getenv('METRO_API_USERNAME')
    password = os.getenv('METRO_API_PASSWORD')
    if not username or not password:
        return Response({'error': '未設置捷運API帳號或密碼'}, status=500)
    username = username.strip()
    password = password.strip()


    # SOAP 請求內容
    soap_body = f'''<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                   xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                   xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
      <soap:Body>
        <GetRecommandRoute xmlns="http://tempuri.org/">
          <entrySid>{entry_station.station_id}</entrySid>
          <exitSid>{exit_station.station_id}</exitSid>
          <username>{username}</username>
          <password>{password}</password>
        </GetRecommandRoute>
      </soap:Body>
    </soap:Envelope>'''


    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': 'http://tempuri.org/GetRecommandRoute'
    }


    try:
        response = requests.post(
            'https://ws.metro.taipei/trtcBeaconBE/RouteControl.asmx',
            data=soap_body.encode('utf-8'),
            headers=headers
        )
        if response.status_code == 200:
            # 先找出 JSON 部分
            response_text = response.text
            json_end = response_text.find('<?xml')
            if json_end != -1:
                json_data = response_text[:json_end]
            else:
                json_data = response_text
            try:
                data = json.loads(json_data)
                return Response(data)
            except Exception as e:
                return Response({'error': f'JSON 解析錯誤: {str(e)}', 'raw': response_text}, status=500)
        else:
            return Response({'error': '捷運API請求失敗', 'status_code': response.status_code, 'response': response.text}, status=500)
    except requests.exceptions.RequestException as e:
        return Response({'error': f'網路請求錯誤: {str(e)}'}, status=500)
    except Exception as e:
        return Response({'error': f'發生未預期的錯誤: {str(e)}', 'raw': response.text if 'response' in locals() else ''}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_station_first_last_trains(request, station_id):
    trains = get_station_first_last_trains_service(station_id)
    if trains is None:
        return Response({'error': '獲取首末班車資訊失敗'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    serializer = MetroFirstLastTrainSerializer(trains, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_station_by_name_first_last_trains(request, station_name):
    """根據站名查詢所有線路的首末班車資訊"""
    station_ids = StationID.objects.filter(station_name=station_name)
    if not station_ids.exists():
        return Response({'error': f'查無站名: {station_name}'}, status=status.HTTP_404_NOT_FOUND)
    result = []
    for sid in station_ids:
        trains = MetroFirstLastTrain.objects.filter(station_id=sid.station_id)
        serializer = MetroFirstLastTrainSerializer(trains, many=True)
        result.append({
            'station_id': sid.station_id,
            'line_name': sid.line_name,
            'first_last_trains': serializer.data
        })
    return Response({station_name: result})


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_metro_lines(request):
    """獲取所有捷運線"""
    lines = MetroLine.objects.all()
    serializer = MetroLineSerializer(lines, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_stations_by_line(request, line_id):
    """獲取指定捷運線的所有站點"""
    line = get_object_or_404(MetroLine, id=line_id)
    stations = Station.objects.filter(metro_line=line)
    serializer = StationSerializer(stations, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_nearby_restaurants(request, station_id):
    """獲取指定捷運站附近的餐廳"""
    station = get_object_or_404(Station, id=station_id)
    restaurants = station.nearby_restaurants.all()
    serializer = RestaurantSerializer(restaurants, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_restaurant_details(request, restaurant_id):
    """獲取單一餐廳的詳細資訊"""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    serializer = RestaurantSerializer(restaurant)
    return Response(serializer.data)


@api_view(['GET'])
def get_station_last_five_trains(request):
    """
    根據站點名稱查詢末五班車資訊
    參數：
    - station_name: 站點名稱
    返回：
    - 該站點所有方向的末五班車資訊
    """
    station_name = request.GET.get('station_name')
    if not station_name:
        return Response({'error': '請提供站點名稱'}, status=400)


    # 查詢該站點的所有末五班車資訊
    trains = MetroLastFiveTrains.objects.filter(
        station_name=station_name
    ).order_by('line_no', 'trip_head_sign', 'train_sequence')


    if not trains.exists():
        return Response({'error': f'找不到站點 {station_name} 的末五班車資訊'}, status=404)


    # 整理資料
    result = {}
    for train in trains:
        key = f"{train.line_no}_{train.trip_head_sign}"
        if key not in result:
            result[key] = {
                'line_no': train.line_no,
                'station_name': train.station_name,
                'direction': train.trip_head_sign,
                'destination': train.destination_station_name,
                'trains': []
            }
       
        result[key]['trains'].append({
            'train_time': train.train_time.strftime('%H:%M'),
            'train_sequence': train.train_sequence,
            'train_type': train.train_type
        })


    return Response(list(result.values()))


@api_view(['GET'])
@permission_classes([AllowAny])
def get_restaurants_by_station(request):
    """根據站點查詢附近的餐廳"""
    station_id = request.GET.get('station_id')
    if not station_id:
        return Response({'error': '請提供站點ID'}, status=400)


    try:
        station = Station.objects.get(id=station_id)
        restaurants = Restaurant.objects.filter(nearby_stations=station)
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data)
    except Station.DoesNotExist:
        return Response({'error': '找不到指定的站點'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_restaurants_by_line(request):
    """根據捷運線查詢沿線的餐廳"""
    line_id = request.GET.get('line_id')
    if not line_id:
        return Response({'error': '請提供捷運線編號'}, status=400)


    try:
        # 獲取指定捷運線的所有站點
        line = MetroLine.objects.get(id=line_id)
        stations = Station.objects.filter(metro_line=line)
       
        # 獲取這些站點附近的所有餐廳
        restaurants = Restaurant.objects.filter(nearby_stations__in=stations).distinct()
       
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data)
    except MetroLine.DoesNotExist:
        return Response({'error': '找不到指定的捷運線'}, status=404)
    except Exception as e:
        return Response({'error': f'發生錯誤：{str(e)}'}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_restaurants_by_station_and_line(request):
    """根據捷運站和捷運線查詢附近的餐廳"""
    station_id = request.GET.get('station_id')
    line_id = request.GET.get('line_id')
   
    if not station_id or not line_id:
        return Response({'error': '請提供捷運站編號和捷運線編號'}, status=400)


    try:
        # 獲取指定捷運站和捷運線
        station = Station.objects.get(id=station_id, metro_line_id=line_id)
       
        # 獲取該站點附近的所有餐廳
        restaurants = Restaurant.objects.filter(nearby_stations=station)
       
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data)
    except Station.DoesNotExist:
        return Response({'error': '找不到指定的捷運站或捷運線'}, status=404)
    except Exception as e:
        return Response({'error': f'發生錯誤：{str(e)}'}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_restaurants_by_station_and_category(request):
    """根據捷運站和餐廳類別查詢附近的餐廳"""
    station_id = request.GET.get('station_id')
    category = request.GET.get('category')
   
    if not station_id or not category:
        return Response({'error': '請提供捷運站編號和餐廳類別'}, status=400)


    try:
        # 獲取指定捷運站
        station = Station.objects.get(id=station_id)
       
        # 獲取該站點附近且符合類別的所有餐廳
        restaurants = Restaurant.objects.filter(
            nearby_stations=station,
            category=category
        )
       
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data)
    except Station.DoesNotExist:
        return Response({'error': '找不到指定的捷運站'}, status=404)
    except Exception as e:
        return Response({'error': f'發生錯誤：{str(e)}'}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_restaurants_by_line_and_category(request):
    """根據捷運線和餐廳類別查詢沿線的餐廳"""
    line_id = request.GET.get('line_id')
    category = request.GET.get('category')
   
    if not line_id or not category:
        return Response({'error': '請提供捷運線編號和餐廳類別'}, status=400)


    try:
        # 獲取指定捷運線的所有站點
        line = MetroLine.objects.get(id=line_id)
        stations = Station.objects.filter(metro_line=line)
       
        # 獲取這些站點附近且符合類別的所有餐廳
        restaurants = Restaurant.objects.filter(
            nearby_stations__in=stations,
            category=category
        ).distinct()
       
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data)
    except MetroLine.DoesNotExist:
        return Response({'error': '找不到指定的捷運線'}, status=404)
    except Exception as e:
        return Response({'error': f'發生錯誤：{str(e)}'}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_restaurants_by_station_line_and_category(request):
    """根據捷運站、捷運線和餐廳類別查詢附近的餐廳"""
    station_id = request.GET.get('station_id')
    line_id = request.GET.get('line_id')
    category = request.GET.get('category')
   
    if not station_id or not line_id or not category:
        return Response({'error': '請提供捷運站編號、捷運線編號和餐廳類別'}, status=400)


    try:
        # 獲取指定捷運站和捷運線
        station = Station.objects.get(id=station_id, metro_line_id=line_id)
       
        # 獲取該站點附近且符合類別的所有餐廳
        restaurants = Restaurant.objects.filter(
            nearby_stations=station,
            category=category
        )
       
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data)
    except Station.DoesNotExist:
        return Response({'error': '找不到指定的捷運站或捷運線'}, status=404)
    except Exception as e:
        return Response({'error': f'發生錯誤：{str(e)}'}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_restaurants_by_station_and_price(request):
    """根據捷運站和價格範圍查詢附近的餐廳"""
    station_id = request.GET.get('station_id')
    price_level = request.GET.get('price_level')
   
    if not station_id or not price_level:
        return Response({'error': '請提供捷運站編號和價格範圍'}, status=400)


    try:
        # 獲取指定捷運站
        station = Station.objects.get(id=station_id)
       
        # 獲取該站點附近且符合價格範圍的所有餐廳
        restaurants = Restaurant.objects.filter(
            nearby_stations=station,
            price_level=price_level
        )
       
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data)
    except Station.DoesNotExist:
        return Response({'error': '找不到指定的捷運站'}, status=404)
    except Exception as e:
        return Response({'error': f'發生錯誤：{str(e)}'}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_restaurants_by_line_and_price(request):
    """根據捷運線和價格範圍查詢沿線的餐廳"""
    line_id = request.GET.get('line_id')
    price_level = request.GET.get('price_level')
   
    if not line_id or not price_level:
        return Response({'error': '請提供捷運線編號和價格範圍'}, status=400)


    try:
        # 獲取指定捷運線的所有站點
        line = MetroLine.objects.get(id=line_id)
        stations = Station.objects.filter(metro_line=line)
       
        # 獲取這些站點附近且符合價格範圍的所有餐廳
        restaurants = Restaurant.objects.filter(
            nearby_stations__in=stations,
            price_level=price_level
        ).distinct()
       
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data)
    except MetroLine.DoesNotExist:
        return Response({'error': '找不到指定的捷運線'}, status=404)
    except Exception as e:
        return Response({'error': f'發生錯誤：{str(e)}'}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_restaurants_by_station_line_and_price(request):
    """根據捷運站、捷運線和價格範圍查詢附近的餐廳"""
    station_id = request.GET.get('station_id')
    line_id = request.GET.get('line_id')
    price_level = request.GET.get('price_level')
   
    if not station_id or not line_id or not price_level:
        return Response({'error': '請提供捷運站編號、捷運線編號和價格範圍'}, status=400)


    try:
        # 獲取指定捷運站和捷運線
        station = Station.objects.get(id=station_id, metro_line_id=line_id)
       
        # 獲取該站點附近且符合價格範圍的所有餐廳
        restaurants = Restaurant.objects.filter(
            nearby_stations=station,
            price_level=price_level
        )
       
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data)
    except Station.DoesNotExist:
        return Response({'error': '找不到指定的捷運站或捷運線'}, status=404)
    except Exception as e:
        return Response({'error': f'發生錯誤：{str(e)}'}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_restaurants_by_station_and_rating(request):
    """根據捷運站和評分查詢附近的餐廳"""
    station_id = request.GET.get('station_id')
    min_rating = request.GET.get('min_rating')
   
    if not station_id or not min_rating:
        return Response({'error': '請提供捷運站編號和最低評分'}, status=400)


    try:
        # 獲取指定捷運站
        station = Station.objects.get(id=station_id)
       
        # 獲取該站點附近且評分不低於指定值的所有餐廳
        restaurants = Restaurant.objects.filter(
            nearby_stations=station,
            rating__gte=min_rating
        )
       
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data)
    except Station.DoesNotExist:
        return Response({'error': '找不到指定的捷運站'}, status=404)
    except Exception as e:
        return Response({'error': f'發生錯誤：{str(e)}'}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_restaurants_by_line_and_rating(request):
    """根據捷運線和評分查詢沿線的餐廳"""
    line_id = request.GET.get('line_id')
    min_rating = request.GET.get('min_rating')
   
    if not line_id or not min_rating:
        return Response({'error': '請提供捷運線編號和最低評分'}, status=400)


    try:
        # 獲取指定捷運線的所有站點
        line = MetroLine.objects.get(id=line_id)
        stations = Station.objects.filter(metro_line=line)
       
        # 獲取這些站點附近且評分不低於指定值的所有餐廳
        restaurants = Restaurant.objects.filter(
            nearby_stations__in=stations,
            rating__gte=min_rating
        ).distinct()
       
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data)
    except MetroLine.DoesNotExist:
        return Response({'error': '找不到指定的捷運線'}, status=404)
    except Exception as e:
        return Response({'error': f'發生錯誤：{str(e)}'}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_restaurants_by_station_line_and_rating(request):
    """根據捷運站、捷運線和評分查詢附近的餐廳"""
    station_id = request.GET.get('station_id')
    line_id = request.GET.get('line_id')
    min_rating = request.GET.get('min_rating')
   
    if not station_id or not line_id or not min_rating:
        return Response({'error': '請提供捷運站編號、捷運線編號和最低評分'}, status=400)


    try:
        # 獲取指定捷運站和捷運線
        station = Station.objects.get(id=station_id, metro_line_id=line_id)
       
        # 獲取該站點附近且評分不低於指定值的所有餐廳
        restaurants = Restaurant.objects.filter(
            nearby_stations=station,
            rating__gte=min_rating
        )
       
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data)
    except Station.DoesNotExist:
        return Response({'error': '找不到指定的捷運站或捷運線'}, status=404)
    except Exception as e:
        return Response({'error': f'發生錯誤：{str(e)}'}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_restaurants_by_station_and_hours(request):
    """根據捷運站和營業時間查詢附近的餐廳"""
    station_id = request.GET.get('station_id')
    day_of_week = request.GET.get('day_of_week')
    time_str = request.GET.get('time')
   
    if not station_id or not day_of_week or not time_str:
        return Response({'error': '請提供捷運站編號、星期和時間'}, status=400)


    try:
        # 解析時間字串
        hour, minute = map(int, time_str.split(':'))
        query_time = time(hour, minute)
       
        # 獲取指定捷運站
        station = Station.objects.get(id=station_id)
       
        # 獲取該站點附近且在指定時間營業的所有餐廳
        restaurants = Restaurant.objects.filter(
            nearby_stations=station,
            business_hours__day_of_week=day_of_week,
            business_hours__open_time__lte=query_time,
            business_hours__close_time__gt=query_time,
            business_hours__is_closed=False
        ).distinct()
       
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data)
    except Station.DoesNotExist:
        return Response({'error': '找不到指定的捷運站'}, status=404)
    except ValueError:
        return Response({'error': '時間格式錯誤，請使用 HH:MM 格式'}, status=400)
    except Exception as e:
        return Response({'error': f'發生錯誤：{str(e)}'}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_restaurants_by_line_and_hours(request):
    """根據捷運線和營業時間查詢沿線的餐廳"""
    line_id = request.GET.get('line_id')
    day_of_week = request.GET.get('day_of_week')
    time_str = request.GET.get('time')
   
    if not line_id or not day_of_week or not time_str:
        return Response({'error': '請提供捷運線編號、星期和時間'}, status=400)


    try:
        # 解析時間字串
        hour, minute = map(int, time_str.split(':'))
        query_time = time(hour, minute)
       
        # 獲取指定捷運線的所有站點
        line = MetroLine.objects.get(id=line_id)
        stations = Station.objects.filter(metro_line=line)
       
        # 獲取這些站點附近且在指定時間營業的所有餐廳
        restaurants = Restaurant.objects.filter(
            nearby_stations__in=stations,
            business_hours__day_of_week=day_of_week,
            business_hours__open_time__lte=query_time,
            business_hours__close_time__gt=query_time,
            business_hours__is_closed=False
        ).distinct()
       
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data)
    except MetroLine.DoesNotExist:
        return Response({'error': '找不到指定的捷運線'}, status=404)
    except ValueError:
        return Response({'error': '時間格式錯誤，請使用 HH:MM 格式'}, status=400)
    except Exception as e:
        return Response({'error': f'發生錯誤：{str(e)}'}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_restaurants_by_station_line_and_hours(request):
    """根據捷運站、捷運線和營業時間查詢附近的餐廳"""
    station_id = request.GET.get('station_id')
    line_id = request.GET.get('line_id')
    day_of_week = request.GET.get('day_of_week')
    time_str = request.GET.get('time')
   
    if not station_id or not line_id or not day_of_week or not time_str:
        return Response({'error': '請提供捷運站編號、捷運線編號、星期和時間'}, status=400)


    try:
        # 解析時間字串
        hour, minute = map(int, time_str.split(':'))
        query_time = time(hour, minute)
       
        # 獲取指定捷運站和捷運線
        station = Station.objects.get(id=station_id, metro_line_id=line_id)
       
        # 獲取該站點附近且在指定時間營業的所有餐廳
        restaurants = Restaurant.objects.filter(
            nearby_stations=station,
            business_hours__day_of_week=day_of_week,
            business_hours__open_time__lte=query_time,
            business_hours__close_time__gt=query_time,
            business_hours__is_closed=False
        ).distinct()
       
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data)
    except Station.DoesNotExist:
        return Response({'error': '找不到指定的捷運站或捷運線'}, status=404)
    except ValueError:
        return Response({'error': '時間格式錯誤，請使用 HH:MM 格式'}, status=400)
    except Exception as e:
        return Response({'error': f'發生錯誤：{str(e)}'}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_restaurants_by_station_and_category_and_price(request):
    """根據捷運站、餐廳類別和價格範圍查詢附近的餐廳"""
    station_id = request.GET.get('station_id')
    category = request.GET.get('category')
    price_level = request.GET.get('price_level')
   
    if not station_id or not category or not price_level:
        return Response({'error': '請提供捷運站編號、餐廳類別和價格範圍'}, status=400)


    try:
        # 獲取指定捷運站
        station = Station.objects.get(id=station_id)
       
        # 獲取該站點附近且符合類別和價格範圍的所有餐廳
        restaurants = Restaurant.objects.filter(
            nearby_stations=station,
            category=category,
            price_level=price_level
        )
       
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data)
    except Station.DoesNotExist:
        return Response({'error': '找不到指定的捷運站'}, status=404)
    except Exception as e:
        return Response({'error': f'發生錯誤：{str(e)}'}, status=500)























