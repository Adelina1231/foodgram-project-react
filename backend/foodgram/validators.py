from django.core.validators import MinValueValidator, RegexValidator


def validate_slug(value):
    value = RegexValidator(regex=r'^[-a-zA-Z0-9_]+$',
                           message='Недопустимый символ в slug')
    return value


def validate_cooking_time(value):
    value = MinValueValidator(1, 'Минимум одна минута')
    return value


def validate_amount_ingredient(value):
    value = MinValueValidator(1, 'Минимум один ингредиент')
    return value
