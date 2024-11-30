from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=128,
        unique=True,
    )
    measurement_unit = models.CharField(
        max_length=64,
    )

    class Meta:
        ordering = ['-id']
        constraints = (
            UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient',
            ),
        )

    def __str__(self):
        return f'{self.name}:{self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        max_length=32,
        unique=True,
    )
    slug = models.SlugField(
        max_length=32,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message='Нельзя символы.'
            )
        ]
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
        max_length=256,
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
    # не забыть добавить константы
    cooking_time = models.IntegerField(
        validators=[
            MinValueValidator(
                1,
                message=f'нельзя меньше {1}'
            )
        ],
        help_text='Время приготовления в минутах',
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
                0.1,
                f'нельзя меньше {1}'
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
        constraints = (
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_cart_user_recipe',
            ),
        )

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

    constraints = (
        UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_favorite_user_recipe',
        )
    )

    def __str__(self):
        return f'{self.recipe} в избранных у {self.user}'
