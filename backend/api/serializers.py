from django.conf import settings
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Carts, Favorite, Ingredient, Recipe,
                            RecipeIngredient, Subscribe, Tag)
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed')
        model = User

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        return (user.is_authenticated
                and user.follower.filter(author=author).exists())


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email',
                  'first_name', 'last_name', 'password')

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    class Meta:
        model = User
        fields = ('current_password', 'new_password')

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data['current_password']):
            raise serializers.ValidationError(
                {'current_password': 'Неправильный пароль.'}
            )
        if (validated_data['current_password']
           == validated_data['new_password']):
            raise serializers.ValidationError(
                {'new_password': 'Новый пароль должен отличаться от текущего.'}
            )
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance


class RecipeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return RecipeShortSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        return (user.is_authenticated
                and user.follower.filter(author=author).exists())


class SubscribeSerializer(serializers.ModelSerializer):
    """Подписка/отписка на автора."""

    class Meta:
        model = Subscribe
        fields = '__all__'

    def validate(self, data):
        user = self.context.get('request').user
        author = data['author']
        if user == author:
            raise serializers.ValidationError(
                {'errors': 'Нельзя подписаться на самого себя!'}
            )
        if user.follower.filter(author=author).exists():
            raise serializers.ValidationError(
                {'errors': 'Вы уже подписаны на данного пользователя!'}
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return SubscribeUserSerializer(
            instance.author, context={'request': request}
        ).data


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientPostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if value < settings.LEN_MIN_LIMIT or value > settings.LEN_MAX_LIMIT:
            raise serializers.ValidationError(
                'Количество ингредиентов должно быть от 1 до 32000')
        return value


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = RecipeIngredient


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(many=True, read_only=True,
                                             source='recipe_ingredients')
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time')
        read_only_fields = ('is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, recipe):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.favorite_user.filter(recipe=recipe
                                                      ).exists())

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.carts.filter(recipe=recipe).exists())


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientPostSerializer(many=True,
                                           source='recipe_ingredients')
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField(use_url=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('name', 'cooking_time', 'text',
                  'tags', 'ingredients', 'image')

    def validate_cooking_time(self, value):
        if value < settings.LEN_MIN_LIMIT or value > settings.LEN_MAX_LIMIT:
            raise serializers.ValidationError(
                'Время приготовления должно быть от 1 мин до 32000 мин')
        return value

    def create_ingredients(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            **validated_data
        )
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        instance.tags.clear()
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_ingredients(ingredients, instance)
        return super().update(instance, validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        user = self.context.get('request').user
        recipe = self.context.get('recipe_id')
        if user.favorite_user.filter(recipe=recipe).exists():
            raise serializers.ValidationError(
                {'errors': 'Этот рецепт уже добавлен в избранное'})
        return data

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return RecipeShortSerializer(instance.recipe, context=context).data


class CartsSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Carts
        fields = ('user', 'recipe')

    def validate(self, data):
        user = self.context.get('request').user
        recipe = self.context.get('recipe_id')
        if user.carts.filter(recipe=recipe).exists():
            raise serializers.ValidationError(
                {'errors': 'Этот рецепт уже добавлен в список покупок'})
        return data
