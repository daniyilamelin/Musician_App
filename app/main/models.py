from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    telegram_id = models.BigIntegerField(null=True, blank=True, verbose_name = 'Telegram ID')
    is_verified = models.BooleanField(blank=True, null=True, default=False, verbose_name = 'Верифікація')
