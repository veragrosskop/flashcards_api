import pytest
from apps.cards.models import Card, LanguageChoice


@pytest.fixture
def card(db):
    return Card.objects.create(
        native="House",
        foreign="Huis",
        native_language=LanguageChoice.ENGLISH,
        foreign_language=LanguageChoice.DUTCH,
    )