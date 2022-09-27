import django_filters
from recipes.models import Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.NumberFilter(field_name='author__id')
    tags = django_filters.ModelMultipleChoiceFilter(
        to_field_name='slug',
        lookup_expr='slug',
        queryset=Tag.objects.all(),
        conjoined=True
    )
    is_favorited = django_filters.Filter(method='filter_favorited')
    is_in_shopping_cart = django_filters.Filter(method='filter_cart')


    def filter_cart(self, queryset, name, query_value):
        user =  self.request.user
        if user.is_authenticated and query_value == '1':
            queryset = queryset.filter(cart__user=user)
        return queryset

    def filter_favorited(self, queryset, name, query_value):
        user =  self.request.user
        if user.is_authenticated and query_value == '1':
            queryset = queryset.filter(follower__user=user)
        return queryset


    class Meta:
        model = Recipe
        fields = ['author', 'tags']