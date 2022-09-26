# Generated by Django 2.2.28 on 2022-09-25 16:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_auto_20220922_2042'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='count',
        ),
        migrations.AlterField(
            model_name='cart',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.RecipeIngredient', verbose_name='Ингредиент'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(help_text='Выберите изображение', upload_to='recipes/images/', verbose_name='Изображение'),
        ),
    ]
