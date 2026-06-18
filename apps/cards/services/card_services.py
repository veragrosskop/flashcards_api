from apps.cards.models import Card


def create_card(*, native, foreign, native_language, foreign_language):
    return Card.objects.create(
        native=native,
        foreign=foreign,
        native_language=native_language,
        foreign_language=foreign_language,
    )

def update_card(card: Card, **fields):
    for attr, value in fields.items():
        setattr(card, attr, value)

    card.save()
    return card