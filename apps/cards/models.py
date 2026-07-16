from typing import Dict

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from common.enums.language import LanguageChoice

BOX_MAX = 5
BOX_MIN = 1
BOXES = range(BOX_MIN, BOX_MAX + 1)


class HierarchyType(models.TextChoices):
    """Similar to an Enumerator this defines the type of Hierarchy of a Source."""

    SOURCE = "SOURCE", "Source"
    VOLUME = "VOLUME", "Volume"
    UNIT = "UNIT", "Unit"
    CHAPTER = "CHAPTER", "Chapter"
    SECTION = "SECTION", "Section"
    SUBSECTION = "SUBSECTION", "Subsection"


class HierarchyItem(models.Model):
    """A class which can be defined as any of the HierarchyTypes."""

    # TODO! enforce hierarchy of HierarchyTypes -> add validation
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hierarchy_items",
    )
    name = models.CharField(max_length=255)
    type = models.CharField(
        max_length=20, choices=HierarchyType.choices, default=HierarchyType.SOURCE
    )
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="children"
    )

    def __str__(self):
        return f"{self.name} ({self.type})"


class Deck(models.Model):
    """A deck holds cards and can belong to any Hierarchy level."""

    name = models.CharField(max_length=200)
    parent = models.ForeignKey(
        HierarchyItem,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="decks",
    )
    cards = models.ManyToManyField("Card", related_name="decks", blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="decks",
    )
    is_public = models.BooleanField(default=False)

    # shared_with = models.ManyToManyField(CustomUser, related_name='shared_decks', blank=True)

    def __str__(self):
        return f"{self.name} (Deck under {self.parent})"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "name", "parent"], name="unique_deck_per_owner_parent"
            )
        ]


class DirectionChoice(models.TextChoices):
    """
    Similar to an Enumerator this defines the direction of a flashcard.
    This could be native to foreign or the other way around.
    """

    NATIVE_TO_FOREIGN = "NTF", "Native to Foreign"
    FOREIGN_TO_NATIVE = "FTN", "Foreign to Native"


class Card(models.Model):

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cards",
    )

    # card content
    native = models.CharField(max_length=100)
    foreign = models.CharField(max_length=100)

    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    native_language = models.CharField(
        max_length=3, choices=LanguageChoice.choices, default=LanguageChoice.ENGLISH
    )
    foreign_language = models.CharField(max_length=3, choices=LanguageChoice.choices)

    # Track progress boxes separately per direction
    box_ntf = models.IntegerField(choices=zip(BOXES, BOXES), default=BOXES[0])
    box_ftn = models.IntegerField(choices=zip(BOXES, BOXES), default=BOXES[0])

    date_created = models.DateTimeField(auto_now_add=True)

    # deck = models.ForeignKey('decks.Deck', on_delete=models.CASCADE, related_name='cards')

    def __str__(self):
        return f"{self.native} -> {self.foreign}"

    def get_text(self, direction: DirectionChoice) -> Dict[str, str]:
        """
        Dynamically return the card text in the correct direction (native, foreign) or (foreign, native)
        """
        if direction == DirectionChoice.NATIVE_TO_FOREIGN:
            return {"front": self.native, "back": self.foreign}
        elif direction == DirectionChoice.FOREIGN_TO_NATIVE:
            return {"front": self.foreign, "back": self.native}
        else:
            raise ValueError(f"Could not find direction: {direction}.")

    # TODO! Not very efficient, but works for now, validate language pair later
    def supports_language_pair(
        self, lang1: LanguageChoice, lang2: LanguageChoice
    ) -> bool:
        return (self.native_language == lang1 and self.foreign_language == lang2) or (
            self.native_language == lang2 and self.foreign_language == lang1
        )


class CardReviewEvent(models.Model):
    class Result(models.TextChoices):
        CORRECT = "CORRECT", "Correct"
        WRONG = "WRONG", "Wrong"

    card = models.ForeignKey(
        "Card",
        on_delete=models.CASCADE,
        related_name="review_events",
    )

    direction = models.CharField(
        max_length=3,
        choices=DirectionChoice.choices,
    )

    result = models.CharField(
        max_length=10,
        choices=Result.choices,
    )

    new_box = models.IntegerField(choices=zip(BOXES, BOXES))

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["card", "created_at"]),
        ]

    def __str__(self):
        return f"{self.card} | {self.direction} | {self.result}"
