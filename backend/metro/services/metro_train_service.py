import requests
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from ..models import MetroFirstLastTrain
import logging


logger = logging.getLogger(__name__)


def get_access_token():
    """獲取 TDX API 的 access token"""
    try:
        token_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'client_credentials',
            'client_id': settings.TDX_CLIENT_ID,
            'client_secret': settings.TDX_CLIENT_SECRET
        }
       
        response = requests.post(token_url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            logger.error(f"獲取 access token 失敗: {response.text}")
            return None
    except Exception as e:
        logger.error(f"獲取 access token 時發生錯誤: {str(e)}")
        return None


def fetch_metro_first_last_trains():
    """獲取並更新捷運首末班車資訊"""
    try:
        # 獲取 access token
        access_token = get_access_token()
        if not access_token:
            logger.error("無法獲取 access token")
            return False


        # 台北捷運 API
        trtc_url = "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/FirstLastTimetable/TRTC?$format=JSON"
        # 新北捷運 API
        ntmc_url = "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/FirstLastTimetable/NTMC?$format=JSON"
       
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
       
        # 獲取台北捷運數據
        trtc_response = requests.get(trtc_url, headers=headers)
        trtc_data = trtc_response.json()
       
        # 獲取新北捷運數據
        ntmc_response = requests.get(ntmc_url, headers=headers)
        ntmc_data = ntmc_response.json()
       
        # 合併數據
        all_data = trtc_data + ntmc_data
       
        # 更新數據庫
        update_count = 0
        for item in all_data:
            try:
                # 解析時間字符串
                first_train_time = datetime.strptime(item['FirstTrainTime'], '%H:%M').time()
                last_train_time = datetime.strptime(item['LastTrainTime'], '%H:%M').time()
                src_update_time = datetime.fromisoformat(item['SrcUpdateTime'].replace('Z', '+00:00'))
                update_time = datetime.fromisoformat(item['UpdateTime'].replace('Z', '+00:00'))
               
                # 創建或更新記錄
                train_info, created = MetroFirstLastTrain.objects.update_or_create(
                    line_no=item['LineNo'],
                    line_id=item['LineID'],
                    station_id=item['StationID'],
                    destination_station_id=item['DestinationStaionID'],
                    train_type=item['TrainType'],
                    defaults={
                        'station_name': item['StationName']['Zh_tw'],
                        'station_name_en': item['StationName']['En'],
                        'trip_head_sign': item['TripHeadSign'],
                        'destination_station_name': item['DestinationStationName']['Zh_tw'],
                        'destination_station_name_en': item['DestinationStationName']['En'],
                        'first_train_time': first_train_time,
                        'last_train_time': last_train_time,
                        'monday': item['ServiceDay']['Monday'],
                        'tuesday': item['ServiceDay']['Tuesday'],
                        'wednesday': item['ServiceDay']['Wednesday'],
                        'thursday': item['ServiceDay']['Thursday'],
                        'friday': item['ServiceDay']['Friday'],
                        'saturday': item['ServiceDay']['Saturday'],
                        'sunday': item['ServiceDay']['Sunday'],
                        'national_holidays': item['ServiceDay']['NationalHolidays'],
                        'src_update_time': src_update_time,
                        'update_time': update_time,
                        'version_id': item['VersionID']
                    }
                )
                update_count += 1
               
            except Exception as e:
                logger.error(f"處理捷運首末班車數據時發生錯誤: {str(e)}")
                continue
       
        logger.info(f"成功更新 {update_count} 筆捷運首末班車數據")
        return True
       
    except Exception as e:
        logger.error(f"獲取捷運首末班車數據時發生錯誤: {str(e)}")
        return False


def get_station_first_last_trains(station_id):
    """獲取特定站點的首末班車資訊"""
    try:
        trains = MetroFirstLastTrain.objects.filter(station_id=station_id)
        return trains
    except Exception as e:
        logger.error(f"獲取站點 {station_id} 的首末班車資訊時發生錯誤: {str(e)}")
        return None



