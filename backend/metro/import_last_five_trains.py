import os
import sys
import django
import pandas as pd
from datetime import datetime, time
from django.utils import timezone


# 添加專案根目錄到 Python 路徑
current_path = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.dirname(current_path)
sys.path.append(backend_path)


# 設置 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mei_restaurant.settings')
django.setup()


from metro.models import MetroLastFiveTrains


# 定義路線對應關係
LINE_MAPPING = {
    'BL': {'name': '板南線', 'train_type': 1},
    'O': {'name': '中和新蘆線', 'train_type': 2},
    'R': {'name': '淡水信義線', 'train_type': 3},
    'G': {'name': '松山新店線', 'train_type': 4},
    'BR': {'name': '文湖線', 'train_type': 5},
    'Y': {'name': '環狀線', 'train_type': 6},
}


# 定義各路線的終點站
DESTINATION_STATIONS = {
    'BL': {
        '往頂埔': {'id': 'BL01', 'name': '頂埔'},
        '往南港展覽館': {'id': 'BL23', 'name': '南港展覽館'}
    },
    'O': {
        '往南勢角': {'id': 'O01', 'name': '南勢角'},
        '往迴龍': {'id': 'O21', 'name': '迴龍'}
    },
    'R': {
        '往淡水': {'id': 'R02', 'name': '淡水'},
        '往象山': {'id': 'R28', 'name': '象山'}
    },
    'G': {
        '往新店': {'id': 'G01', 'name': '新店'},
        '往松山': {'id': 'G19', 'name': '松山'}
    },
    'BR': {
        '往動物園': {'id': 'BR01', 'name': '動物園'},
        '往南港展覽館': {'id': 'BR24', 'name': '南港展覽館'}
    },
    'Y': {
        '往新北產業園區': {'id': 'Y01', 'name': '新北產業園區'},
        '往大坪林': {'id': 'Y14', 'name': '大坪林'}
    }
}


def import_excel_data(excel_file):
    # 讀取 Excel 檔案
    print(f"Reading Excel file from: {excel_file}")
    df = pd.read_excel(excel_file)
    print(f"Found {len(df)} rows in Excel file")
   
    # 遍歷每一行數據
    for index, row in df.iterrows():
        try:
            print(f"Processing row {index + 1}/{len(df)}")
           
            # 從站名中提取站點ID和路線編號
            station_info = row['站名'].split(' ', 1)
            station_id = station_info[0]
            station_name = station_info[1]
           
            # 根據站點ID判斷路線
            line_no = None
            for prefix in LINE_MAPPING.keys():
                if station_id.startswith(prefix):
                    line_no = prefix
                    break
           
            if line_no is None:
                print(f"Unknown line number: {station_id}")
                continue
               
            train_type = LINE_MAPPING[line_no]['train_type']
           
            # 根據日期設置服務日
            is_weekday = row['日期'] == '平日'
            is_holiday = row['日期'] == '假日'
           
            # 處理每個班次
            for i in range(1, 6):
                train_time = row[f'班次{i}']
                if pd.isna(train_time):
                    continue
               
                # 根據路線和方向設置目的地站點
                direction = row['方向']
                if line_no in DESTINATION_STATIONS and direction in DESTINATION_STATIONS[line_no]:
                    destination = DESTINATION_STATIONS[line_no][direction]
                    destination_station_id = destination['id']
                    destination_station_name = destination['name']
                else:
                    print(f"Unknown direction for line {line_no}: {direction}")
                    continue
                   
                # 創建或更新 MetroLastFiveTrains 記錄
                MetroLastFiveTrains.objects.update_or_create(
                    line_no=line_no,
                    station_id=station_id,
                    destination_station_id=destination_station_id,
                    train_type=train_type,
                    train_sequence=i,
                    defaults={
                        'line_id': line_no,
                        'station_name': station_name,
                        'station_name_en': '',  # 暫時留空
                        'trip_head_sign': direction,
                        'destination_station_name': destination_station_name,
                        'destination_station_name_en': '',  # 暫時留空
                        'train_time': train_time,
                        'monday': is_weekday,
                        'tuesday': is_weekday,
                        'wednesday': is_weekday,
                        'thursday': is_weekday,
                        'friday': is_weekday,
                        'saturday': is_holiday,
                        'sunday': is_holiday,
                        'national_holidays': is_holiday,
                        'src_update_time': timezone.now(),
                        'update_time': timezone.now(),
                        'version_id': 1
                    }
                )
        except Exception as e:
            print(f"Error importing row {index + 1}:")
            print(f"Row data: {row.to_dict()}")
            print(f"Error message: {str(e)}")


if __name__ == '__main__':
    # 指定 Excel 檔案的完整路徑
    excel_file = input("請輸入 Excel 檔案的完整路徑: ").strip()
   
    if not os.path.exists(excel_file):
        print(f"錯誤：找不到檔案 {excel_file}")
        exit(1)
       
    # 執行匯入
    import_excel_data(excel_file)
    print("Import completed!")



