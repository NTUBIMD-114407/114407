import requests
import pandas as pd

# Google Places API Key（請確保 API Key 沒有空格）
API_KEY = "AIzaSyCSjgDp4YRLipBUWzKnY0-jPkQSsriAu1w"

# 台北捷運站座標
taipei_mrt_stations = {
    "台北車站": (25.0477, 121.5170),
    "忠孝敦化": (25.0414, 121.5516),
    "西門站": (25.0422, 121.5071),
}

def search_restaurants(station, lat, lng, keyword="美食", radius=500):
    """搜尋捷運站周邊的美食餐廳，返回 捷運站、商家 ID 和 商家名稱"""
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "keyword": keyword,
        "type": "restaurant",
        "key": API_KEY
    }
    response = requests.get(url, params=params)
    
    # 檢查 API 是否成功返回結果
    data = response.json()
    if "error_message" in data:
        print(f"⚠️ Google Places API 錯誤：{data['error_message']}")
        return []
    
    return [{"捷運站": station, "商家ID": r["place_id"], "商家名稱": r["name"]} for r in data.get("results", [])]

# 存放結果
restaurants_data = []

for station, (lat, lng) in taipei_mrt_stations.items():
    print(f"📍 正在抓取 {station} 附近的餐廳...")
    restaurants = search_restaurants(station, lat, lng)
    restaurants_data.extend(restaurants)

# 儲存為 CSV（包含 捷運站、商家ID 和 商家名稱）
df = pd.DataFrame(restaurants_data)
df.to_csv("taipei_mrt_businesses.csv", index=False, encoding="utf-8-sig")

print("✅ 爬取完成！已儲存 taipei_mrt_businesses.csv")
