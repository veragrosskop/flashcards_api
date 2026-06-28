from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField

from common.enums.language import LanguageChoice

class User(AbstractUser):
    email = models.EmailField(unique=True)

    native_languages = ArrayField(
        base_field=models.CharField(max_length=10, choices=LanguageChoice.choices),
        default=list,
        blank=True,
        )