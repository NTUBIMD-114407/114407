# -*- coding: utf-8 -*-
"""
台北捷運各站方圓 1 公里內的「純酒吧」
→ 嚴格只保留 types 含 'bar' 的地點（預設排除 night_club）
→ 只輸出：station_name, place_id (Google), name
"""
import os, time, random
import requests
import pandas as pd
from tqdm import tqdm

# ====== 金鑰（建議用環境變數，並在 GCP 設 referrer / IP 限制）======
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyCSjgDp4YRLipBUWzKnY0-jPkQSsriAu1w")
if not GOOGLE_API_KEY or GOOGLE_API_KEY == "AIzaSyCSjgDp4YRLipBUWzKnY0-jPkQSsriAu1w":
    print("⚠️ 請將 GOOGLE_API_KEY 設為你的 Google 金鑰（或用環境變數 GOOGLE_API_KEY）")

# ====== 參數 ======
RADIUS_METERS = 1000
LANGUAGE = "zh-TW"
REGION = "tw"
NEARBY_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

# 嚴格過濾參數
EXCLUDE_NIGHT_CLUB = True     # 預設排除夜店
MIN_RATING_COUNT = 0          # 若想排除冷門店，可改成 5/10

SLEEP_BETWEEN_REQUESTS = 0.25
SLEEP_FOR_NEXT_PAGE = 2.5
MAX_PAGES_PER_QUERY = 3

# ==== 站點清單（你的清單，可自行增補）====
# ==== 捷運站清單：紅線 + 藍線 ====
STATIONS = [
    # 紅線
    {"station_name": "象山", "lat": 25.03283, "lon": 121.569576},
    {"station_name": "台北101/世貿", "lat": 25.033102, "lon": 121.563292},
    {"station_name": "信義安和", "lat": 25.033326, "lon": 121.553526},
    {"station_name": "大安", "lat": 25.032943, "lon": 121.543551},
    {"station_name": "大安森林公園", "lat": 25.033396, "lon": 121.534882},
    {"station_name": "東門", "lat": 25.033847, "lon": 121.528739},
    {"station_name": "中正紀念堂", "lat": 25.032729, "lon": 121.51827},
    {"station_name": "台大醫院", "lat": 25.041256, "lon": 121.51604},
    {"station_name": "台北車站", "lat": 25.046255, "lon": 121.517532},
    {"station_name": "中山", "lat": 25.052685, "lon": 121.520392},
    {"station_name": "雙連", "lat": 25.057805, "lon": 121.520627},
    {"station_name": "民權西路", "lat": 25.062905, "lon": 121.51932},
    {"station_name": "圓山", "lat": 25.071353, "lon": 121.520118},
    {"station_name": "劍潭", "lat": 25.084873, "lon": 121.525078},
    {"station_name": "士林", "lat": 25.093535, "lon": 121.52623},
    {"station_name": "芝山", "lat": 25.10306, "lon": 121.522514},
    {"station_name": "明德", "lat": 25.109721, "lon": 121.518848},
    {"station_name": "石牌", "lat": 25.114523, "lon": 121.515559},
    {"station_name": "唭哩岸", "lat": 25.120872, "lon": 121.506252},
    {"station_name": "奇岩", "lat": 25.125491, "lon": 121.501132},
    {"station_name": "北投", "lat": 25.131841, "lon": 121.498633},
    {"station_name": "新北投", "lat": 25.136933, "lon": 121.50253},
    {"station_name": "復興崗", "lat": 25.137474, "lon": 121.485444},
    {"station_name": "忠義", "lat": 25.130969, "lon": 121.47341},
    {"station_name": "關渡", "lat": 25.125633, "lon": 121.467102},
    {"station_name": "竹圍", "lat": 25.13694, "lon": 121.459479},
    {"station_name": "紅樹林", "lat": 25.154042, "lon": 121.458872},
    {"station_name": "淡水", "lat": 25.167818, "lon": 121.445561},

    # 藍線
    {"station_name": "頂埔", "lat": 24.96012, "lon": 121.4205},
    {"station_name": "永寧", "lat": 24.966726, "lon": 121.436072},
    {"station_name": "土城", "lat": 24.973094, "lon": 121.444362},
    {"station_name": "海山", "lat": 24.985339, "lon": 121.448786},
    {"station_name": "亞東醫院", "lat": 24.998037, "lon": 121.452514},
    {"station_name": "府中", "lat": 25.008619, "lon": 121.459409},
    {"station_name": "板橋", "lat": 25.013618, "lon": 121.462302},
    {"station_name": "新埔", "lat": 25.023738, "lon": 121.468361},
    {"station_name": "江子翠", "lat": 25.03001, "lon": 121.47239},
    {"station_name": "龍山寺", "lat": 25.03528, "lon": 121.499826},
    {"station_name": "西門", "lat": 25.04209, "lon": 121.508303},
    {"station_name": "善導寺", "lat": 25.044823, "lon": 121.523208},
    {"station_name": "忠孝新生", "lat": 25.042356, "lon": 121.532905},
    {"station_name": "忠孝復興", "lat": 25.041629, "lon": 121.543767},
    {"station_name": "忠孝敦化", "lat": 25.041478, "lon": 121.551098},
    {"station_name": "國父紀念館", "lat": 25.041349, "lon": 121.557802},
    {"station_name": "市政府", "lat": 25.041171, "lon": 121.565228},
    {"station_name": "永春", "lat": 25.040859, "lon": 121.576293},
    {"station_name": "後山埤", "lat": 25.045055, "lon": 121.582522},
    {"station_name": "昆陽", "lat": 25.050461, "lon": 121.593268},
    {"station_name": "南港", "lat": 25.052116, "lon": 121.606686},
]


