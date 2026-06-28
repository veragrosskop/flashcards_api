import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="test-password-123",
        first_name="Testuser",
        last_name="Example",
    )


@pytest.fixture
def authenticated_client(api_client, user):
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


def test_register_user(api_client):
    payload = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "secure-password-123",
    }

    response = api_client.post("/api/users/register/", payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.count() == 1

    user = User.objects.get(username="newuser")
    assert user.email == "newuser@example.com"
    assert user.check_password("secure-password-123")
    assert "password" not in response.data


def test_register_user_fails_when_password_is_too_short(api_client):
    payload = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "short",
    }

    response = api_client.post("/api/users/register/", payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert User.objects.count() == 0


def test_register_user_fails_when_username_already_exists(api_client, user):
    payload = {
        "username": user.username,
        "email": "different@example.com",
        "password": "secure-password-123",
    }

    response = api_client.post("/api/users/register/", payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert User.objects.count() == 1


def test_get_current_user(authenticated_client, user):
    response = authenticated_client.get("/api/users/me/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == user.id
    assert response.data["username"] == "testuser"
    assert response.data["email"] == "testuser@example.com"
    assert response.data["first_name"] == "Testuser"
    assert response.data["last_name"] == "Example"


def test_get_current_user_fails_when_not_authenticated(api_client):
    response = api_client.get("/api/users/me/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_patch_current_user(authenticated_client, user):
    payload = {
        "email": "updated@example.com",
        "first_name": "Updated",
        "last_name": "User",
    }

    response = authenticated_client.patch("/api/users/me/", payload, format="json")

    assert response.status_code == status.HTTP_200_OK

    user.refresh_from_db()
    assert user.email == "updated@example.com"
    assert user.first_name == "Updated"
    assert user.last_name == "User"


def test_patch_current_user_change_username(authenticated_client, user):
    payload = {
        "username": "changed-username",
        "email": "updated@example.com",
    }

    response = authenticated_client.patch("/api/users/me/", payload, format="json")

    assert response.status_code == status.HTTP_200_OK

    user.refresh_from_db()
    assert user.username == "changed-username"
    assert user.email == "updated@example.com"


def test_obtain_token_pair(api_client, user):
    payload = {
        "username": "testuser",
        "password": "test-password-123",
    }

    response = api_client.post("/api/users/token/", payload, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data


def test_obtain_token_pair_fails_with_invalid_credentials(api_client, user):
    payload = {
        "username": "testuser",
        "password": "wrong-password",
    }

    response = api_client.post("/api/users/token/", payload, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_token(api_client, user):
    refresh = RefreshToken.for_user(user)

    payload = {
        "refresh": str(refresh),
    }

    response = api_client.post("/api/users/token/refresh/", payload, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data


def test_register_user_hashes_password(api_client):
    payload = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "secure-password-123",
    }

    response = api_client.post("/api/users/register/", payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED

    user = User.objects.get(username="newuser")
    assert user.password != "secure-password-123"
    assert user.check_password("secure-password-123")
