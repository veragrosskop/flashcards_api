from django.test import TestCase
from apps.cards.models import (
    Card,
    DirectionChoice,
    LanguageChoice,
    CardReviewEvent,
    BOX_MIN,
)
from apps.cards.services.spaced_repitition import submit_card_guess


def test_submit_correct_guess_increases_box(card):
    submit_card_guess(
        card=card,
        direction=DirectionChoice.NATIVE_TO_FOREIGN,
        correct=True,
    )

    card.refresh_from_db()

    assert card.box_ntf == 2
    assert CardReviewEvent.objects.count() == 1


def test_submit_wrong_guess_resets_box(card):
    card.box_ntf = 3
    card.save()

    submit_card_guess(
        card=card,
        direction=DirectionChoice.NATIVE_TO_FOREIGN,
        correct=False,
    )

    card.refresh_from_db()

    assert card.box_ntf == BOX_MIN
