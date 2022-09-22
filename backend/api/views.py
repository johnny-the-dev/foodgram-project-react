from .serializers import (
    CustomUserSerializer, FollowUserSerializer, IngredientSerializer, 
    RecipeSerializer, TagSerializer, FavoriteRecipeSerializer
)
from .permissions import IsAuthorOrReadonly
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from recipes.models import Favorite, Follow, Ingredient, Recipe, Tag
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet


User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadonly,)

    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
        url_path='favorite'
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            favorite, is_created = Favorite.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            if is_created:
                fav_serializer = FavoriteRecipeSerializer(recipe)
                return Response(fav_serializer.data, status=status.HTTP_201_CREATED)
            return Response({'error':'Рецепт уже есть в избранном.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            favorite = request.user.favorite_recipes.get(recipe=recipe)
        except:
            return Response({'error':'Рецепт не является избранным.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer


    def get_permissions(self):
        if self.action == 'retrieve':
            self.permission_classes = (permissions.IsAuthenticated,)
        elif self.action == 'list':
            self.permission_classes = (permissions.AllowAny,)
        return super(self.__class__, self).get_permissions()

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
            follow, is_created = Follow.objects.get_or_create(
                user=request.user,
                author=author
            )
            if is_created:
                fol_serializer = self.get_serializer(author)
                return Response(fol_serializer.data, status=status.HTTP_201_CREATED)
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
    )
    def get_subscriptions(self, request):
        queryset = User.objects.select_related().filter(follower__user=request.user)
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'notification':'Вы не подписаны ни на одного автора.'}, status=status.HTTP_204_NO_CONTENT)
