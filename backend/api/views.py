from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.mixins import (CreateModelMixin, ListModelMixin,
                                   RetrieveModelMixin)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from users.models import User
from recipes.models import (Carts, Favorite, Ingredient, Recipe,
                            RecipeIngredient, Subscribe, Tag)
from .filters import IngredienFilter, RecipeFilter
from .pagination import CustomPaginator
from .permissions import IsAuthorOrReadOnly
from .serializers import (CartsSerializer, FavoriteSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer, SubscribeSerializer,
                          SubscribeUserSerializer, TagSerializer,
                          UserCreateSerializer, UserSerializer,
                          UserSetPasswordSerializer)


class CreateListRetrieveViewSet(CreateModelMixin,
                                ListModelMixin,
                                RetrieveModelMixin,
                                GenericViewSet):
    pass


class ListRetrieveViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    pass


class UserViewSet(CreateListRetrieveViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserSerializer
        return UserCreateSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        serialiser = self.get_serializer(request.user)
        return Response(serialiser.data, status=status.HTTP_200_OK)

    @action(detail=False,
            methods=['post'],
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = UserSetPasswordSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Пароль успешно изменен!'},
                        status=status.HTTP_204_NO_CONTENT)


class SubscribeViewSet(APIView):
    """Подписка/отписка на автора."""
    pagination_class = CustomPaginator

    def post(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        user = request.user
        serializer = SubscribeSerializer(
            data={'user': user.id, 'author': author.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        user = request.user
        subscription = Subscribe.objects.filter(user=user, author=author)
        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Вы не подписаны на пользователя!'},
            status=status.HTTP_400_BAD_REQUEST
        )


class SubscribeListViewSet(ListAPIView):
    serializer_class = SubscribeUserSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPaginator

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    filterset_class = IngredienFilter


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCreateSerializer

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'recipe_ingredients__ingredient', 'tags'
        ).all()
        return recipes

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        if request.method == 'POST':
            favorite = Favorite.objects.create(user=user, recipe=recipe)
            serializer = FavoriteSerializer(favorite,
                                            context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            favorite = Favorite.objects.filter(user=user, recipe=recipe)
            if favorite.exists():
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        """Добавление/ удаление рецептов из списка покупок."""
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        if request.method == 'POST':
            shopping_cart = Carts.objects.create(user=user, recipe=recipe)
            serializer = CartsSerializer(shopping_cart,
                                         context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            shopping_cart = Carts.objects.filter(user=user, recipe=recipe)
            if shopping_cart.exists():
                shopping_cart.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Скачивание файла со списком покупок."""
        ingredients = RecipeIngredient.objects.filter(
            recipe__carts__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        shopping_list = ['Список покупок:\n']
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['amount']
            shopping_list.append(f'{name} - {amount}, {unit}\n')
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_cart.txt"')
        return response
