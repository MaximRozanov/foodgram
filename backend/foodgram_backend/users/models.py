from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    email = models.EmailField(
        max_length=254,
        blank=False,
        unique=True,
    )
    first_name = models.CharField(
        max_length=150,
        blank=False,
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
    )
    username = models.CharField(
        max_length=150,
        unique=True,
    )
    avatar = models.ImageField(
        blank=True,
        null=True,
        upload_to='media/avatars',
    )


class Subscription(models.Model):
    user = models.ForeignKey(
        MyUser,
        related_name='follower',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        MyUser,
        related_name='author',
        on_delete=models.CASCADE,
    )
