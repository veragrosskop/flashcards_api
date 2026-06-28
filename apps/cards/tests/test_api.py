import pytest
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from apps.cards.models import Card, LanguageChoice
from apps.cards.tests.conftest import card


@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_create_card(api_client):
    payload = {
        "native": "Cat",
        "foreign": "Gatto",
        "native_language": LanguageChoice.ENGLISH,
        "foreign_language": LanguageChoice.ITALIAN,
    }

    response = api_client.post("/api/cards/", payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert Card.objects.count() == 1

    card = Card.objects.first()
    assert card.native == "Cat"
    assert card.foreign == "Gatto"
    assert card.native_language == LanguageChoice.ENGLISH
    assert card.foreign_language == LanguageChoice.ITALIAN


def test_get_cards_list(api_client, card):
    response = api_client.get("/api/cards/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == card.id
    assert response.data[0]["native"] == "House"
    assert response.data[0]["foreign"] == "Huis"


def test_get_card_detail(api_client, card):
    response = api_client.get(f"/api/cards/{card.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == card.id
    assert response.data["native"] == "House"
    assert response.data["foreign"] == "Huis"
    assert response.data["native_language"] == LanguageChoice.ENGLISH
    assert response.data["foreign_language"] == LanguageChoice.DUTCH


def test_update_card(api_client, card):
    payload = {
        "native": "House, Houses",
        "foreign": "Huis, Huizen",
        "native_language": LanguageChoice.ENGLISH,
        "foreign_language": LanguageChoice.DUTCH,
        "box_ntf": 4,
        "box_ftn": 2,
    }

    response = api_client.put(f"/api/cards/{card.id}/", payload, format="json")

    assert response.status_code == status.HTTP_200_OK

    card.refresh_from_db()
    assert card.native == "House, Houses"
    assert card.foreign == "Huis, Huizen"
    assert card.native_language == LanguageChoice.ENGLISH
    assert card.foreign_language == LanguageChoice.DUTCH
    assert card.box_ntf == 4
    assert card.box_ftn == 2


def test_partial_update_card(api_client, card):
    payload = {
        "native": "Door",
    }

    response = api_client.patch(f"/api/cards/{card.id}/", payload, format="json")

    assert response.status_code == status.HTTP_200_OK

    card.refresh_from_db()
    assert card.native == "Door"
    assert card.foreign == "Huis"


def test_delete_card(api_client, card):
    response = api_client.delete(f"/api/cards/{card.id}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Card.objects.count() == 0


@pytest.mark.django_db
def test_create_card_fails_when_native_and_foreign_language_are_same(api_client):
    payload = {
        "native": "House",
        "foreign": "Huis",
        "native_language": LanguageChoice.ENGLISH,
        "foreign_language": LanguageChoice.ENGLISH,
    }

    response = api_client.post("/api/cards/", payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Card.objects.count() == 0


@pytest.mark.django_db
def test_create_card_fails_when_required_fields_are_missing(api_client):
    payload = {
        "native": "House",
        "native_language": LanguageChoice.ENGLISH,
        "foreign_language": LanguageChoice.DUTCH,
    }

    response = api_client.post("/api/cards/", payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Card.objects.count() == 0


@pytest.mark.django_db
def test_get_card_detail_returns_404_for_unknown_card(api_client):
    response = api_client.get("/api/cards/999/")

    assert response.status_code == status.HTTP_404_NOT_FOUND