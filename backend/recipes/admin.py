from django.contrib import admin
from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient


class RecipeIngredientAdmin(admin.TabularInline):
    model = RecipeIngredient
    extra = 0
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientAdmin,)
    list_display = (
        'name',
        'author',
        'get_favorite_count'
    )
    list_display_links = ('name',)
    list_filter = ('author', 'name', 'tags')

    def get_favorite_count(self, obj):
        return obj.follower.count()

    get_favorite_count.short_description = 'в избранном'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientAdmin,)
    list_display = (
        'name',
        'measurement_unit'
    )
    list_filter = ('name',)    

