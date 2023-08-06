from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet, SubscribeListViewSet,
                    SubscribeViewSet, TagViewSet, UserViewSet)

app_name = 'api'

v1_router = DefaultRouter()
v1_router.register('users', UserViewSet)
v1_router.register('tags', TagViewSet)
v1_router.register('ingredients', IngredientViewSet)
v1_router.register('recipes', RecipeViewSet)

urlpatterns = [
    path(
        'users/subscriptions/',
        SubscribeListViewSet.as_view(),
        name='subscriptions'
    ),
    path(
        'users/<int:user_id>/subscribe/',
        SubscribeViewSet.as_view(),
        name='subscribe'
    ),
    path('', include(v1_router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
