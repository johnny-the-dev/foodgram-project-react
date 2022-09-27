from .serializers import (
    CustomUserSerializer, FollowUserSerializer, IngredientSerializer, 
    RecipeSerializer, TagSerializer, FavoriteRecipeSerializer
)
from .permissions import IsAuthorOrReadonly
from .renrerers import CSVCartRenderer
from .pagination import PageNumberLimitPagination, SubscriptionsPagination
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Cart, Favorite, Follow, Ingredient, Recipe, Tag
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from .filters import RecipeFilter


User = get_user_model()

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (filters.SearchFilter,)
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
        kwargs['partial'] = False
        return self.update(request, *args, **kwargs)

    def get_renderers(self):
        if self.action == 'download_shopping_cart' and self.request.user.is_authenticated:
            return [CSVCartRenderer()]
        return super().get_renderers()

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
        url_path='favorite',
        serializer_class=FavoriteRecipeSerializer
    )
    def favorite(self, request, pk):
        recipe = self.get_object()
        if request.method == 'POST':
            _, is_created = Favorite.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            if is_created:
                serializer = self.get_serializer(recipe)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'error':'Рецепт уже есть в избранном.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            favorite = request.user.favorite_recipes.get(recipe=recipe)
        except:
            return Response({'error':'Рецепт не является избранным.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


    @action(
        methods=['get'],
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        instance = request.user.cart.all()
        cart_dct = {}
        for cart_obj in instance:
            for ingredient_amount in cart_obj.recipe.ingredients_lst.all():
                ingredient = ingredient_amount.ingredient.name
                if ingredient in cart_dct:
                    cart_dct[ingredient] += ingredient_amount.amount
                else:
                    cart_dct[ingredient] = ingredient_amount.amount
        result = [
            {'Ингредиент': ingredient, 'Количество': cart_dct[ingredient]} for 
            ingredient in cart_dct
        ]
        return Response(
            result,
            headers={'Content-Disposition': 'attachment; filename=cart.csv'},
            content_type='text/csv',
            status=status.HTTP_200_OK
        )


    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='shopping_cart',
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=FavoriteRecipeSerializer
    )
    def shopping_cart(self, request, pk):
        recipe = self.get_object()
        if request.method == 'POST':
            _, is_created = Cart.objects.get_or_create(user=request.user, recipe=recipe)
            if is_created:
                serializer = self.get_serializer(recipe)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'error': 'Рецепт уже есть в корзине.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            cart_recipe = request.user.cart.get(recipe=recipe)
        except:
            return Response({'error':'Рецепт отсутствует в корзине.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            cart_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


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
                return Response({'error':'Вы не можете подписаться на самого себя.'}, status=status.HTTP_400_BAD_REQUEST)
            _, is_created = Follow.objects.get_or_create(
                user=request.user,
                author=author
            )
            if is_created:
                serializer = self.get_serializer(author)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'error':'Вы уже подписаны на данного автора'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            favorite = request.user.following.get(author=author)
        except:
            return Response({'error':'Вы не подписаны на данного автора.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('get',),
        detail=False,
        url_path='subscriptions',
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=FollowUserSerializer,
        pagination_class = SubscriptionsPagination
    )
    def get_subscriptions(self, request):
        queryset = User.objects.select_related().filter(follower__user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error':'Вы не подписаны ни на одного автора.'}, status=status.HTTP_204_NO_CONTENT)
