from django.contrib import admin

from .models import (Carts, Favorite, Ingredient, Recipe, RecipeIngredient,
                     Subscribe, Tag)


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name', 'slug')
    empy_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empy_value_display = '-пусто-'


class RecipeIngredientAdmin(admin.TabularInline):
    model = RecipeIngredient
    autocomplete_fields = ('ingredient',)


class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientAdmin,)
    list_display = (
        'id', 'author', 'name', 'image', 'text', 'pub_date', 'in_favorite'
    )
    search_fields = ('author', 'name', 'tags')
    list_filter = ('author', 'name', 'tags')
    empy_value_display = '-пусто-'
    min_num = 1

    def in_favorite(self, obj):
        return obj.favorite.all().count()


class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')
    empy_value_display = '-пусто-'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    empy_value_display = '-пусто-'


class CartsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    empy_value_display = '-пусто-'


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Carts, CartsAdmin)
