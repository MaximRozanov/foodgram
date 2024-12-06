from datetime import datetime
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint
from foodgram_backend.constants import (COOKING_TIME_MIN,
                                        INGREDIENT_AMOUNT_MIN,
                                        INGREDIENT_LENGTH_LIMIT,
                                        RECIPE_LENGTH_LIMIT, TAG_LENGTH_LIMIT,
                                        UNIT_LENGTH_LIMIT)

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        max_length=INGREDIENT_LENGTH_LIMIT,
        unique=True,
    )
    measurement_unit = models.CharField(
        max_length=UNIT_LENGTH_LIMIT,
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient',
            ),
        ]

    def __str__(self):
        return f'{self.name}:{self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        max_length=TAG_LENGTH_LIMIT,
        unique=True,
    )
    slug = models.SlugField(
        max_length=TAG_LENGTH_LIMIT,
        unique=True,
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(
        max_length=RECIPE_LENGTH_LIMIT,
    )
    image = models.ImageField(
        blank=False,
        upload_to='media/recipes/',
    )
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient,
        blank=False,
        through='RecipeIngredient',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        blank=False,
        through='RecipeTag',
        related_name='recipes',

    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                COOKING_TIME_MIN,
                message=f'нельзя меньше {COOKING_TIME_MIN}'
            )
        ],
        help_text='Время приготовления в минутах'
    )
    pub_date = models.DateTimeField(
        default=datetime.now,
    )


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_list',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe',
    )
    amount = models.FloatField(
        validators=[
            MinValueValidator(
                INGREDIENT_AMOUNT_MIN,
                f'нельзя меньше {INGREDIENT_AMOUNT_MIN}'
            )
        ],
    )

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='tag_list',
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tag_recipe',
    )

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f'{self.recipe} имеет тег {self.tag}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_cart_user_recipe',
            ),
        ]

    def __str__(self):
        return f'{self.recipe} в корзине {self.user}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_user_recipe',
            ),
        ]

    def __str__(self):
        return f'{self.recipe} в избранных у {self.user}'
