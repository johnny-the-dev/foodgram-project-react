# Generated by Django 4.1.1 on 2022-09-26 19:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0012_alter_recipe_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ['name'], 'verbose_name': 'Ингредиент', 'verbose_name_plural': 'Ингредиенты'},
        ),
    ]
