from .services.metro_train_service import fetch_metro_first_last_trains


def update_metro_first_last_trains_cron():
    """定時自動更新捷運首末班車資料"""
    fetch_metro_first_last_trains()



