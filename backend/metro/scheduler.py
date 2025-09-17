from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.utils import timezone
from metro.services.youbike_service import YouBikeService
from metro.services.review_service import update_restaurant_reviews


def update_youbike_stations():
    """更新所有 YouBike 站點資訊"""
    service = YouBikeService()
    service.update_station_status()


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
   
    # 每15分鐘更新一次 YouBike 站點
    scheduler.add_job(
        update_youbike_stations,
        'interval',
        minutes=15,
        name='update_youbike_stations',
        replace_existing=True
    )
   
    # 每天凌晨三點更新餐廳評論
    scheduler.add_job(
        update_restaurant_reviews,
        'cron',
        hour=3,
        minute=0,
        name='update_restaurant_reviews',
        replace_existing=True
    )
   
    scheduler.start()
    print("排程器已啟動:")
    print("- YouBike 站點將每15分鐘更新一次")
    print("- 餐廳評論將在每天凌晨三點更新")



