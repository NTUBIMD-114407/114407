from django.core.management.base import BaseCommand
from metro.services.review_service import update_restaurant_reviews


class Command(BaseCommand):
    help = 'Update restaurant reviews from Google Places API'


    def handle(self, *args, **options):
        self.stdout.write('Starting review update...')
        update_restaurant_reviews()
        self.stdout.write(self.style.SUCCESS('Review update completed'))


