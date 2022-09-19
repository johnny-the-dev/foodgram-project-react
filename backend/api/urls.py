from django.urls import path, include
from rest_framework.routers import DefaultRouter
from djoser.views import UserViewSet
from .views import IngredientViewSet, RecipeViewSet, TagViewSet, CustomUserViewSet

router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('users', CustomUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken'))
]

