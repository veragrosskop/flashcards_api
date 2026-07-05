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
