from apps.cards.models import DirectionChoice, CardReviewEvent, BOX_MIN
from apps.cards.models import BOX_MIN, BOXES
from django.db import transaction

@transaction.atomic
def submit_card_guess(card, direction:DirectionChoice, correct: bool) -> None:
    """
    Moves a card to a study box depending on whether it was solved.
    Solved? -> yes -> move a box over
    Solved? -> No -> move back to box 0

    :param direction:
    :param solved:
    :return:
    """

    if direction == DirectionChoice.NATIVE_TO_FOREIGN:
        curr_box = card.box_ntf
    elif direction == DirectionChoice.FOREIGN_TO_NATIVE:
        curr_box = card.box_ftn
    else:
        raise ValueError(f"Could not find direction: {direction}.")

    new_box = curr_box + 1 if correct else BOX_MIN

    # TODO! Add achievement stats here later like total_reviews, correct and wrongs etc

    if new_box in BOXES:
        if direction == DirectionChoice.NATIVE_TO_FOREIGN:
            card.box_ntf = new_box
        if direction == DirectionChoice.FOREIGN_TO_NATIVE:
            card.box_ftn = new_box

    card.save()

    #event Log
    CardReviewEvent.objects.create(
        card=card,
        direction=direction,
        result=CardReviewEvent.Result.CORRECT if correct else CardReviewEvent.Result.WRONG,
        new_box=new_box
    )