import pytest
from rest_framework import status

from apps.cards.models import Card, Deck, HierarchyItem, HierarchyType, LanguageChoice
from apps.cards.tests.conftest import (
    another_user,
    api_client,
    authenticated_client,
    card,
    deck,
    hierarchy_item,
    public_deck,
    user,
)


@pytest.mark.django_db
def test_create_deck(authenticated_client, user):
    response = authenticated_client.post(
        "/api/decks/", {"name": "Animals"}, format="json"
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert Deck.objects.count() == 1
    assert Deck.objects.first().owner == user


def test_get_decks_list_only_returns_own_and_public_decks(
    authenticated_client, user, another_user, deck
):
    Deck.objects.create(owner=another_user, name="Private of another user")

    response = authenticated_client.get("/api/decks/")

    assert response.status_code == status.HTTP_200_OK
    ids = [d["id"] for d in response.data]
    assert deck.id in ids
    assert len(ids) == 1


def test_get_deck_detail_returns_404_for_another_users_private_deck(
    authenticated_client, another_user
):
    other_deck = Deck.objects.create(owner=another_user, name="Private")

    response = authenticated_client.get(f"/api/decks/{other_deck.id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_deck_detail_returns_404_for_unknown_deck(authenticated_client):
    response = authenticated_client.get("/api/decks/999/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_create_deck_fails_when_not_authenticated(api_client):
    response = api_client.post("/api/decks/", {"name": "Animals"}, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Deck.objects.count() == 0


def test_update_deck(authenticated_client, deck):
    response = authenticated_client.put(
        f"/api/decks/{deck.id}/", {"name": "Renamed"}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK
    deck.refresh_from_db()
    assert deck.name == "Renamed"


def test_partial_update_deck(authenticated_client, deck):
    response = authenticated_client.patch(
        f"/api/decks/{deck.id}/", {"is_public": True}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK
    deck.refresh_from_db()
    assert deck.is_public is True


def test_delete_deck(authenticated_client, deck):
    response = authenticated_client.delete(f"/api/decks/{deck.id}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Deck.objects.count() == 0


def test_create_deck_fails_on_duplicate_name_parent_for_same_owner(
    authenticated_client, deck
):
    response = authenticated_client.post(
        "/api/decks/", {"name": deck.name}, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Deck.objects.count() == 1


def test_create_deck_succeeds_with_same_name_for_different_owner(
    authenticated_client, another_user
):
    Deck.objects.create(owner=another_user, name="Animals")

    response = authenticated_client.post(
        "/api/decks/", {"name": "Animals"}, format="json"
    )

    assert response.status_code == status.HTTP_201_CREATED


def test_create_deck_with_parent_hierarchy_item(authenticated_client, hierarchy_item):
    response = authenticated_client.post(
        "/api/decks/",
        {"name": "Chapter Deck", "parent": hierarchy_item.id},
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert Deck.objects.get().parent_id == hierarchy_item.id


def test_create_deck_rejects_parent_owned_by_another_user(
    authenticated_client, another_user
):
    other_item = HierarchyItem.objects.create(
        owner=another_user, name="Textbook", type=HierarchyType.SOURCE
    )

    response = authenticated_client.post(
        "/api/decks/", {"name": "Deck", "parent": other_item.id}, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Deck.objects.count() == 0


def test_public_deck_visible_to_other_users(authenticated_client, public_deck):
    list_response = authenticated_client.get("/api/decks/")
    detail_response = authenticated_client.get(f"/api/decks/{public_deck.id}/")

    assert list_response.status_code == status.HTTP_200_OK
    assert public_deck.id in [d["id"] for d in list_response.data]
    assert detail_response.status_code == status.HTTP_200_OK


def test_public_deck_not_editable_by_non_owner(authenticated_client, public_deck):
    patch_response = authenticated_client.patch(
        f"/api/decks/{public_deck.id}/", {"name": "Hijacked"}, format="json"
    )
    delete_response = authenticated_client.delete(f"/api/decks/{public_deck.id}/")

    assert patch_response.status_code == status.HTTP_403_FORBIDDEN
    assert delete_response.status_code == status.HTTP_403_FORBIDDEN


def test_deck_cards_action_owner_sees_full_data(authenticated_client, deck, user):
    owned_card = Card.objects.create(
        owner=user,
        native="Dog",
        foreign="Hond",
        native_language=LanguageChoice.ENGLISH,
        foreign_language=LanguageChoice.DUTCH,
    )
    deck.cards.add(owned_card)

    response = authenticated_client.get(f"/api/decks/{deck.id}/cards/")

    assert response.status_code == status.HTTP_200_OK
    assert "box_ntf" in response.data[0]
    assert "owner" in response.data[0]


def test_deck_cards_action_non_owner_sees_public_fields_for_public_deck(
    authenticated_client, public_deck
):
    response = authenticated_client.get(f"/api/decks/{public_deck.id}/cards/")

    assert response.status_code == status.HTTP_200_OK
    assert "box_ntf" not in response.data[0]
    assert "owner" not in response.data[0]
    assert response.data[0]["native"] == "Dog"


def test_deck_cards_action_non_owner_private_deck_returns_404(
    authenticated_client, another_user
):
    other_deck = Deck.objects.create(owner=another_user, name="Private")

    response = authenticated_client.get(f"/api/decks/{other_deck.id}/cards/")

    # not visible to the requester at all (get_queryset excludes it), so 404 not 403
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_add_single_card_to_deck(authenticated_client, deck, card):
    response = authenticated_client.post(
        f"/api/decks/{deck.id}/cards/add/", {"card_ids": [card.id]}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK
    assert deck.cards.count() == 1


def test_add_multiple_cards_to_deck(authenticated_client, deck, user):
    card_one = Card.objects.create(
        owner=user,
        native="Dog",
        foreign="Hond",
        native_language=LanguageChoice.ENGLISH,
        foreign_language=LanguageChoice.DUTCH,
    )
    card_two = Card.objects.create(
        owner=user,
        native="Cat",
        foreign="Kat",
        native_language=LanguageChoice.ENGLISH,
        foreign_language=LanguageChoice.DUTCH,
    )

    response = authenticated_client.post(
        f"/api/decks/{deck.id}/cards/add/",
        {"card_ids": [card_one.id, card_two.id]},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert deck.cards.count() == 2


def test_add_another_users_card_to_deck_fails(
    authenticated_client, deck, another_user
):
    others_card = Card.objects.create(
        owner=another_user,
        native="Dog",
        foreign="Hond",
        native_language=LanguageChoice.ENGLISH,
        foreign_language=LanguageChoice.DUTCH,
    )

    response = authenticated_client.post(
        f"/api/decks/{deck.id}/cards/add/",
        {"card_ids": [others_card.id]},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert deck.cards.count() == 0


def test_add_cards_with_language_mismatch_rolls_back(
    authenticated_client, deck, user, card
):
    deck.cards.add(card)  # English -> Dutch
    mismatched_card = Card.objects.create(
        owner=user,
        native="Cat",
        foreign="Gatto",
        native_language=LanguageChoice.ENGLISH,
        foreign_language=LanguageChoice.ITALIAN,
    )
    compatible_card = Card.objects.create(
        owner=user,
        native="Bird",
        foreign="Vogel",
        native_language=LanguageChoice.ENGLISH,
        foreign_language=LanguageChoice.DUTCH,
    )

    response = authenticated_client.post(
        f"/api/decks/{deck.id}/cards/add/",
        {"card_ids": [compatible_card.id, mismatched_card.id]},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert deck.cards.count() == 1  # only the original card, add was rolled back


def test_add_cards_to_deck_by_non_owner_returns_404(authenticated_client, another_user):
    other_deck = Deck.objects.create(owner=another_user, name="Private")
    other_card = Card.objects.create(
        owner=another_user,
        native="Dog",
        foreign="Hond",
        native_language=LanguageChoice.ENGLISH,
        foreign_language=LanguageChoice.DUTCH,
    )

    response = authenticated_client.post(
        f"/api/decks/{other_deck.id}/cards/add/",
        {"card_ids": [other_card.id]},
        format="json",
    )

    # not visible to the requester at all (get_queryset excludes it), so 404 not 403
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_remove_cards_from_deck(authenticated_client, deck, card):
    deck.cards.add(card)

    response = authenticated_client.post(
        f"/api/decks/{deck.id}/cards/remove/", {"card_ids": [card.id]}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK
    assert deck.cards.count() == 0


def test_remove_cards_from_deck_by_non_owner_returns_404(
    authenticated_client, another_user
):
    other_deck = Deck.objects.create(owner=another_user, name="Private")
    other_card = Card.objects.create(
        owner=another_user,
        native="Dog",
        foreign="Hond",
        native_language=LanguageChoice.ENGLISH,
        foreign_language=LanguageChoice.DUTCH,
    )
    other_deck.cards.add(other_card)

    response = authenticated_client.post(
        f"/api/decks/{other_deck.id}/cards/remove/",
        {"card_ids": [other_card.id]},
        format="json",
    )

    # not visible to the requester at all (get_queryset excludes it), so 404 not 403
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_move_cards_between_own_decks(authenticated_client, deck, card, user):
    target = Deck.objects.create(owner=user, name="Target")
    deck.cards.add(card)

    response = authenticated_client.post(
        f"/api/decks/{deck.id}/cards/move/",
        {"card_ids": [card.id], "target_deck_id": target.id},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert deck.cards.count() == 0
    assert target.cards.count() == 1


def test_move_cards_to_deck_not_owned_by_requester_returns_404(
    authenticated_client, deck, card, another_user
):
    other_deck = Deck.objects.create(owner=another_user, name="Not mine")
    deck.cards.add(card)

    response = authenticated_client.post(
        f"/api/decks/{deck.id}/cards/move/",
        {"card_ids": [card.id], "target_deck_id": other_deck.id},
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert deck.cards.count() == 1  # untouched


def test_move_cards_language_mismatch_rolls_back(authenticated_client, deck, card, user):
    deck.cards.add(card)  # English -> Dutch
    target = Deck.objects.create(owner=user, name="Target")
    mismatched_card = Card.objects.create(
        owner=user,
        native="Cat",
        foreign="Gatto",
        native_language=LanguageChoice.ENGLISH,
        foreign_language=LanguageChoice.ITALIAN,
    )
    target.cards.add(mismatched_card)

    response = authenticated_client.post(
        f"/api/decks/{deck.id}/cards/move/",
        {"card_ids": [card.id], "target_deck_id": target.id},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert deck.cards.count() == 1  # card stays in source, move rolled back
    assert target.cards.count() == 1  # only the pre-existing mismatched card


def test_copy_public_deck_creates_independent_copy(authenticated_client, public_deck, user):
    original_card = public_deck.cards.get()

    response = authenticated_client.post(f"/api/decks/{public_deck.id}/copy/")

    assert response.status_code == status.HTTP_201_CREATED
    new_deck = Deck.objects.get(pk=response.data["id"])
    assert new_deck.owner == user
    assert new_deck.cards.count() == 1

    copied_card = new_deck.cards.get()
    assert copied_card.id != original_card.id
    assert copied_card.owner == user
    assert copied_card.native == original_card.native
    assert copied_card.box_ntf == 1
    assert copied_card.box_ftn == 1

    # original untouched
    original_card.refresh_from_db()
    assert public_deck.cards.count() == 1


def test_copy_private_deck_not_owned_returns_404(authenticated_client, another_user):
    private_deck = Deck.objects.create(owner=another_user, name="Private")

    response = authenticated_client.post(f"/api/decks/{private_deck.id}/copy/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
