# Generated by Django 4.1.1 on 2022-09-26 19:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0013_alter_ingredient_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ['name'], 'verbose_name': 'Тег', 'verbose_name_plural': 'Теги'},
        ),
    ]
