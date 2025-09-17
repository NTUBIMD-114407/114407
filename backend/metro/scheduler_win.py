import schedule
import time
from services.metro_train_service import fetch_metro_first_last_trains
from services.review_service import update_restaurant_reviews


def job_metro():
    print("[排程] 自動更新捷運首末班車資料...")
    fetch_metro_first_last_trains()
    print("[排程] 捷運首末班車更新完成！")


def job_review():
    print("[排程] 自動更新餐廳評論...")
    update_restaurant_reviews()
    print("[排程] 餐廳評論更新完成！")


# 每天凌晨2點執行捷運首末班車更新
schedule.every().day.at("02:00").do(job_metro)
# 每天凌晨3點執行餐廳評論更新
schedule.every().day.at("03:00").do(job_review)


print("啟動自動更新排程（捷運首末班車 02:00、餐廳評論 03:00）...")
while True:
    schedule.run_pending()
    time.sleep(60)



