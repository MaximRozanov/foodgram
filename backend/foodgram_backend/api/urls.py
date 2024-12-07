from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (AvatarView, FavoriteView, IngredientViewSet,
                       RecipeViewSet, ShoppingCartView, SubscribeView,
                       TagViewSet, UserViewSet, ViewSubscriptionView,
                       download_shopping_cart, short_url)

app_name = 'api'

router = DefaultRouter()

router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path('recipes/download_shopping_cart/', download_shopping_cart),
    path('recipes/<int:id>/shopping_cart/', ShoppingCartView.as_view()),
    path('recipes/<int:id>/favorite/', FavoriteView.as_view()),
    path('recipes/<int:pk>/get-link/', RecipeViewSet.as_view({'get': 'get_link'})),
    path('', include(router.urls)),
    path('users/subscriptions/', ViewSubscriptionView.as_view()),
    path('users/<int:id>/subscribe/', SubscribeView.as_view()),
    path('users/me/', UserViewSet.as_view({'get': 'me'})),
    path('users/me/avatar/', AvatarView.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
]
