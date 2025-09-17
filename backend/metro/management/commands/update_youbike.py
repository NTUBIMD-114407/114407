from django.core.management.base import BaseCommand
from metro.services.youbike_service import YouBikeService


class Command(BaseCommand):
    help = '從台北捷運 API 更新 YouBike 站點資訊'


    def handle(self, *args, **options):
        self.stdout.write('開始更新 YouBike 站點資訊...')
       
        service = YouBikeService()
        if service.update_stations():
            self.stdout.write(self.style.SUCCESS('YouBike 站點資訊更新成功！'))
        else:
            self.stdout.write(self.style.ERROR('YouBike 站點資訊更新失敗！'))


