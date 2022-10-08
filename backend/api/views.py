from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import Cart, Favorite, Follow, Ingredient, Recipe, Tag
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import User

from .filters import IngredientFilter, RecipeFilter
from .pagination import PageNumberLimitPagination, SubscriptionsPagination
from .permissions import IsAuthorOrReadonly
from .renrerers import CSVCartRenderer
from .serializers import (CustomUserSerializer, FavoriteRecipeSerializer,
                          FollowUserSerializer, IngredientSerializer,
                          RecipeSerializer, TagSerializer,
                          UpdateRecipeSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadonly,)
    pagination_class = PageNumberLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        self.serializer_class = UpdateRecipeSerializer
        kwargs['partial'] = False
        return self.update(request, *args, **kwargs)

    def get_renderers(self):
        if (
            self.action == 'download_shopping_cart'
            and self.request.user.is_authenticated
        ):
            return (CSVCartRenderer(),)
        return super().get_renderers()

    def post_del_base(self, request, model, post_error_msg, delete_error_msg):
        recipe = self.get_object()
        if request.method == 'POST':
            _, is_created = model.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            if is_created:
                serializer = self.get_serializer(recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                {'error': f'{post_error_msg}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        object_to_delete = model.objects.filter(recipe=recipe,
                                                user=request.user).first()
        if object_to_delete:
            object_to_delete.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {'error': f'{delete_error_msg}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
        url_path='favorite',
        serializer_class=FavoriteRecipeSerializer
    )
    def favorite(self, request, pk):
        return self.post_del_base(
            request,
            Favorite,
            'Рецепт уже есть в избранном.',
            'Рецепт не является избранным.'
        )

    @action(
        methods=('post', 'delete'),
        detail=True,
        url_path='shopping_cart',
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=FavoriteRecipeSerializer
    )
    def shopping_cart(self, request, pk):
        return self.post_del_base(
            request,
            Cart,
            'Рецепт уже есть в корзине.',
            'Рецепт отсутствует в корзине.'
        )

    @action(
        methods=('get',),
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        instance = request.user.cart.all()
        cart_dct = {}
        for obj in instance:
            for ingredient_amount in obj.recipe.ingredients_lst.all():
                ingredient = ingredient_amount.ingredient.name
                if ingredient in cart_dct:
                    cart_dct[ingredient][0] += ingredient_amount.amount
                else:
                    cart_dct[ingredient] = [
                        ingredient_amount.amount,
                        ingredient_amount.ingredient.measurement_unit
                    ]
        result = [
            {
                'Ингредиент': ingredient,
                'Мера измерения': cart_dct[ingredient][1],
                'Количество': cart_dct[ingredient][0]
            }
            for ingredient in cart_dct
        ]
        return Response(
            result,
            headers={'Content-Disposition': 'attachment; filename=cart.csv'},
            content_type='text/csv',
            status=status.HTTP_200_OK
        )


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    def get_serializer_class(self):
        if self.action == 'me':
            return CustomUserSerializer
        return super().get_serializer_class()

    @action(
        methods=('post', 'delete'),
        detail=True,
        url_path='subscribe',
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=FollowUserSerializer
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, pk=id)
        if request.method == 'POST':
            if author == request.user:
                return Response(
                    {'error': 'Вы не можете подписаться на самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            _, is_created = Follow.objects.get_or_create(
                user=request.user,
                author=author
            )
            if is_created:
                serializer = self.get_serializer(author)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                {'error': 'Вы уже подписаны на данного автора'},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite = request.user.following.filter(author=author).first()
        if favorite:
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Вы не подписаны на данного автора.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=('get',),
        detail=False,
        url_path='subscriptions',
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=FollowUserSerializer,
        pagination_class=SubscriptionsPagination
    )
    def get_subscriptions(self, request):
        queryset = User.objects.select_related().filter(
            follower__user=request.user
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Вы не подписаны ни на одного автора.'},
                status=status.HTTP_204_NO_CONTENT
            )
