# Flashcards API

A Django REST Framework API for managing flashcards, decks, users, authentication, and spaced-repetition learning workflows.

This project is structured as a modular Django backend with separate applications for cards and users. It is designed to support authenticated users, user-owned flashcards/decks, and RESTful API access for frontend clients or mobile applications.

---

## 📒 Features

- User registration and authentication
- JWT-based API authentication
- Flashcard CRUD operations
- Deck and card organization
- Language-pair support for flashcards
- Spaced-repetition service layer
- Django REST Framework API endpoints
- Pytest-based test suite
- Environment-based configuration
- PostgreSQL-ready database configuration

---

## 🏗️ Tech Stack

- Python 3.14
- Django
- Django REST Framework
- Simple JWT authentication
- PostgreSQL
- pytest
- virtualenv

---

## 📌 Getting Started

### 1. Clone the repository
````console
bash git clone <repository-url> cd flashcards_api
````
---

### 2. Create and activate a virtual environment

On macOS/Linux:
````bash
python -m venv .venv source .venv/bin/activate
````
On Windows PowerShell:
````powershell
python -m venv .venv .venv\Scripts\Activate.ps1
````

---

### 3. Install dependencies
````bash 
pip install -r requirements.txt
````

---

## 📡 Running the Development Server
```bash
python manage.py runserver
```
The API will be available at:
```text
http://127.0.0.1:8000/
```
---

## 📚 API Overview

### 👤 Users

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/users/register/` | Register a new user | No |
| `POST` | `/api/users/token/` | Obtain JWT token pair | No |
| `POST` | `/api/users/token/refresh/` | Refresh access token | No |
| `POST` | `/api/users/token/blacklist/` | Blacklist refresh token | Yes |
| `GET` | `/api/users/me/` | Get current authenticated user | Yes |
| `PATCH` | `/api/users/me/` | Update current authenticated user | Yes |

### ✉️Cards

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/cards/` | List authenticated user's cards | Yes |
| `POST` | `/api/cards/` | Create a card | Yes |
| `GET` | `/api/cards/{id}/` | Retrieve a card | Yes |
| `PUT` | `/api/cards/{id}/` | Replace a card | Yes |
| `PATCH` | `/api/cards/{id}/` | Partially update a card | Yes |
| `DELETE` | `/api/cards/{id}/` | Delete a card | Yes |

### 🗂️ Decks

Decks are owned by a single user. Setting `is_public: true` lets other users browse the deck's cards (content only, no progress stats) and copy it into their own account.

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/decks/` | List your decks, plus any public decks | Yes |
| `POST` | `/api/decks/` | Create a deck | Yes |
| `GET` | `/api/decks/{id}/` | Retrieve a deck you own, or any public deck | Yes |
| `PUT` | `/api/decks/{id}/` | Replace a deck you own | Yes |
| `PATCH` | `/api/decks/{id}/` | Partially update a deck you own | Yes |
| `DELETE` | `/api/decks/{id}/` | Delete a deck you own | Yes |
| `GET` | `/api/decks/{id}/cards/` | List the deck's cards (full data if you own it, public-safe fields otherwise) | Yes |
| `POST` | `/api/decks/{id}/cards/add/` | Add one or more of your cards to a deck you own | Yes |
| `POST` | `/api/decks/{id}/cards/remove/` | Remove one or more cards from a deck you own | Yes |
| `POST` | `/api/decks/{id}/cards/move/` | Move one or more cards to another deck you own | Yes |
| `POST` | `/api/decks/{id}/copy/` | Copy a public (or your own) deck, including independent copies of its cards | Yes |

### 🧩 Hierarchy Items

Hierarchy items are owned by a single user and let you organize your own decks under resources like Textbook → Chapter → Unit.

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/hierarchy-items/` | List your hierarchy items | Yes |
| `POST` | `/api/hierarchy-items/` | Create a hierarchy item | Yes |
| `GET` | `/api/hierarchy-items/{id}/` | Retrieve a hierarchy item you own | Yes |
| `PUT` | `/api/hierarchy-items/{id}/` | Replace a hierarchy item you own | Yes |
| `PATCH` | `/api/hierarchy-items/{id}/` | Partially update a hierarchy item you own | Yes |
| `DELETE` | `/api/hierarchy-items/{id}/` | Delete a hierarchy item you own | Yes |

Full interactive documentation (Swagger UI / ReDoc) is available at `/docs/` and `/redoc/`.

---

## Example Card Payload
```json
{
  "native": "House",
  "foreign": "Huis",
  "native_language": "EN",
  "foreign_language": "NL"
}
```
Optional spaced-repetition box fields may also be included:
```json
{
  "box_ntf": 1,
  "box_ftn": 1
}
```
---
## 📇 Project Structure
```text
flashcards_api/ 
├── apps/ 
│ ├── cards/ 
│ │ ├── api/ 
│ │ │ ├── serializers.py 
│ │ │ └── views.py 
│ │ ├── services/ 
│ │ │ ├── card_services.py 
│ │ │ ├── deck_services.py 
│ │ │ └── spaced_repitition.py 
│ │ ├── tests/ 
│ │ │ ├── conftest.py 
│ │ │ ├── test_api.py 
│ │ │ ├── test_models.py 
│ │ │ └── test_services.py 
│ │ ├── models.py 
│ │ └── urls.py 
│ │
│ ├── users/ 
│ │ ├── api/ 
│ │ ├── serializers.py 
│ │ └── views.py 
│ ├── services/ 
│ ├── tests/ 
│ │ ├── test_api.py 
│ │ └── test_services.py 
│ ├── models.py 
│ └── urls.py 
│
├── common/ 
│ ├── enums/ 
│ ├── constants.py 
│ ├── exceptions.py 
│ └── mixins.py 
│
├── config/ 
│ ├── settings/ 
│ │ ├── base.py 
│ │ ├── dev.py 
│ │ ├── prod.py 
│ │ └── test.py 
│ ├── urls.py 
│ ├── asgi.py 
│ └── wsgi.py 
│
├── tests/ 
├── manage.py 
├── pytest.ini 
├── requirements.txt 
└── README.md
```
---

## 💻 License

This project is currently licensed under the MIT License. 


