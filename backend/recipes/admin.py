from django.contrib import admin
from recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag


class RecipeIngredientAdmin(admin.TabularInline):
    model = RecipeIngredient
    extra = 0
    min_num = 1
    verbose_name_plural = 'список ингредиентов'
    verbose_name = 'ингредиент'
    readonly_fields = ('get_measurement_unit',)

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit

    get_measurement_unit.short_description = 'мера измерения'


class RecipeTagAdmin(admin.TabularInline):
    model = RecipeTag
    extra = 0
    min_num = 1
    verbose_name_plural = 'список тегов'
    verbose_name = 'тег'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientAdmin, RecipeTagAdmin)
    list_display = (
        'name',
        'author'
    )
    list_display_links = ('name',)
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name',)
    readonly_fields = ('get_favorite_count',)

    def get_favorite_count(self, obj):
        return obj.follower.count()

    get_favorite_count.short_description = 'в избранном'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    inlines = (RecipeTagAdmin, )
    list_display = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientAdmin,)
    list_display = (
        'name',
        'measurement_unit'
    )
    list_filter = ('name',)
    search_fields = ('name',)
