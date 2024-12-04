from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import Subscription, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'username',
        'email',
        'first_name',
        'last_name',
        'is_active',
        'is_staff',
    ]
    search_fields = [
        'username',
        'email',
        'first_name',
        'last_name',
    ]
    list_filter = [
        'is_active',
        'is_staff',
    ]
    ordering = ['username']
    empty_value_display = '-пусто-'


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
