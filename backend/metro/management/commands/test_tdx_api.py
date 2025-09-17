from django.core.management.base import BaseCommand
from metro.services.metro_train_service import get_access_token, fetch_metro_first_last_trains
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '測試 TDX API 連接'


    def handle(self, *args, **options):
        self.stdout.write("開始測試 TDX API 連接...")
       
        # 測試獲取 access token
        self.stdout.write("\n1. 測試獲取 access token...")
        access_token = get_access_token()
        if access_token:
            self.stdout.write(self.style.SUCCESS(f"成功獲取 access token: {access_token[:20]}..."))
        else:
            self.stdout.write(self.style.ERROR("獲取 access token 失敗"))
            return
       
        # 測試獲取捷運首末班車資訊
        self.stdout.write("\n2. 測試獲取捷運首末班車資訊...")
        if fetch_metro_first_last_trains():
            self.stdout.write(self.style.SUCCESS("成功獲取並更新捷運首末班車資訊"))
        else:
            self.stdout.write(self.style.ERROR("獲取捷運首末班車資訊失敗"))



