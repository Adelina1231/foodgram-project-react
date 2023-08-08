from django.conf import settings
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)


def validate_slug(value):
    value = RegexValidator(regex=r'^[-a-zA-Z0-9_]+$',
                           message='Недопустимый символ в slug')
    return value


def validate_cooking_time(value):
    validators = (MinValueValidator(settings.LEN_MIN_LIMIT,
                                    'Минимум одна минута'),
                  MaxValueValidator(settings.LEN_MAX_LIMIT,
                                    'Слишком долго ждать приготовления'))
    for validator in validators:
        validator(value)
    return value


def validate_amount_ingredient(value):
    validators = (MinValueValidator(settings.LEN_MIN_LIMIT,
                                    'Минимум один ингредиент'),
                  MaxValueValidator(settings.LEN_MAX_LIMIT,
                                    'Слишком много ингредиентов'))
    for validator in validators:
        validator(value)
    return value
