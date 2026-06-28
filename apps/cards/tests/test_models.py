from apps.cards.models import  DirectionChoice, LanguageChoice


def test_get_text_ntf_ftn(card):
    ntf_card = card.get_text(DirectionChoice.NATIVE_TO_FOREIGN)
    ftn_card = card.get_text(DirectionChoice.FOREIGN_TO_NATIVE)

    assert ntf_card.get("front") == "House"
    assert ntf_card.get("back")== "Huis"
    assert ftn_card.get("front") == "Huis"
    assert ftn_card.get("back") == "House"

def test_language_pair_support(card):
    assert True == card.supports_language_pair(
            LanguageChoice.DUTCH,
            LanguageChoice.ENGLISH
        )