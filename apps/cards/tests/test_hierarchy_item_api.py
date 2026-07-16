import pytest
from rest_framework import status

from apps.cards.models import HierarchyItem, HierarchyType
from apps.cards.tests.conftest import (
    another_user,
    api_client,
    authenticated_client,
    hierarchy_item,
    user,
)


@pytest.mark.django_db
def test_create_hierarchy_item(authenticated_client, user):
    response = authenticated_client.post(
        "/api/hierarchy-items/",
        {"name": "Textbook", "type": HierarchyType.SOURCE},
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert HierarchyItem.objects.count() == 1
    assert HierarchyItem.objects.first().owner == user


@pytest.mark.django_db
def test_create_hierarchy_item_fails_when_not_authenticated(api_client):
    response = api_client.post(
        "/api/hierarchy-items/",
        {"name": "Textbook", "type": HierarchyType.SOURCE},
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert HierarchyItem.objects.count() == 0


def test_list_hierarchy_items_only_returns_authenticated_users_items(
    authenticated_client, another_user, hierarchy_item
):
    HierarchyItem.objects.create(
        owner=another_user, name="Other's Textbook", type=HierarchyType.SOURCE
    )

    response = authenticated_client.get("/api/hierarchy-items/")

    assert response.status_code == status.HTTP_200_OK
    ids = [item["id"] for item in response.data]
    assert hierarchy_item.id in ids
    assert len(ids) == 1


def test_get_hierarchy_item_detail_returns_404_for_another_users_item(
    authenticated_client, another_user
):
    other_item = HierarchyItem.objects.create(
        owner=another_user, name="Other's Textbook", type=HierarchyType.SOURCE
    )

    response = authenticated_client.get(f"/api/hierarchy-items/{other_item.id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_hierarchy_item_detail(authenticated_client, hierarchy_item):
    response = authenticated_client.get(f"/api/hierarchy-items/{hierarchy_item.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == hierarchy_item.id


def test_update_hierarchy_item(authenticated_client, hierarchy_item):
    response = authenticated_client.put(
        f"/api/hierarchy-items/{hierarchy_item.id}/",
        {"name": "Renamed", "type": HierarchyType.VOLUME},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    hierarchy_item.refresh_from_db()
    assert hierarchy_item.name == "Renamed"
    assert hierarchy_item.type == HierarchyType.VOLUME


def test_partial_update_hierarchy_item(authenticated_client, hierarchy_item):
    response = authenticated_client.patch(
        f"/api/hierarchy-items/{hierarchy_item.id}/",
        {"name": "Renamed"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    hierarchy_item.refresh_from_db()
    assert hierarchy_item.name == "Renamed"


def test_delete_hierarchy_item(authenticated_client, hierarchy_item):
    response = authenticated_client.delete(f"/api/hierarchy-items/{hierarchy_item.id}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert HierarchyItem.objects.count() == 0


def test_create_hierarchy_item_with_parent(authenticated_client, hierarchy_item):
    response = authenticated_client.post(
        "/api/hierarchy-items/",
        {
            "name": "Chapter 1",
            "type": HierarchyType.CHAPTER,
            "parent": hierarchy_item.id,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    new_item = HierarchyItem.objects.get(name="Chapter 1")
    assert new_item.parent_id == hierarchy_item.id


def test_create_hierarchy_item_rejects_parent_owned_by_another_user(
    authenticated_client, another_user
):
    other_item = HierarchyItem.objects.create(
        owner=another_user, name="Other's Textbook", type=HierarchyType.SOURCE
    )

    response = authenticated_client.post(
        "/api/hierarchy-items/",
        {"name": "Chapter 1", "type": HierarchyType.CHAPTER, "parent": other_item.id},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert HierarchyItem.objects.count() == 1  # only other_item


def test_update_hierarchy_item_rejects_self_as_own_ancestor(
    authenticated_client, hierarchy_item
):
    response = authenticated_client.patch(
        f"/api/hierarchy-items/{hierarchy_item.id}/",
        {"parent": hierarchy_item.id},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_update_hierarchy_item_rejects_indirect_ancestor_cycle(
    authenticated_client, user, hierarchy_item
):
    child = HierarchyItem.objects.create(
        owner=user, name="Chapter", type=HierarchyType.CHAPTER, parent=hierarchy_item
    )
    grandchild = HierarchyItem.objects.create(
        owner=user, name="Section", type=HierarchyType.SECTION, parent=child
    )

    response = authenticated_client.patch(
        f"/api/hierarchy-items/{hierarchy_item.id}/",
        {"parent": grandchild.id},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
