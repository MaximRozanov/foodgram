from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, RecipeViewSet, TagViewSet, download_shopping_cart, ShoppingCartView, \
    FavoriteView, SubscribeView, ViewSubscriptionView

app_name = 'api'

router = DefaultRouter()

router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path('recipes/download_shopping_cart/', download_shopping_cart),
    path('recipes/<int:id>/shopping_cart/', ShoppingCartView.as_view()),
    path('recipes/{id}/favorite/', FavoriteView.as_view()),
    path('users/subscriptions/', ViewSubscriptionView.as_view()),
    path('users/<int:id>/subscribe/', SubscribeView.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
    path('', include(router.urls)),
]