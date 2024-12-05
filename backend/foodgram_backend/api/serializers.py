from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, ShoppingCart, Tag)
from users.models import Subscription, User


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ['avatar', ]


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(allow_null=True, required=False)

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user,
            author=obj
        ).exists()


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        ]

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        ]

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user,
            recipe_id=obj,
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user,
            recipe_id=obj,
        ).exists()


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


class AdIngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class CreateRecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = AdIngredientRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        ]

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Это поле не может быть пустым.'}
            )

        ingredient_ids = [ingredient.get('id') for ingredient in ingredients]
        existing_ingredients = Ingredient.objects.filter(id__in=ingredient_ids)

        if len(existing_ingredients) != len(ingredient_ids):
            existing_ids = {
                ingredient.id for ingredient in existing_ingredients
            }
            missing_ids = set(ingredient_ids) - existing_ids
            raise serializers.ValidationError(
                {'ingredients': (
                    f'Ингредиенты с id {", ".join(map(str, missing_ids))} '
                    'не существуют.'
                )}
            )
        ingredient_count = {}
        for ingredient in ingredients:
            amount = ingredient.get('amount')
            ingredient_id = ingredient.get('id')
            if amount is None or int(amount) < 1:
                raise serializers.ValidationError(
                    {'amount': 'Количество должно быть больше 0.'}
                )
            if ingredient_id in ingredient_count:
                raise serializers.ValidationError(
                    {
                        'ingredient': (
                            'Ингредиент может присутствовать только один раз.'
                        )
                    }
                )
            ingredient_count[ingredient_id] = amount
        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Это поле не может быть пустым.'}
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                {'tags': 'Теги не должны повторяться.'}
            )
        if 'image' not in self.initial_data or not self.initial_data['image']:
            raise serializers.ValidationError(
                {'image': 'Это поле не может быть пустым.'}
            )
        return data

    def create_tags(self, tags, recipe):
        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag)

    def create_ingredients(self, ingredients, recipe):
        recipe_ingredients = [
            RecipeIngredient(
                ingredient_id=ingr['id'],
                recipe=recipe,
                amount=ingr['amount'],
            ) for ingr in ingredients
        ]

        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user

        recipe = Recipe.objects.create(author=author, **validated_data)

        self.add_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        RecipeTag.objects.filter(recipe=instance).delete()
        RecipeIngredient.objects.filter(recipe=instance).delete()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        self.create_ingredients(ingredients, instance)
        self.create_tags(tags, instance)
        instance.name = validated_data.pop('name')
        instance.text = validated_data.pop('text')
        if validated_data.get('image'):
            instance.image = validated_data.pop('image')
        instance.cooking_time = validated_data.pop('cooking_time')
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class ShowFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ['user', 'recipe']

    def to_representation(self, instance):
        return ShowFavoriteSerializer(instance.recipe, context={
            'request': self.context.get('request')
        }).data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['user', 'recipe']

    def to_representation(self, instance):
        return ShowFavoriteSerializer(instance.recipe, context={
            'request': self.context.get('request')
        }).data


class ViewSubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar',
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user,
            author=obj
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = Recipe.objects.filter(author=obj)
        limit = request.query_params.get('recipes_limit', None)
        if limit:
            recipes = recipes[:int(limit)]
        return ShowFavoriteSerializer(
            recipes,
            many=True,
            context={'request': request}
        ).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['user', 'author']
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=['user', 'author'],
            )
        ]

    def to_representation(self, instance):
        return ViewSubscriptionSerializer(
            instance.author,
            context=self.context
        ).data
