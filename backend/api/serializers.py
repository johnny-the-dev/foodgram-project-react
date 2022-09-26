import base64
from collections import OrderedDict
from rest_framework import serializers
from recipes.models import Recipe, RecipeIngredient, RecipeTag, Tag, Ingredient, Cart
from djoser.serializers import UserSerializer
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

User = get_user_model()

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)

class TagSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all())

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
    

class IngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)
    name = serializers.CharField(source='ingredient.name', required=False)
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit', required=False)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')  


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        if self.context['request'] and self.context['request'].user.is_authenticated:
            try:
                self.context['request'].user.following.get(author=obj)
                return True
            except:
                return False
        else:
            return False


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = RecipeIngredientSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(min_value=1)
    
    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        try:
            self.context['request'].user.favorite_recipes.get(recipe=obj)
            return True
        except:
            return False

    def get_is_in_shopping_cart(self, obj):
        try:
            self.context['request'].user.cart.get(recipe=obj)
            return True
        except:
            return False

    def validate_ingredients(self, value):
        if value:
            return value
        raise serializers.ValidationError('Добавьте хотя бы один ингредиент.')

    def validate_tags(self, value):
        if value:
            return value
        raise serializers.ValidationError('Добавьте хотя бы один тег.')

    def add_ingredient(self, ingredient, instance):
        # Если один ингредиент указан несколько раз, значение amount складывается
        current_ingredient, status = RecipeIngredient.objects.get_or_create(
            recipe=instance,
            ingredient=ingredient['id']
        )
        if status:
            current_ingredient.amount = ingredient['amount']    
        else:
            current_ingredient.amount += ingredient['amount']
        current_ingredient.save()

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_obj in ingredients:
            self.add_ingredient(ingredient_obj, recipe)
        for tag in tags:
            RecipeTag.objects.get_or_create(recipe=recipe, tag=tag)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients_lst.all().delete()
        instance.tags_lst.all().delete()
        for ingredient_obj in ingredients:
            self.add_ingredient(ingredient_obj, instance)
        for tag in tags:
            RecipeTag.objects.create(recipe=instance, tag=tag)
        instance.name = validated_data['name']
        instance.text = validated_data['text']
        instance.cooking_time = validated_data['cooking_time']
        instance.image = validated_data['image']
        return instance

    def to_representation(self, instance):    
        ret = OrderedDict()
        fields = self._readable_fields

        for field in fields:
            if field.field_name == 'ingredients':
                attribute = instance.ingredients_lst.all()
            else:
                attribute = field.get_attribute(instance)    

            if field.field_name == 'tags':
                ret['tags'] = TagSerializer(instance.tags.all(), many=True).data
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'    
        )


class FollowUserSerializer(CustomUserSerializer):
    recipes = FavoriteRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    
    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        return True

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
