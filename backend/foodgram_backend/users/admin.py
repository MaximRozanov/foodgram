from django.contrib import admin
from django.contrib.auth import get_user_model

from users.models import Subscription

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'username',
        'email',
        'first_name',
        'last_name',
    ]
    search_fields = [
        'username',
        'email',
    ]
    list_filter = [
        'username',
        'email',
    ]
    ordering = ['username', ]
    empty_value_display = '-empty-'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'author',
        'id'
    ]
    search_fields = [
        'user',
        'author',
    ]
