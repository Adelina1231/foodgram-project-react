import csv
import os

from django.core.management.base import BaseCommand
from recipes.models import Ingredient

from foodgram.settings import BASE_DIR

class Command(BaseCommand):
    help = 'Загрузка данных из CSV-файлов'

    def handle(self, *args, **options):
        file_path = os.path.join(BASE_DIR, 'data')
        with open(
            f'{file_path}/ingredients.csv', 'r', encoding='UTF-8'
        ) as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                Ingredient.objects.get_or_create(
                    name=row[0], measurement_unit=row[1]
                )
