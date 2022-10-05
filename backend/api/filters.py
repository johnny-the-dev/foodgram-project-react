import django_filters
from recipes.models import Recipe, Tag
from rest_framework.exceptions import NotAcceptable, NotAuthenticated


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.NumberFilter(field_name='author__id')
    tags = django_filters.ModelMultipleChoiceFilter(
        to_field_name='slug',
        lookup_expr='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = django_filters.Filter(method='filter_favorited')
    is_in_shopping_cart = django_filters.Filter(method='filter_cart')

    def filter_cart(self, queryset, name, query_value):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated
        if query_value == '1':
            return queryset.filter(cart__user=user)
        elif query_value == '0':
            return queryset
        else:
            raise NotAcceptable(f'{name} принимает значения 0 или 1')

    def filter_favorited(self, queryset, name, query_value):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated
        if query_value == '1':
            return queryset.filter(follower__user=user)
        elif query_value == '0':
            return queryset
        else:
            raise NotAcceptable(f'{name} принимает значения 0 или 1')

    class Meta:
        model = Recipe
        fields = ('author', 'tags')
