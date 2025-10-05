import logging
import requests
import json
from datetime import datetime
from django.conf import settings
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from django.db import close_old_connections
from .models import TrainInfo
from django.apps import apps
from apscheduler.schedulers.base import STATE_RUNNING
import urllib3
from apscheduler.events import EVENT_JOB_MISSED


# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# 設置 APScheduler 的日誌級別為 ERROR，大幅減少不必要的日誌
logging.getLogger('apscheduler').setLevel(logging.ERROR)


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)  # 改為 WARNING 級別以減少日誌輸出


def missed_job_listener(event):
    """處理錯過的任務，但不記錄日誌"""
    pass


def fetch_train_info():
    """從台北捷運 API 獲取列車到站資訊"""
    try:
        # 準備請求
        headers = {
            'Content-Type': 'text/xml; charset=utf-8'
        }
       
        # SOAP 請求內容
        soap_request = '''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <getTrackInfo xmlns="http://tempuri.org/" />
  </soap:Body>
</soap:Envelope>'''


        # 發送請求
        response = requests.post(
            'https://ws.metro.taipei/MetroApi/TrackInfo.asmx',
            headers=headers,
            data=soap_request.encode('utf-8'),
            verify=False,
            timeout=30
        )


        # 檢查響應狀態
        if response.status_code != 200:
            return []


        # 解析 XML 響應
        from xml.etree import ElementTree
        root = ElementTree.fromstring(response.content)
       
        # 提取所需資訊
        trains_data = []
        for train in root.findall('.//{http://tempuri.org/}TrainInfo'):
            train_info = {}
            for child in train:
                tag = child.tag.split('}')[-1]  # 移除命名空間
                train_info[tag] = child.text
            trains_data.append(train_info)
           
        return trains_data


    except Exception as e:
        logger.error(f'獲取列車資訊時發生錯誤: {str(e)}')
        return []


def get_line_by_station(station_name):
    """根據站名判斷路線"""
    # 定義各路線包含的站名
    line_stations = {
        '文湖線': ['動物園', '木柵', '萬芳社區', '萬芳醫院', '辛亥', '麟光', '六張犁', '科技大樓', '大安',
                '忠孝復興', '南京復興', '中山國中', '松山機場', '大直', '劍南路', '西湖', '港墘', '文德',
                '內湖', '大湖公園', '葫洲', '東湖', '南港軟體園區', '南港展覽館'],
        '淡水信義線': ['淡水', '紅樹林', '竹圍', '關渡', '忠義', '復興崗', '北投', '奇岩', '唭哩岸',
                    '石牌', '明德', '芝山', '士林', '劍潭', '圓山', '民權西路', '雙連', '中山',
                    '台北車站', '台大醫院', '中正紀念堂', '東門', '大安森林公園', '大安', '信義安和',
                    '台北101/世貿', '象山'],
        '松山新店線': ['新店', '新店區公所', '七張', '大坪林', '景美', '萬隆', '公館', '台電大樓',
                    '古亭', '中正紀念堂', '小南門', '西門', '北門', '中山', '松江南京', '南京復興',
                    '台北小巨蛋', '南京三民', '松山'],
        '中和新蘆線': ['蘆洲', '三民高中', '徐匯中學', '三和國中', '三重國小', '大橋頭', '台北橋',
                    '菜寮', '三重', '先嗇宮', '頭前庄', '新莊', '輔大', '丹鳳', '迴龍', '第一果菜',
                    '民權西路', '中山國小', '行天宮', '松江南京', '忠孝新生', '東門', '古亭', '頂溪',
                    '永安市場', '景安', '南勢角'],
        '板南線': ['頂埔', '永寧', '土城', '海山', '亞東醫院', '府中', '板橋', '新埔', '江子翠',
                '龍山寺', '西門', '台北車站', '善導寺', '忠孝新生', '忠孝復興', '忠孝敦化',
                '國父紀念館', '市政府', '永春', '後山埤', '昆陽', '南港', '南港展覽館']
    }
   
    # 移除站名中的「站」字
    station_name = station_name.replace('站', '')
   
    # 檢查站名屬於哪條路線
    for line, stations in line_stations.items():
        for station in stations:
            # 移除站名中的「站」字進行比較
            station = station.replace('站', '')
            if station in station_name or station_name in station:
                return line
    return None


def start():
    """啟動定時任務"""
    try:
        # 獲取 Metro 應用配置
        metro_config = apps.get_app_config('metro')
       
        # 如果調度器已經存在且正在運行，先停止它
        if metro_config.scheduler and metro_config.scheduler.state == STATE_RUNNING:
            metro_config.scheduler.shutdown(wait=False)
            metro_config.scheduler = None


        # 創建新的調度器
        scheduler = BackgroundScheduler({
            'apscheduler.timezone': 'Asia/Taipei',
            'apscheduler.job_defaults.max_instances': 1,
            'apscheduler.job_defaults.coalesce': True,
            'apscheduler.job_defaults.misfire_grace_time': 60  # 設置 misfire 寬限時間為 60 秒
        })
       
        # 配置執行器，使用單線程執行器
        executors = {
            'default': ThreadPoolExecutor(max_workers=1)
        }
        scheduler.configure(executors=executors)
       
        # 添加 Django 作業存儲
        scheduler.add_jobstore(DjangoJobStore(), "default")
       
        # 清理舊的任務
        scheduler.remove_all_jobs()
       
        # 添加錯過任務的監聽器
        scheduler.add_listener(missed_job_listener, EVENT_JOB_MISSED)
       
        # 每30秒執行一次
        scheduler.add_job(
            fetch_train_info,
            'interval',
            seconds=30,
            id='fetch_train_info_job',
            name='fetch_train_info',
            replace_existing=True,
            max_instances=1,
            coalesce=True,
            misfire_grace_time=60
        )
       
        # 啟動調度器
        scheduler.start()
        metro_config.scheduler = scheduler
        logger.warning('定時任務已啟動')
    except Exception as e:
        logger.error(f'啟動定時任務時發生錯誤: {str(e)}')


