import json

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Adds ingredients from json file'

    def handle(self, *args, **options):
        try:
            with open('../data/ingredients.json', 'r') as file:
                ingredients = json.load(file)
                count_new = 0
                for ingredient in ingredients:
                    name = ingredient.get('name')
                    measurement_unit = ingredient.get('measurement_unit')
                    if measurement_unit and name:
                        new, status = Ingredient.objects.get_or_create(
                            name=name
                        )
                        if status:
                            new.measurement_unit = measurement_unit
                            count_new += 1
                            new.save()
                print(f'Добавлено ингредиентов: {count_new}')
        except FileNotFoundError as e:
            print(e)
