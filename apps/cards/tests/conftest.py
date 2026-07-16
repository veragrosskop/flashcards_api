import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.cards.models import Card, Deck, HierarchyItem, HierarchyType, LanguageChoice

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


@pytest.fixture
def hierarchy_item(db, user):
    return HierarchyItem.objects.create(owner=user, name="Duolingo", type=HierarchyType.SOURCE)


@pytest.fixture
def deck(db, user):
    return Deck.objects.create(owner=user, name="Animals", parent=None)


@pytest.fixture
def public_deck(db, another_user):
    deck = Deck.objects.create(owner=another_user, name="Shared Deck", is_public=True)
    card = Card.objects.create(
        owner=another_user,
        native="Dog",
        foreign="Hond",
        native_language=LanguageChoice.ENGLISH,
        foreign_language=LanguageChoice.DUTCH,
    )
    deck.cards.add(card)
    return deck