def nearby_bars_strict(lat: float, lng: float):
    """
    Nearby Search + 嚴格過濾：
    - 只保留 place['types'] 包含 'bar'
    - 若 EXCLUDE_NIGHT_CLUB=True，則剔除包含 'night_club' 的地點
    - 可選：以 user_ratings_total 門檻過濾
    回傳 [(place_id, name), ...]
    """
    results = []
    next_page_token = None
    pages = 0
    while True:
        params = {
            "key": GOOGLE_API_KEY,
            "location": f"{lat},{lng}",
            "radius": RADIUS_METERS,
            "language": LANGUAGE,
            "region": REGION,
            "type": "bar",
        }
        if next_page_token:
            params["pagetoken"] = next_page_token
            time.sleep(SLEEP_FOR_NEXT_PAGE)

        r = requests.get(NEARBY_URL, params=params, timeout=30)
        data = r.json()
        status = data.get("status", "")
        if status not in ("OK", "ZERO_RESULTS"):
            raise RuntimeError(f"Nearby status={status}, error_message={data.get('error_message')}")

        for place in data.get("results", []):
            types = set(place.get("types", []))
            if "bar" not in types:
                continue
            if EXCLUDE_NIGHT_CLUB and "night_club" in types:
                continue
            if place.get("user_ratings_total", 0) < MIN_RATING_COUNT:
                continue

            pid = place.get("place_id")
            nm = place.get("name")
            if pid and nm:
                results.append((pid, nm))

        next_page_token = data.get("next_page_token")
        if next_page_token:
            pages += 1
            if pages >= MAX_PAGES_PER_QUERY:
                break
        else:
            break

        time.sleep(SLEEP_BETWEEN_REQUESTS)
    return results

def main():
    rows = []
    for s in tqdm(STATIONS):
        lat, lng = s["lat"], s["lon"]
        station = s["station_name"]
        try:
            places = nearby_bars_strict(lat, lng)
            for pid, nm in places:
                rows.append({"station_name": station, "place_id": pid, "name": nm})
            time.sleep(SLEEP_BETWEEN_REQUESTS)
        except Exception as e:
            print(f"⚠️ 站「{station}」查詢失敗：{e}")

    if not rows:
        print("⚠️ 沒抓到資料，請確認 API 金鑰與 Places API 是否啟用。")
        return

    df = pd.DataFrame(rows).drop_duplicates(["station_name", "place_id"])
    df.to_csv("bars_google_placeid_strict.csv", index=False, encoding="utf-8-sig")
    print("✅ 完成：bars_google_placeid_strict.csv（station_name, place_id, name）")

if __name__ == "__main__":
    main()
