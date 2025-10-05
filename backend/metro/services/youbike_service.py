import requests
from django.conf import settings
from django.utils import timezone
from ..models import YouBikeStation, Station, YouBikeHistory
import xml.etree.ElementTree as ET
import json
import logging
from django.db import transaction
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime, timedelta
from django.db.models import Avg
from .weather_service import WeatherService


logger = logging.getLogger(__name__)


class YouBikeService:
    def __init__(self):
        self.taipei_api_url = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"
        self.new_taipei_api_url = "https://data.ntpc.gov.tw/api/datasets/010e5b15-3823-4b20-b401-b1cf00055bc5/json?page=0&size=2000"
        self.weather_service = WeatherService()
       
        print(f"\n=== 初始化 YouBike 服務 ===")
        print(f"API URL: {self.taipei_api_url}")
        print(f"新北市 API URL: {self.new_taipei_api_url}")
        print(f"使用測試數據: {settings.USE_TEST_DATA}")
        print("===========================\n")


        if not self.taipei_api_url:
            print("警告: API 憑證未設置，將使用測試數據")
            settings.USE_TEST_DATA = True


    def initialize_stations(self):
        """初始化台北市 YouBike 站點資料"""
        stations = self.get_all_stations()
        if not stations:
            return False


        try:
            # 清除現有站點資料
            YouBikeStation.objects.all().delete()
            print("已清除現有站點資料")


            # 創建新站點
            created_count = 0
            for station_data in stations:
                try:
                    YouBikeStation.objects.create(
                        station_id=station_data['sno'],
                        name=station_data['sna'],
                        total_spaces=int(station_data.get('total', 0)),
                        available_bikes=int(station_data.get('available_rent_bikes', 0)),
                        available_spaces=int(station_data.get('available_return_bikes', 0)),
                        latitude=float(station_data.get('latitude', 0)),
                        longitude=float(station_data.get('longitude', 0)),
                        address=station_data.get('ar', '')
                    )
                    created_count += 1
                    print(f"成功創建站點: {station_data['sna']}")
                except Exception as e:
                    print(f"創建站點時發生錯誤: {str(e)}, 資料: {station_data}")
           
            print(f"成功創建 {created_count} 個站點")
            return True
           
        except Exception as e:
            print(f"初始化站點時發生錯誤: {str(e)}")
            print(f"錯誤發生時的資料: {stations}")  # 印出完整的資料結構
            return False


    def _initialize_with_test_data(self):
        """使用測試數據初始化站點"""
        test_stations = [
            {
                'sno': 'TPE0001',
                'sna': '台北車站 YouBike 站',
                'lat': '25.047778',
                'lng': '121.517222',
                'ar': '台北市中正區忠孝西路一段 3 號'
            },
            {
                'sno': 'TPE0002',
                'sna': '市政府 YouBike 站',
                'lat': '25.041171',
                'lng': '121.565728',
                'ar': '台北市信義區市府路 1 號'
            },
            {
                'sno': 'TPE0003',
                'sna': '台大醫院 YouBike 站',
                'lat': '25.045083',
                'lng': '121.516900',
                'ar': '台北市中正區常德街 1 號'
            },
            {
                'sno': 'TPE0004',
                'sna': '捷運善導寺站 YouBike 站',
                'lat': '25.044823',
                'lng': '121.523208',
                'ar': '台北市中正區忠孝東路一段'
            },
            {
                'sno': 'TPE0005',
                'sna': '捷運忠孝新生站 YouBike 站',
                'lat': '25.042356',
                'lng': '121.532905',
                'ar': '台北市大安區新生南路一段'
            }
        ]


        try:
            with transaction.atomic():
                for station_data in test_stations:
                    station, created = YouBikeStation.objects.update_or_create(
                        station_id=station_data['sno'],
                        defaults={
                            'name': station_data['sna'],
                            'total_spaces': 30,  # 測試用預設值
                            'available_spaces': 15,
                            'available_bikes': 15,
                            'latitude': float(station_data['lat']),
                            'longitude': float(station_data['lng']),
                            'address': station_data['ar'],
                            'last_update': timezone.now()
                        }
                    )


                    if created:
                        logger.info(f"創建測試站點: {station.name}")
                        # 更新附近捷運站關聯
                        self._update_nearby_stations(station)
                    else:
                        logger.info(f"更新測試站點: {station.name}")


            logger.info("測試站點初始化完成")
            return True


        except Exception as e:
            logger.error(f"初始化測試站點時發生錯誤: {str(e)}")
            return False


    def _update_nearby_stations(self, youbike_station):
        """更新 YouBike 站點附近的捷運站關聯"""
        try:
            # 獲取所有捷運站
            metro_stations = Station.objects.all()
           
            # 計算距離並找出最近的捷運站（500公尺內）
            nearby_stations = []
            for metro_station in metro_stations:
                distance = self._calculate_distance(
                    float(youbike_station.latitude),
                    float(youbike_station.longitude),
                    float(metro_station.latitude),
                    float(metro_station.longitude)
                )
                if distance <= 0.5:  # 500公尺
                    nearby_stations.append(metro_station)
           
            # 更新關聯
            youbike_station.nearby_stations.set(nearby_stations)
            logger.info(f"更新站點 {youbike_station.name} 的鄰近捷運站: {len(nearby_stations)} 個")


        except Exception as e:
            logger.error(f"更新站點 {youbike_station.name} 的鄰近捷運站時發生錯誤: {str(e)}")


    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """計算兩個坐標點之間的距離（公里）"""
        R = 6371  # 地球半徑（公里）
       
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
       
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c


    def _make_soap_request(self, action, params=None):
        """發送 SOAP 請求到 YouBike API"""
        if settings.USE_TEST_DATA:
            print("使用測試數據模式，跳過 API 請求")
            return None


        # 構建 SOAP 請求
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <{action} xmlns="http://tempuri.org/">
            <userName>{self.username}</userName>
            <passWord>{self.password}</passWord>
            {params if params else ''}
        </{action}>
    </soap:Body>
