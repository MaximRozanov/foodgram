from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import IsAuthorOrAdminOrReadOnly
from api.serializers import TagSerializer, IngredientSerializer, RecipeSerializer, CreateRecipeSerializer, \
    SubscriptionSerializer, ViewSubscriptionSerializer, FavoriteSerializer, ShoppingCartSerializer
from recipes.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart
from users.models import Subscription

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthorOrAdminOrReadOnly, ]  # Добавить только ток авторизованный пермишн
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return CreateRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context


class ViewSubscriptionView(APIView):
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self, user):
        return User.objects.filter(author__user=user)

    def get(self, request):
        user = request.user
        queryset = self.get_queryset(user)

        if not queryset.exist():
            return Response([], status=status.HTTP_204_NO_CONTENT)

        serializer = ViewSubscriptionSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        data = {
            'user': request.user.id,
            'author': id,
        }
        serializer = SubscriptionSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        author = get_object_or_404(User, id=id)
        subscribtion = get_object_or_404(Subscription, user=request.user, author=author)
        subscribtion.delete()
        return Response({'detail': 'Отписка'}, status=status.HTTP_204_NO_CONTENT)


class FavoriteView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request, id):
        data = {
            'user': request.user.id,
            'author': id,
        }

        if Favorite.objects.filter(user=request.user, recipe__id=id).exists():
            return Response({'detail': 'Уже в избранном.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = FavoriteSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        favorite = get_object_or_404(Favorite, user=request.user, recipe=recipe)
        favorite.delete()
        return Response({'detail': 'Убрали из избранного'}, status=status.HTTP_204_NO_CONTENT)


class ShoppingCartView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request, id):
        data = {
            'user': request.user.id,
            'recipe': id
        }
        recipe = get_object_or_404(Recipe, id=id)

        if ShoppingCart.objects.filter(user=request.user, recipe=recipe).exists():
            return Response({'detail': 'Уже в корзине.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ShoppingCartSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        shopping_cart_stuff = get_object_or_404(ShoppingCart, user=request.user, recipe=recipe)
        shopping_cart_stuff.delete()

        return Response({'detail': 'Рецепт убран из корзины.'}, status=status.HTTP_204_NO_CONTENT)


def download_shopping_cart():
    pass
