from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название тега',
        help_text='Введите название тега'
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='Цвет тега',
        help_text='Введите цветовой HEX-код тега'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор тега',
        help_text='Введите уникальный идентификатор тега'
    )

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Теги'
        verbose_name = 'Тег'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название ингредиента',
        help_text='Введите название ингредиента'
    )

    measurement_unit = models.CharField(
        max_length=20,
        verbose_name='Мера измерения',
        help_text='Введите меру измерения'
    )


    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient')
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
        help_text='Введите название рецепта'
    )
    image = models.ImageField(
        verbose_name='Изображение',
        help_text='Выберите изображение',
        upload_to='recipes/images/'
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Введите описание рецепта'
    )
    cooking_time = models.SmallIntegerField(
        verbose_name='Время приготовления (минуты)',
        help_text='Введите время приготовления в минутах'
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )
    
    class Meta:
        ordering = ['-pub_date']
        verbose_name_plural = 'Рецепты'
        verbose_name = 'Рецепт'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredients_lst',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        help_text='Выберите ингредиент'
    )
    amount = models.IntegerField(
        verbose_name='Количество',
        help_text='Укажите количество ингредиента',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"'ingredient': {self.ingredient.name}, 'amount': {self.amount}"

class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='tags_lst',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег',
        help_text='Выберите тег'
    )    


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='following'    
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='follower',
        blank=True,
        null=True
    )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='favorite_recipes',
        blank=True,
        null=True
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='follower',
        blank=True,
        null=True
    )


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Владелец списка',
        related_name='cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='cart',
        blank=True,
        null=True
    )
