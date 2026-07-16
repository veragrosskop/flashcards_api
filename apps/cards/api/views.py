from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from apps.cards.models import Card
from .serializers import CardSerializer
from apps.cards.services.card_services import create_card, update_card


@extend_schema_view(
    list=extend_schema(
        summary="List your cards",
        description="Returns all flashcards owned by the authenticated user.",
    ),
    retrieve=extend_schema(
        summary="Retrieve a card",
        description="Returns a single flashcard owned by the authenticated user.",
    ),
    create=extend_schema(
        summary="Create a card",
        description=(
            "Creates a new flashcard for the authenticated user. `native`/`foreign` "
            "are the two sides of the card; `native_language`/`foreign_language` must "
            "differ; `box_ntf`/`box_ftn` (1-5) track spaced-repetition progress "
            "independently for each review direction and default to 1."
        ),
    ),
    update=extend_schema(
        summary="Replace a card",
        description="Replaces all fields of an existing flashcard owned by the authenticated user.",
    ),
    partial_update=extend_schema(
        summary="Update a card",
        description="Updates one or more fields of an existing flashcard owned by the authenticated user.",
    ),
    destroy=extend_schema(
        summary="Delete a card",
        description="Deletes a flashcard owned by the authenticated user.",
    ),
)
class CardViewSet(viewsets.ModelViewSet):
    serializer_class = CardSerializer

    def get_queryset(self):
        return Card.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        create_card(owner=self.request.user, **serializer.validated_data)

    def perform_update(self, serializer):
        update_card(serializer.instance, **serializer.validated_data)
