from .base import *

DEBUG = False

# speeds up tests by switching to a faster hasher
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