</soap:Envelope>"""


        try:
            print(f"\n發送請求到 YouBike API:")
            print(f"Action: {action}")
            print(f"Headers: {self.headers}")
            print(f"Request Body: {soap_body}\n")
           
            response = requests.post(
                self.taipei_api_url,
                data=soap_body.encode('utf-8'),
                headers=self.headers,
                verify=False
            )
           
            print(f"Response Status: {response.status_code}")
            print(f"Response Content: {response.text[:200]}...")  # 只顯示前200個字符
           
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"API 請求失敗: {str(e)}")
            return None


    def get_all_stations(self):
        """獲取所有台北市 YouBike 站點資訊"""
        print("\n=== 開始獲取 YouBike 站點資訊 ===")
        print("正在從台北市 API 獲取資料...")
       
        try:
            response = requests.get(self.taipei_api_url)
            if response.status_code == 200:
                stations = response.json()
                print(f"成功獲取 {len(stations)} 個站點資料")
                return stations
            else:
                print(f"API 請求失敗: {response.status_code}")
                return None
        except Exception as e:
            print(f"獲取站點資訊時發生錯誤: {str(e)}")
            return None


    def get_station_by_name(self, station_name):
        """根據站點名稱獲取 YouBike 站點資訊"""
        try:
            stations = self.get_all_stations()
            if not stations:
                return None
               
            for station in stations:
                if station['sna'] == station_name:
                    return station
            return None
        except Exception as e:
            print(f"獲取站點 {station_name} 資訊時發生錯誤: {str(e)}")
            return None


    def update_stations(self):
        """更新 YouBike 站點狀態"""
        print("\n=== 開始更新 YouBike 站點狀態 ===")
        current_time = timezone.now()
        print(f"更新時間: {current_time}")
       
        try:
            # 獲取所有站點資訊
            print("正在從 API 獲取站點資訊...")
            stations_data = self.get_all_stations()
           
            if not stations_data:
                print("無法獲取站點資訊")
                return
               
            print(f"成功獲取 {len(stations_data)} 個站點的資訊")
           
            # 獲取資料庫中所有 YouBike 站點的 ID
            db_station_ids = set(YouBikeStation.objects.values_list('station_id', flat=True))
            print(f"資料庫中有 {len(db_station_ids)} 個 YouBike 站點")
           
            # 更新每個站點
            updated_count = 0
            for station_data in stations_data:
                station_id = station_data.get('sno')
                if not station_id:
                    print(f"無法獲取站點ID，跳過此筆資料")
                    continue
                   
                # 只更新資料庫中存在的站點
                if station_id not in db_station_ids:
                    continue
                   
                try:
                    # 查找站點
                    station = YouBikeStation.objects.get(station_id=station_id)
                   
                    # 更新站點狀態
                    old_bikes = station.available_bikes
                    old_spaces = station.available_spaces
                   
                    # 更新站點資訊
                    station.available_bikes = int(station_data.get('available_rent_bikes', 0))
                    station.available_spaces = int(station_data.get('available_return_bikes', 0))
                    station.total_spaces = int(station_data.get('total', 0))
                    station.last_updated = current_time
                    station.save()
                   
                    # 如果車輛數或空位數有變化，創建歷史記錄
                    if old_bikes != station.available_bikes or old_spaces != station.available_spaces:
                        print(f"站點 {station.name} 更新:")
                        print(f"- 可用車輛: {old_bikes}->{station.available_bikes}")
                        print(f"- 可用車位: {old_spaces}->{station.available_spaces}")
                        print(f"- 總車位數: {station.total_spaces}")
                       
                        # 獲取該站點的天氣資訊
                        weather_info = self.weather_service.get_current_weather(
                            latitude=float(station_data.get('latitude', 0)),
                            longitude=float(station_data.get('longitude', 0))
                        )
                       
                        # 直接創建歷史記錄
                        YouBikeHistory.objects.create(
                            station=station,
                            available_bikes=station.available_bikes,
                            available_spaces=station.available_spaces,
                            day_of_week=current_time.weekday(),
                            hour=current_time.hour,
                            minute=current_time.minute,
                            is_holiday=self._is_holiday(current_time),
                            weather=weather_info.get('weather', 'unknown'),
                            temperature=weather_info.get('temperature', 0.0),
                            timestamp=current_time
                        )
                        updated_count += 1
                   
                except YouBikeStation.DoesNotExist:
                    print(f"找不到站點 ID: {station_id}")
                except Exception as e:
                    print(f"更新站點 {station_data.get('sna', 'Unknown')} 時發生錯誤: {str(e)}")
                   
            print(f"\n=== YouBike 站點狀態更新完成 ===")
            print(f"總共更新了 {updated_count} 個站點")
            print(f"更新完成時間: {current_time}")
            return True
           
        except Exception as e:
            print(f"更新 YouBike 站點狀態時發生錯誤: {str(e)}")
            return False


    def predict_availability(self, station_id, target_time=None):
        """預測指定時間的可用車輛數"""
        try:
            station = YouBikeStation.objects.get(station_id=station_id)
            if not target_time:
                target_time = datetime.now()
               
            # 獲取歷史數據
            historical_data = self._get_historical_data(station, target_time)
            if not historical_data:
                return station.available_bikes
               
            # 獲取天氣資訊
            weather_data = self.weather_service.get_current_weather(
                station.latitude,
                station.longitude
            )
           
            # 簡單的預測邏輯：使用最近一小時的平均值
            recent_data = historical_data.filter(
                timestamp__gte=target_time - timedelta(hours=1)
            )
            if recent_data.exists():
                avg_bikes = recent_data.aggregate(Avg('available_bikes'))['available_bikes__avg']
                return round(avg_bikes)
               
            return station.available_bikes
           
        except YouBikeStation.DoesNotExist:
            print(f"找不到站點 ID: {station_id}")
            return None
        except Exception as e:
            print(f"預測可用車輛數時發生錯誤: {str(e)}")
            return None
           
    def _get_historical_data(self, station, target_time):
        """獲取歷史數據"""
        try:
            # 獲取相同星期幾和時間段的歷史數據
            day_of_week = target_time.weekday()
            hour = target_time.hour
           
            return YouBikeHistory.objects.filter(
                station=station,
                day_of_week=day_of_week,
                hour=hour
            ).order_by('-timestamp')
           
        except Exception as e:
            print(f"獲取歷史數據時發生錯誤: {str(e)}")
            return None


    def _parse_response(self, response_text):
        """解析 SOAP 響應"""
        try:
            logger.debug(f"開始解析 SOAP 響應: {response_text[:200]}...")  # 只記錄前200個字符
            root = ET.fromstring(response_text)
           
            # 找到包含 JSON 數據的節點
            for elem in root.iter():
                if elem.text and elem.text.strip():
                    text = elem.text.strip()
                    logger.debug(f"找到可能的 JSON 數據: {text[:200]}...")  # 只記錄前200個字符
                   
                    if text.startswith('[{') or text.startswith('{'):
                        try:
                            data = json.loads(text)
                            if isinstance(data, dict):
                                return [data]
                            return data
                        except json.JSONDecodeError as e:
                            logger.warning(f"JSON 解析失敗: {str(e)}")
                            continue
           
            logger.error("在響應中未找到有效的 JSON 數據")
            return None
           
        except ET.ParseError as e:
            logger.error(f"解析 XML 響應時發生錯誤: {str(e)}")
            logger.debug(f"問題的 XML 內容: {response_text[:200]}...")  # 只記錄前200個字符
            return None
        except Exception as e:
            logger.error(f"解析響應時發生錯誤: {str(e)}")
            return None


    def update_station_status(self):
        """更新所有 YouBike 站點的即時狀態並保存歷史記錄"""
        current_time = timezone.now()
        print(f"\n=== 開始更新 YouBike 站點狀態 ===")
        print(f"更新時間: {current_time}")
       
        stations = self.get_all_stations()
        if not stations:
            print("無法獲取站點資訊")
            return False


        try:
            with transaction.atomic():
                updated_count = 0
                for station_data in stations:
                    station_id = station_data['sno']
                   
                    # 更新站點即時資訊
                    station = YouBikeStation.objects.filter(station_id=station_id).first()
                    if not station:
                        print(f"找不到站點 ID: {station_id}")
                        continue
                   
                    # 更新即時資訊
                    old_bikes = station.available_bikes
                    old_spaces = station.available_spaces
                   
                    # 使用新的欄位名稱
                    station.available_bikes = int(station_data.get('available_rent_bikes', 0))
                    station.available_spaces = int(station_data.get('available_return_bikes', 0))
                    station.total_spaces = int(station_data.get('total', 0))
                    station.last_updated = timezone.now()
                    station.save()
                   
                    # 如果數值有變化，創建歷史記錄
                    if old_bikes != station.available_bikes or old_spaces != station.available_spaces:
                        print(f"站點 {station.name} 更新:")
                        print(f"- 可用車輛: {old_bikes} -> {station.available_bikes}")
                        print(f"- 可用車位: {old_spaces} -> {station.available_spaces}")
                        print(f"- 更新時間: {station_data.get('updateTime')}")
                       
                        # 獲取該站點的天氣資訊
                        weather_info = self.weather_service.get_current_weather(
                            latitude=float(station_data.get('latitude', 0)),
                            longitude=float(station_data.get('longitude', 0))
                        )
                       
                        YouBikeHistory.objects.create(
                            station=station,
                            available_bikes=station.available_bikes,
                            available_spaces=station.available_spaces,
                            day_of_week=current_time.weekday(),
                            hour=current_time.hour,
                            minute=current_time.minute,
                            is_holiday=self._is_holiday(current_time),
                            weather=weather_info.get('weather', 'unknown'),
                            temperature=weather_info.get('temperature', 0.0),
                            timestamp=current_time
                        )
                        updated_count += 1
               
                print(f"\n=== YouBike 站點狀態更新完成 ===")
                print(f"總共更新了 {updated_count} 個站點的歷史記錄")
                print(f"更新完成時間: {current_time}\n")
            return True
           
        except Exception as e:
            print(f"更新站點狀態時發生錯誤: {str(e)}")
            print(f"錯誤發生時的資料: {stations}")  # 印出完整的資料結構
            return False


    def _is_holiday(self, date):
        """判斷是否為假日（週末）"""
        return date.weekday() >= 5  # 5 和 6 分別是週六和週日



