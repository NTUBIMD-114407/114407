import requests
from django.conf import settings
from django.utils import timezone
from ..models import YouBikeStation, Station, YouBikeHistory
import xml.etree.ElementTree as ET
import json
import logging
from django.db import transaction
from math import radians, sin, cos, sqrt, atan2


logger = logging.getLogger(__name__)


__all__ = ['YouBikeService']


class YouBikeService:
    def __init__(self):
        self.api_url = "https://api.metro.taipei/MetroAPI/UBike.asmx"
        self.headers = {
            "Content-Type": "text/xml; charset=utf-8"
        }
        self.username = settings.METRO_API_USERNAME
        self.password = settings.METRO_API_PASSWORD


    def initialize_stations(self):
        """初始化所有 YouBike 站點資訊（只需執行一次）"""
        logger.info("開始初始化 YouBike 站點資訊...")
       
        # 獲取所有站點資訊
        stations_data = self.get_all_stations()
        if not stations_data:
            logger.warning("無法獲取 YouBike 站點資訊，使用測試數據")
            return self._initialize_with_test_data()


        try:
            with transaction.atomic():
                for station_data in stations_data:
                    station, created = YouBikeStation.objects.update_or_create(
                        station_id=station_data['sno'],
                        defaults={
                            'name': station_data['sna'],
                            'total_spaces': 0,  # 初始值設為0，之後更新
                            'available_spaces': 0,
                            'available_bikes': 0,
                            'latitude': float(station_data['lat']),
                            'longitude': float(station_data['lng']),
                            'address': station_data.get('ar', '')
                        }
                    )


                    if created:
                        logger.info(f"創建新站點: {station.name}")
                        # 更新附近捷運站關聯
                        self._update_nearby_stations(station)
                    else:
                        logger.info(f"更新既有站點: {station.name}")


            logger.info("YouBike 站點初始化完成")
            return True


        except Exception as e:
            logger.error(f"初始化站點時發生錯誤: {str(e)}")
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
        if not self.username or not self.password:
            print(f"API 認證資訊: username={self.username}, password={self.password}")
            return None


        # 根據不同的 action 使用不同的請求格式
        if action == "getYourBikeNearBy":
            soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <getYourBikeNearBy xmlns="http://tempuri.org/">
      <userName>{self.username}</userName>
      <passWord>{self.password}</passWord>
    </getYourBikeNearBy>
  </soap:Body>
