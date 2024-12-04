from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import UniqueConstraint
from foodgram_backend.constants import EMAIL_LENGTH_LIMIT, USER_LENGTH_LIMIT


class User(AbstractUser):
    email = models.EmailField(
        max_length=EMAIL_LENGTH_LIMIT,
        unique=True,
        null=False,
    )
    first_name = models.CharField(
        max_length=USER_LENGTH_LIMIT,
    )
    last_name = models.CharField(
        max_length=USER_LENGTH_LIMIT,
    )
    username = models.CharField(
        max_length=USER_LENGTH_LIMIT,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Нельзя символы.'
            )
        ]
    )
    avatar = models.ImageField(
        blank=True,
        null=True,
        upload_to='media/avatars',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['username']

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        related_name='subscriptions',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='followers',
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['-id', ]
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author',
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
