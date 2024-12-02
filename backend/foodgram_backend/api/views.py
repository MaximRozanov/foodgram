from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import redirect
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrAdminOrReadOnly
from api.serializers import (AvatarSerializer, CreateRecipeSerializer,
                             FavoriteSerializer, IngredientSerializer,
                             MyUserSerializer, RecipeSerializer,
                             ShoppingCartSerializer, SubscriptionSerializer,
                             TagSerializer, ViewSubscriptionSerializer)
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscription

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthorOrAdminOrReadOnly, ]
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
    permission_classes = [IsAuthorOrAdminOrReadOnly, ]
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

    def get_link(self, request, id=None):
        recipe = get_object_or_404(Recipe, pk=id)
        rev_link = reverse('short_url', args=[recipe.pk])
        return Response({'short-link': request.build_absolute_uri(rev_link)},
                        status=status.HTTP_200_OK, )


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
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        user = request.user
        queryset = User.objects.filter(subscriptions__user=user)
        paginator = self.pagination_class()

        page = paginator.paginate_queryset(queryset, request)
        if page is None:
            return Response([], status=status.HTTP_204_NO_CONTENT)

        serializer = ViewSubscriptionSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)


class SubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        author = get_object_or_404(User, id=id)
        if request.user.id == author.id:
            return Response(
                {'detail': 'Нельзя подписываться на себя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        data = {
            'user': request.user.id,
            'author': author.id,
        }
        serializer = SubscriptionSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        author = get_object_or_404(User, id=id)
        subscription = Subscription.objects.filter(
            user=request.user,
            author=author,
        ).first()
        if subscription is None:
            return Response(
                {'detail': 'Подписка нет насяльника.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(
            {'detail': 'Отписано'},
            status=status.HTTP_204_NO_CONTENT
        )


class FavoriteView(APIView):
    permission_classes = [IsAuthenticated, ]
    pagination_class = CustomPagination

    def post(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        if not Favorite.objects.filter(
                user=request.user, recipe__id=id).exists():
            serializer = FavoriteSerializer(
                data=data, context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        if Favorite.objects.filter(
                user=request.user, recipe=recipe).exists():
            Favorite.objects.filter(
                user=request.user,
                recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ShoppingCartView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request, id):
        data = {
            'user': request.user.id,
            'recipe': id
        }
        recipe = get_object_or_404(Recipe, id=id)
        if not ShoppingCart.objects.filter(
                user=request.user, recipe=recipe).exists():
            serializer = ShoppingCartSerializer(
                data=data, context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        if ShoppingCart.objects.filter(
                user=request.user, recipe=recipe).exists():
            ShoppingCart.objects.filter(
                user=request.user, recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def short_url(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    return redirect(f'/recipes/{recipe.pk}/')


@api_view(['GET'])
def download_shopping_cart(request):
    ingredients = RecipeIngredient.objects.filter(
        recipe__shopping_cart__user=request.user
    ).values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(amount=Sum('amount'))

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        'attachment; '
        'filename="shopping_list.pdf"'
    )

    p = canvas.Canvas(response, pagesize=letter)
    p.drawString(100, 750, "Cписок покупок:")

    y_position = 730
    for i in ingredients:
        ingredient_line = (
            f"{i['ingredient__name']} - "
            f"{i['amount']} {i['ingredient__measurement_unit']}"
        )
        p.drawString(100, y_position, ingredient_line)
        y_position -= 20
    p.showPage()
    p.save()
    return response


class UserViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def me(self, request):
        serializer = MyUserSerializer(request.user)
        return Response(serializer.data)
