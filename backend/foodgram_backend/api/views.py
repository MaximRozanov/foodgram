from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrAdminOrReadOnly
from api.serializers import TagSerializer, IngredientSerializer, RecipeSerializer, CreateRecipeSerializer, \
    SubscriptionSerializer, ViewSubscriptionSerializer, FavoriteSerializer, ShoppingCartSerializer, AvatarSerializer
from recipes.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart
from users.models import Subscription

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny, ]
    pagination_class = None
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny, ]
    pagination_class = None
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = [IngredientFilter, ]
    search_fields = ['^name', ]


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthorOrAdminOrReadOnly, ]  # Добавить только ток авторизованный пермишн
    pagination_class = CustomPagination
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return CreateRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context


class AvatarView(APIView):
    permission_classes = [IsAuthenticated, ]

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = AvatarSerializer(instance=user, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        user = request.user
        if user.avatar:
            user.avatar.delete()
            user.avatar = None
            user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ViewSubscriptionView(APIView):
    permission_classes = [IsAuthenticated, ]
    pagination_class = CustomPagination

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
    permission_classes = [IsAuthenticated, ]

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
    pagination_class = CustomPagination

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
