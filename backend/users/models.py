from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        'Логин',
        max_length=settings.LEN_NAME_USER,
        unique=True,
    )
    email = models.EmailField(
        'Email',
        max_length=settings.LEN_EMAIL,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=settings.LEN_NAME_USER,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=settings.LEN_NAME_USER,
    )
    password = models.CharField(
        'Пароль',
        max_length=settings.LEN_PASSWORD
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return f'{self.username}, {self.email}'
