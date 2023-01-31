from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Создаем новую модель пользователя с дополнительный полем
    JSON, которое будет хранить баланс средств пользователя"""

    username = models.CharField('username', unique=True, max_length=30, default='')
    first_name = models.CharField('first_name', max_length=30, null=True, blank=True)
    last_name = models.CharField('last_name', max_length=30, null=True, blank=True)
    email = models.EmailField('email', null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    balance_of_funds=models.JSONField(dict, null=True, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def get_short_name(self):
        return self.username

    def natural_key(self):
        return self.username

    def __str__(self):
        return self.username


