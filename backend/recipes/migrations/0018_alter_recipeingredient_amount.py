# Generated by Django 4.1.1 on 2022-10-04 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0017_alter_recipeingredient_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.IntegerField(blank=True, help_text='Укажите количество ингредиента', null=True, verbose_name='Количество'),
        ),
    ]
