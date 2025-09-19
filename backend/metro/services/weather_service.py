import requests
from django.conf import settings
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


class WeatherService:
    def __init__(self):
        self.api_key = getattr(settings, 'CWB_API_KEY', None)
        self.base_url = "https://opendata.cwb.gov.tw/api/v1/rest/datastore"
       
        if not self.api_key:
            logger.warning("中央氣象局 API 金鑰未設置，將使用預設天氣資訊")
           
    def get_current_weather(self, latitude, longitude):
        """獲取指定位置的當前天氣資訊"""
        if not self.api_key:
            # 如果沒有 API 金鑰，返回預設值
            return {
                'temperature': 25.0,
                'weather': '晴'
            }
           
        try:
            # 使用經緯度查詢天氣
            params = {
                'Authorization': self.api_key,
                'locationName': '臺北市',  # 暫時固定為臺北市
                'elementName': ['TEMP', 'Wx']  # 溫度和天氣現象
            }
           
            response = requests.get(f"{self.base_url}/F-C0032-001", params=params)
            response.raise_for_status()
            data = response.json()
           
            # 解析天氣數據
            weather_data = data['records']['location'][0]['weatherElement']
            temperature = float(weather_data[0]['time'][0]['elementValue'][0]['value'])
            weather = weather_data[1]['time'][0]['elementValue'][0]['value']
           
            return {
                'temperature': temperature,
                'weather': weather
            }
           
        except Exception as e:
            logger.error(f"獲取天氣資訊時發生錯誤: {str(e)}")
            # 發生錯誤時返回預設值
            return {
                'temperature': 25.0,
                'weather': '晴'
            }


