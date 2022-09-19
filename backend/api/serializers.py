from rest_framework import serializers
from recipes.models import Recipe, RecipeIngredient, RecipeTag, Tag, Ingredient, Cart, User
from djoser.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        extra_kwargs = {
            'name': {'required': False},
            'color': {'required': False},
            'slug': {'required': False}
        }


class IngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(required=False)

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        extra_kwargs = {
            'name': {'required': False},
            'measurement_unit': {'required': False}
        }


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount') 

    def get_name(self, obj):
        return obj.name

    def get_measurement_unit(self, obj):
        return obj.measurement_unit


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
        if self.context['request'].user.is_authenticated:
            try:
                self.context['request'].user.following.get(author=obj)
                return True
            except:
                return False
        else:
            return False


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    ingredients = IngredientSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        

    # def validate(self, attrs):
    #     return super().validate(attrs)

    # def create(self, validated_data):
    #     # ingredients = validated_data.pop('ingredients')
    #     # tags = validated_data.pop('tags')
    #     recipe = Recipe.objects.create(**validated_data)
    #     # for ingredient in ingredients:
    #         # try:
    #         #     current_ingredient = Ingredient.objects.get(id=ingredient['id'])
    #         # except:
    #         #     raise serializers.ValidationError(f'ингредиент с id={ingredient["id"]} отсутствует')
    #         # else:
    #         # RecipeIngredient.objects.create(
    #             # recipe=recipe,
    #             # amount=ingredient['amount'],
    #             # ingredient=ingredient['id']
    #         # )
    #     # for tag_id in tags:
    #     #     try:
    #     #         current_tag = Tag.objects.get(id=tag_id)
    #     #     except:
    #     #         raise serializers.ValidationError(f'тег c id={tag_id} отсутствует')
    #     #     else:
    #     #         RecipeTag.objects.create(recipe=recipe, tag=current_tag)
    #     return recipe


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = RecipeIngredientSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    
    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            # 'image',
            'text',
            'cooking_time'
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_obj in ingredients:
            try:
                current_ingredient = RecipeIngredient.objects.get(
                    recipe=recipe,
                    ingredient=ingredient_obj['id'],
                )
            except:
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=ingredient_obj['id'],
                    amount=ingredient_obj['amount']
                )
            else:
                current_ingredient.amount+=ingredient_obj['amount']
        for tag in tags:
            RecipeTag.objects.get_or_create(recipe=recipe, tag=tag)
        print()
        print()
        print()
        print(recipe.ingredients.all())
        print()
        print()
        print()
        return recipe


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'    
        )


class FollowUserSerializer(CustomUserSerializer):
    recipes = RecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()
    
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