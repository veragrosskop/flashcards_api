from .base import *

DEBUG = True

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True
