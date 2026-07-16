from django.db import transaction

from apps.cards.models import Card, Deck


def create_deck(*, owner, name, parent=None, is_public=False):
    return Deck.objects.create(owner=owner, name=name, parent=parent, is_public=is_public)


def update_deck(deck: Deck, **fields):
    for attr, value in fields.items():
        setattr(deck, attr, value)
    deck.save()
    return deck


def add_card_to_deck(card, deck):
    """ "
    Adds a card to a deck. It will validate that the card languages are compatible with the deck.
    """
    existing_cards = deck.cards.all()

    if existing_cards.exists():
        existing_cards = deck.cards.all()

        if existing_cards.exists():
            if existing_cards.exclude(
                native_language=card.native_language,
                foreign_language=card.foreign_language,
            ).exists():
                raise ValueError("Language mismatch in deck")

    deck.cards.add(card)


def remove_card_from_deck(card, deck):
    deck.cards.remove(card)


@transaction.atomic
def add_cards_to_deck(cards, deck):
    for card in cards:
        add_card_to_deck(card, deck)


def remove_cards_from_deck(cards, deck):
    for card in cards:
        remove_card_from_deck(card, deck)


@transaction.atomic
def move_cards_between_decks(cards, source_deck, target_deck):
    for card in cards:
        remove_card_from_deck(card, source_deck)
        add_card_to_deck(card, target_deck)


@transaction.atomic
def copy_deck(deck: Deck, new_owner):
    new_deck = Deck.objects.create(
        owner=new_owner, name=deck.name, parent=deck.parent, is_public=False
    )
    for card in deck.cards.all():
        new_card = Card.objects.create(
            owner=new_owner,
            native=card.native,
            foreign=card.foreign,
            native_language=card.native_language,
            foreign_language=card.foreign_language,
        )
        new_deck.cards.add(new_card)
    return new_deck
