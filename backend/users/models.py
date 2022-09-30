from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models


class User(AbstractUser):
    ADMIN = 'admin'
    USER = 'user'
    ROLES = (
        (ADMIN, 'admin'),
        (USER, 'user'),
    )

    id = models.BigAutoField(primary_key=True)

    username = models.CharField(
        verbose_name='Никнейм',
        help_text='Имя пользователя',
        max_length=150,
        unique=True,
        validators=[validators.RegexValidator(regex=r'^[\w.@+-]+\Z')]
    )
    email = models.EmailField(
        verbose_name='Email',
        help_text='Адрес электронной почты',
        max_length=254,
        unique=True
    )
    role = models.CharField(
        verbose_name='Статус пользователя',
        help_text='Права, предоставляемые пользователю',
        max_length=20,
        choices=ROLES,
        default='user'
    )
    first_name = models.CharField(
        verbose_name='Имя',
        help_text='Введите имя',
        max_length=150
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        help_text='Введите фамилию',
        max_length=150
    )

    is_subscribed = models.BooleanField(default=False)

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name'
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
