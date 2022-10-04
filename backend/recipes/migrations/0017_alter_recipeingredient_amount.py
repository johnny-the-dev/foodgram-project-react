# Generated by Django 4.1.1 on 2022-10-04 08:13

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0016_alter_ingredient_options_alter_recipe_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.IntegerField(blank=True, help_text='Укажите количество ингредиента', null=True, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Количество'),
        ),
    ]
