from django.core.management.base import BaseCommand
from django.conf import settings
import requests
import json
from metro.models import YouBikeStation
from datetime import datetime


class Command(BaseCommand):
    help = '從北捷 API 初始化捷運站附近的 YouBike 站點資訊'


    def handle(self, *args, **options):
        # 檢查 API 設定
        self.stdout.write("\n=== API 設定檢查 ===")
        self.stdout.write(f"API 用戶名: {settings.TAIPEI_METRO_API_USERNAME}")
        self.stdout.write(f"API 密碼是否設置: {'是' if settings.TAIPEI_METRO_API_PASSWORD else '否'}")
        self.stdout.write("==================\n")


        # 北捷 API
        api_url = "https://api.metro.taipei/MetroAPI/UBike.asmx"
       
        # SOAP 請求標頭
        headers = {
            'Content-Type': 'text/xml; charset=utf-8'
        }
       
        # SOAP 請求內容 - 使用與 Postman 相同的格式
        soap_body = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <getYourBikeNearBy xmlns="http://tempuri.org/">
      <userName>{username}</userName>
      <passWord>{password}</passWord>
    </getYourBikeNearBy>
  </soap:Body>
</soap:Envelope>""".format(
            username=settings.TAIPEI_METRO_API_USERNAME,
            password=settings.TAIPEI_METRO_API_PASSWORD
        )
       
        try:
            # 發送請求獲取站點資料
            self.stdout.write("正在從北捷 API 獲取捷運站附近的 YouBike 站點資料...")
            self.stdout.write(f"請求 URL: {api_url}")
            self.stdout.write("正在發送 SOAP 請求...")
           
            response = requests.post(api_url, data=soap_body, headers=headers, verify=False)
           
            self.stdout.write(f"API 回應狀態碼: {response.status_code}")
            self.stdout.write("正在解析回應資料...")
           
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f'API 請求失敗: {response.status_code}'))
                self.stdout.write(self.style.ERROR(f'回應內容: {response.text}'))
                return
           
            # 解析回應內容
            response_text = response.text
            self.stdout.write("\n=== 回應內容 ===")
            self.stdout.write(response_text[:500])
            self.stdout.write("==================\n")
           
            # 找出 JSON 資料的開始和結束位置
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
           
            if start_idx == -1 or end_idx == 0:
                self.stdout.write(self.style.ERROR('無法在回應中找到有效的 JSON 資料'))
                self.stdout.write(self.style.ERROR('回應內容: ' + response_text[:500] + '...'))
                return
           
            json_data = response_text[start_idx:end_idx]
            self.stdout.write(f"找到 JSON 資料，長度: {len(json_data)}")
           
            stations = json.loads(json_data)
            self.stdout.write(f"成功解析 {len(stations)} 個站點資料")
           
            # 清除現有的站點資料
            self.stdout.write("正在清除現有的站點資料...")
            YouBikeStation.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('已清除現有的站點資料'))
           
            # 創建新的站點
            created_count = 0
            for station in stations:
                try:
                    # 只使用模型支援的欄位
                    YouBikeStation.objects.create(
                        station_id=station['sno'],
                        name=station['sna'],
                        total_spaces=30,  # 預設值
                        available_bikes=15,  # 預設值
                        available_spaces=15,  # 預設值
                        latitude=float(station['lat']),
                        longitude=float(station['lng'])
                    )
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'成功創建站點: {station["sna"]}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'創建站點 {station.get("sna", "Unknown")} 時發生錯誤: {str(e)}'))
           
            self.stdout.write(self.style.SUCCESS(f'\n初始化完成! 總共創建了 {created_count} 個捷運站附近的 YouBike 站點'))
           
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'執行過程中發生錯誤: {str(e)}'))