</soap:Envelope>"""
        else:  # getYourBikeNearByName
            soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <getYourBikeNearByName xmlns="http://tempuri.org/">
      <userName>{self.username}</userName>
      <passWord>{self.password}</passWord>
      <StationName>{params}</StationName>
    </getYourBikeNearByName>
  </soap:Body>
</soap:Envelope>"""


        try:
            print(f"\n發送請求到 YouBike API: {action}")
            print(f"請求內容:\n{soap_body}\n")
           
            response = requests.post(
                self.api_url,
                data=soap_body.encode('utf-8'),
                headers=self.headers,
                verify=False
            )
            response.raise_for_status()
           
            print(f"API 回應狀態碼: {response.status_code}")
            print(f"API 回應內容:\n{response.text}\n")
           
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"API 請求失敗: {str(e)}")
            return None


    def get_all_stations(self):
        """獲取所有 YouBike 站點資訊"""
        response = self._make_soap_request("getYourBikeNearBy")
        if response:
            data = self._parse_response(response)
            if data:
                logger.info(f"成功獲取 {len(data)} 個站點資訊")
            return data
        return None


    def get_station_by_name(self, station_name):
        """根據站點名稱獲取 YouBike 資訊"""
        response = self._make_soap_request("getYourBikeNearByName", station_name)
        if response:
            data = self._parse_response(response)
            if data:
                logger.info(f"成功獲取站點 {station_name} 的資訊")
            return data
        return None


    def update_stations(self):
        """更新所有 YouBike 站點資訊"""
        if not self.username or not self.password:
            logger.warning("未設置 Metro API 憑證，使用測試數據")
            return self._update_with_test_data()


        data = self.get_all_stations()
        if not data:
            logger.error("無法獲取 YouBike 站點資訊，使用測試數據")
            return self._update_with_test_data()


        try:
            updated_count = 0
            for station_data in data:
                try:
                    station, created = YouBikeStation.objects.update_or_create(
                        station_id=station_data['StationID'],
                        defaults={
                            'name': station_data['StationName'],
                            'total_spaces': int(station_data['TotalSpace']),
                            'available_spaces': int(station_data['AvailableSpace']),
                            'available_bikes': int(station_data['AvailableBike']),
                            'latitude': float(station_data['Latitude']),
                            'longitude': float(station_data['Longitude']),
                            'address': station_data['Address'],
                            'last_update': timezone.now()
                        }
                    )


                    # 創建歷史記錄
                    YouBikeHistory.create_from_station(station)


                    # 更新附近的捷運站關聯
                    if created:
                        self._update_nearby_stations(station)


                    updated_count += 1
                    logger.info(f"更新站點: {station.name} (可用車輛: {station.available_bikes})")


                except Exception as e:
                    logger.error(f"更新站點 {station_data.get('StationName')} 時發生錯誤: {str(e)}")
                    continue


            logger.info(f"成功更新 {updated_count} 個站點")
            return True


        except Exception as e:
            logger.error(f"更新 YouBike 站點時發生錯誤: {str(e)}")
            return False


    def _update_with_test_data(self):
        """使用測試數據更新站點"""
        test_stations = [
            {
                'StationID': 'TPE0001',
                'StationName': '台北車站 YouBike 站',
                'TotalSpace': '30',
                'AvailableSpace': '15',
                'AvailableBike': '15',
                'Latitude': '25.047778',
                'Longitude': '121.517222',
                'Address': '台北市中正區忠孝西路一段 3 號'
            },
            {
                'StationID': 'TPE0002',
                'StationName': '市政府 YouBike 站',
                'TotalSpace': '40',
                'AvailableSpace': '25',
                'AvailableBike': '15',
                'Latitude': '25.041171',
                'Longitude': '121.565728',
                'Address': '台北市信義區市府路 1 號'
            },
            {
                'StationID': 'TPE0003',
                'StationName': '台大醫院 YouBike 站',
                'TotalSpace': '20',
                'AvailableSpace': '8',
                'AvailableBike': '12',
                'Latitude': '25.045083',
                'Longitude': '121.516900',
                'Address': '台北市中正區常德街 1 號'
            }
        ]


        try:
            updated_count = 0
            for station_data in test_stations:
                try:
                    station, created = YouBikeStation.objects.update_or_create(
                        station_id=station_data['StationID'],
                        defaults={
                            'name': station_data['StationName'],
                            'total_spaces': int(station_data['TotalSpace']),
                            'available_spaces': int(station_data['AvailableSpace']),
                            'available_bikes': int(station_data['AvailableBike']),
                            'latitude': float(station_data['Latitude']),
                            'longitude': float(station_data['Longitude']),
                            'address': station_data['Address'],
                            'last_update': timezone.now()
                        }
                    )


                    # 創建歷史記錄
                    YouBikeHistory.create_from_station(station)


                    # 更新附近的捷運站關聯
                    if created:
                        self._update_nearby_stations(station)


                    updated_count += 1
                    logger.info(f"更新測試站點: {station.name} (可用車輛: {station.available_bikes})")


                except Exception as e:
                    logger.error(f"更新測試站點 {station_data.get('StationName')} 時發生錯誤: {str(e)}")
                    continue


            logger.info(f"成功更新 {updated_count} 個測試站點")
            return True


        except Exception as e:
            logger.error(f"更新測試站點時發生錯誤: {str(e)}")
            return False


    def _parse_response(self, response_text):
        """解析 SOAP 響應"""
        try:
            print("開始解析 SOAP 響應...")
           
            # 找到 JSON 數據的開始和結束位置
            json_start = response_text.find('[')
            json_end = response_text.find(']') + 1
           
            if json_start != -1 and json_end != -1:
                json_data = response_text[json_start:json_end]
                print(f"找到 JSON 數據:\n{json_data}\n")
               
                try:
                    data = json.loads(json_data)
                    print(f"成功解析為 JSON 數據:\n{json.dumps(data, indent=2, ensure_ascii=False)}\n")
                    return data
                except json.JSONDecodeError as e:
                    print(f"JSON 解析失敗: {str(e)}")
                    return None
            else:
                print("在響應中未找到 JSON 數據")
                return None
           
        except Exception as e:
            print(f"解析響應時發生錯誤: {str(e)}")
            return None


