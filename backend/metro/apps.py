from django.apps import AppConfig
from django.conf import settings
import logging
import sys
import os
from apscheduler.schedulers.background import BackgroundScheduler


logger = logging.getLogger(__name__)


class MetroConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'metro'
   
    def ready(self):
        """初始化應用程序"""
        # 只在主進程中運行
        if os.environ.get('RUN_MAIN') != 'true':
            return
           
        # 只在 runserver 命令時運行
        if 'runserver' not in sys.argv:
            return
           
        # 初始化日誌
        logger.info("Metro application is initializing...")
       
        # 檢查 API 設定
        if not settings.USE_TEST_DATA and (not settings.TAIPEI_METRO_API_USERNAME or not settings.TAIPEI_METRO_API_PASSWORD):
            logger.warning("Metro API credentials are not configured")
           
        # 啟動排程器
        try:
            from .services.youbike_service import YouBikeService
           
            # 創建排程器
            scheduler = BackgroundScheduler()
            youbike_service = YouBikeService()
           
            # 設定每5分鐘執行一次更新
            scheduler.add_job(
                youbike_service.update_stations,
                'interval',
                minutes=5,
                id='update_youbike_stations',
                replace_existing=True
            )
           
            # 啟動排程器
            scheduler.start()
            print("\n=== YouBike 站點更新排程已啟動 ===")
            print("更新頻率: 每5分鐘")
            print("==============================\n")
        except Exception as e:
            logger.error(f"啟動排程器時發生錯誤: {str(e)}")




