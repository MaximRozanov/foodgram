from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient, Favorite, ShoppingCart
from users.models import Subscription

User = get_user_model()


class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'id',
            'avatar',
        ]


class MyUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
        ]


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['avatar', ]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'amount', 'measurement_unit']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'name',
            'image',
            'text',
            'cooking_time',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
        ]


class RecipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'amount', 'measurement_unit']


class CreateRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'name',
            'image',
            'text',
            'cooking_time',
            'ingredients',
        ]


class AdIngredientRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['user', 'recipe']


class ViewFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ['user', 'recipe']


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['user', 'author']


class ViewSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        ]
