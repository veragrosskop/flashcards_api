import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.cards.models import Card, LanguageChoice

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="test-password-123",
    )


@pytest.fixture
def another_user(db):
    return User.objects.create_user(
        username="otheruser",
        email="otheruser@example.com",
        password="test-password-123",
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def card(db, user):
    return Card.objects.create(
        owner=user,
        native="House",
        foreign="Huis",
        native_language=LanguageChoice.ENGLISH,
        foreign_language=LanguageChoice.DUTCH,
    )
