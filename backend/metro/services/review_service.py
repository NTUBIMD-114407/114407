import requests
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from ..models import Restaurant, Review, CheckinReview
import logging
from django.db import models
from django.db.models import Avg


logger = logging.getLogger(__name__)


def create_review_from_frontend(restaurant_id, review_data):
    """從前端接收並創建餐廳評論
   
    Args:
        restaurant_id (int): 餐廳 ID
        review_data (dict): 評論資料，包含：
            - reviewer_name (str): 評論者名稱（可選）
            - rating (int): 評分 (1-5)
            - comment (str): 評論內容（可選）
    """
    try:
        # 驗證評分
        rating = review_data.get('rating', 0)
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            logger.error(f"無效的評分: {rating}")
            return None
           
        # 查找餐廳
        restaurant = Restaurant.objects.get(id=restaurant_id)
       
        # 創建評論
        review = Review.objects.create(
            restaurant=restaurant,
            reviewer_name=review_data.get('reviewer_name', '匿名'),
            rating=rating,
            comment=review_data.get('comment', ''),
            created_at=timezone.now()
        )
       
        # 更新餐廳的評分和評論數
        reviews = Review.objects.filter(restaurant=restaurant)
        restaurant.total_ratings = reviews.count()
        restaurant.rating = reviews.aggregate(
            avg_rating=models.Avg('rating')
        )['avg_rating'] or 0
        restaurant.save()
       
        logger.info(f"成功創建評論: {review.id} 於餐廳 {restaurant.name}")
        return review
       
    except Restaurant.DoesNotExist:
        logger.error(f"找不到餐廳 ID: {restaurant_id}")
        return None
    except Exception as e:
        logger.error(f"創建評論時發生錯誤: {str(e)}")
        return None


def update_restaurant_reviews():
    """更新餐廳評論"""
    try:
        # 獲取需要更新的餐廳
        restaurants = Restaurant.objects.filter(
            last_review_update__isnull=True
        ) | Restaurant.objects.filter(
            last_review_update__lt=timezone.now() - timedelta(hours=6)
        )
       
        if not restaurants.exists():
            logger.info("No restaurants need review updates at this time")
            return
       
        logger.info(f"Found {restaurants.count()} restaurants that need review updates")
       
        for restaurant in restaurants:
            try:
                # 構建 Google Places API 請求
                url = f"https://maps.googleapis.com/maps/api/place/details/json"
                params = {
                    'place_id': restaurant.google_place_id,
                    'fields': 'rating,reviews',
                    'key': settings.GOOGLE_PLACES_API_KEY,
                    'language': 'zh-TW'  # 使用繁體中文
                }
               
                response = requests.get(url, params=params)
                data = response.json()
               
                if data['status'] != 'OK':
                    logger.warning(f"Failed to fetch reviews for restaurant {restaurant.name}: {data['status']}")
                    continue
               
                # 更新餐廳評分
                if 'rating' in data['result']:
                    restaurant.rating = data['result']['rating']
                    restaurant.total_ratings = len(data['result'].get('reviews', []))
                    restaurant.save()
               
                # 更新評論
                if 'reviews' in data['result']:
                    for review_data in data['result']['reviews']:
                        # 檢查評論是否已存在
                        existing_review = Review.objects.filter(
                            restaurant=restaurant,
                            reviewer_name=review_data['author_name'],
                            created_at=datetime.fromtimestamp(review_data['time'])
                        ).first()
                       
                        if not existing_review:
                            Review.objects.create(
                                restaurant=restaurant,
                                reviewer_name=review_data['author_name'],
                                rating=review_data['rating'],
                                comment=review_data['text'],
                                created_at=datetime.fromtimestamp(review_data['time'])
                            )
               
                # 更新最後更新時間
                restaurant.last_review_update = timezone.now()
                restaurant.save()
               
                logger.info(f"Successfully updated reviews for restaurant {restaurant.name}")
               
            except Exception as e:
                logger.error(f"Error updating reviews for restaurant {restaurant.name}: {str(e)}")
                continue
       
    except Exception as e:
        logger.error(f"Error in update_restaurant_reviews: {str(e)}")


def create_checkin_review(restaurant_id, review_data):
    """創建打卡版評論
   
    Args:
        restaurant_id (int): 餐廳 ID
        review_data (dict): 評論資料，包含：
            - reviewer_name (str): 評論者名稱（可選）
            - rating (int): 評分 (1-5)
            - comment (str): 評論內容（可選）
    """
    try:
        # 驗證評分
        rating = review_data.get('rating', 0)
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            logger.error(f"無效的評分: {rating}")
            return None
           
        # 查找餐廳
        restaurant = Restaurant.objects.get(id=restaurant_id)
       
        # 創建打卡評論
        review = CheckinReview.objects.create(
            restaurant=restaurant,
            reviewer_name=review_data.get('reviewer_name', '匿名'),
            rating=rating,
            comment=review_data.get('comment', ''),
            created_at=timezone.now()
        )
       
        logger.info(f"成功創建打卡評論: {review.id} 於餐廳 {restaurant.name}")
        return review
       
    except Restaurant.DoesNotExist:
        logger.error(f"找不到餐廳 ID: {restaurant_id}")
        return None
    except Exception as e:
        logger.error(f"創建打卡評論時發生錯誤: {str(e)}")
        return None


def get_checkin_reviews(restaurant_id, limit=10):
    """獲取餐廳的打卡評論列表
   
    Args:
        restaurant_id (int): 餐廳 ID
        limit (int): 返回的評論數量限制
    """
    try:
        reviews = CheckinReview.objects.filter(
            restaurant_id=restaurant_id
        ).order_by('-created_at')[:limit]
       
        return [{
            'id': review.id,
            'reviewer_name': review.reviewer_name,
            'rating': review.rating,
            'comment': review.comment,
            'created_at': review.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for review in reviews]
       
    except Exception as e:
        logger.error(f"獲取打卡評論時發生錯誤: {str(e)}")
        return []



