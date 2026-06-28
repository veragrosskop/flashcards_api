import pytest
from rest_framework import status

from apps.cards.models import Card, LanguageChoice
from apps.cards.tests.conftest import card, user, another_user, api_client, authenticated_client

@pytest.mark.django_db
def test_create_card(authenticated_client, user):
    payload = {
        "native": "Cat",
        "foreign": "Gatto",
        "native_language": LanguageChoice.ENGLISH,
        "foreign_language": LanguageChoice.ITALIAN,
    }

    response = authenticated_client.post("/api/cards/", payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert Card.objects.count() == 1

    card = Card.objects.first()
    assert card.owner == user
    assert card.native == "Cat"
    assert card.foreign == "Gatto"
    assert card.native_language == LanguageChoice.ENGLISH
    assert card.foreign_language == LanguageChoice.ITALIAN

def test_get_cards_list_only_returns_authenticated_users_cards(
    authenticated_client,
    user,
    another_user,
    card,
):
    Card.objects.create(
        owner=another_user,
        native="Cat",
        foreign="Kat",
        native_language=LanguageChoice.ENGLISH,
        foreign_language=LanguageChoice.DUTCH,
    )

    response = authenticated_client.get("/api/cards/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == card.id
    assert response.data[0]["native"] == "House"


def test_get_card_detail_returns_404_for_another_users_card(
    authenticated_client,
    another_user,
):
    other_card = Card.objects.create(
        owner=another_user,
        native="Cat",
        foreign="Kat",
        native_language=LanguageChoice.ENGLISH,
        foreign_language=LanguageChoice.DUTCH,
    )

    response = authenticated_client.get(f"/api/cards/{other_card.id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
def test_create_card_fails_when_not_authenticated(api_client):
    payload = {
        "native": "Cat",
        "foreign": "Gatto",
        "native_language": LanguageChoice.ENGLISH,
        "foreign_language": LanguageChoice.ITALIAN,
    }

    response = api_client.post("/api/cards/", payload, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Card.objects.count() == 0


def test_update_card(authenticated_client, card):
    payload = {
        "native": "House, Houses",
        "foreign": "Huis, Huizen",
        "native_language": LanguageChoice.ENGLISH,
        "foreign_language": LanguageChoice.DUTCH,
        "box_ntf": 4,
        "box_ftn": 2,
    }

    response = authenticated_client.put(f"/api/cards/{card.id}/", payload, format="json")

    assert response.status_code == status.HTTP_200_OK

    card.refresh_from_db()
    assert card.native == "House, Houses"
    assert card.foreign == "Huis, Huizen"
    assert card.native_language == LanguageChoice.ENGLISH
    assert card.foreign_language == LanguageChoice.DUTCH
    assert card.box_ntf == 4
    assert card.box_ftn == 2


def test_partial_update_card(authenticated_client, card):
    payload = {
        "native": "Door",
    }

    response = authenticated_client.patch(f"/api/cards/{card.id}/", payload, format="json")

    assert response.status_code == status.HTTP_200_OK

    card.refresh_from_db()
    assert card.native == "Door"
    assert card.foreign == "Huis"


def test_delete_card(authenticated_client, card):
    response = authenticated_client.delete(f"/api/cards/{card.id}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Card.objects.count() == 0


@pytest.mark.django_db
def test_create_card_fails_when_native_and_foreign_language_are_same(authenticated_client):
    payload = {
        "native": "House",
        "foreign": "Huis",
        "native_language": LanguageChoice.ENGLISH,
        "foreign_language": LanguageChoice.ENGLISH,
    }

    response = authenticated_client.post("/api/cards/", payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Card.objects.count() == 0


@pytest.mark.django_db
def test_create_card_fails_when_required_fields_are_missing(authenticated_client):
    payload = {
        "native": "House",
        "native_language": LanguageChoice.ENGLISH,
        "foreign_language": LanguageChoice.DUTCH,
    }

    response = authenticated_client.post("/api/cards/", payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Card.objects.count() == 0


@pytest.mark.django_db
def test_get_card_detail_returns_404_for_unknown_card(authenticated_client):
    response = authenticated_client.get("/api/cards/999/")

    assert response.status_code == status.HTTP_404_NOT_FOUND