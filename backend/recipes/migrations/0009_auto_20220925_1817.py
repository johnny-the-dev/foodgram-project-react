# Generated by Django 2.2.28 on 2022-09-25 18:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_auto_20220925_1734'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cart',
            old_name='owner',
            new_name='user',
        ),
    ]
