from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from apps.cards.models import Card, Deck, HierarchyItem
from .serializers import (
    CardIdsSerializer,
    CardSerializer,
    DeckSerializer,
    HierarchyItemSerializer,
    MoveCardsSerializer,
    PublicCardSerializer,
)
from apps.cards.services.card_services import create_card, update_card
from apps.cards.services.deck_services import (
    add_cards_to_deck,
    copy_deck,
    create_deck,
    move_cards_between_decks,
    remove_cards_from_deck,
    update_deck,
)
from apps.cards.services.hierarchy_services import (
    create_hierarchy_item,
    update_hierarchy_item,
)


@extend_schema(tags=["Cards"])
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


class IsDeckOwnerOrPublicReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.owner == request.user or obj.is_public
        return obj.owner == request.user


@extend_schema(tags=["Decks"])
@extend_schema_view(
    list=extend_schema(
        summary="List your decks",
        description="Returns decks owned by the authenticated user, plus any public decks from other users.",
    ),
    retrieve=extend_schema(
        summary="Retrieve a deck",
        description="Returns a deck owned by the authenticated user, or any public deck.",
    ),
    create=extend_schema(
        summary="Create a deck",
        description="Creates a new deck for the authenticated user, optionally nested under a hierarchy item you own.",
    ),
    update=extend_schema(
        summary="Replace a deck",
        description="Replaces all fields of a deck you own.",
    ),
    partial_update=extend_schema(
        summary="Update a deck",
        description="Updates one or more fields of a deck you own.",
    ),
    destroy=extend_schema(
        summary="Delete a deck",
        description="Deletes a deck you own.",
    ),
)
class DeckViewSet(viewsets.ModelViewSet):
    serializer_class = DeckSerializer
    permission_classes = [permissions.IsAuthenticated, IsDeckOwnerOrPublicReadOnly]

    def get_queryset(self):
        return Deck.objects.filter(
            Q(owner=self.request.user) | Q(is_public=True)
        ).distinct()

    def perform_create(self, serializer):
        create_deck(owner=self.request.user, **serializer.validated_data)

    def perform_update(self, serializer):
        update_deck(serializer.instance, **serializer.validated_data)

    @extend_schema(
        summary="List this deck's cards",
        description=(
            "Owner sees full card data including progress; other users see "
            "public-safe fields only, and only if the deck is public."
        ),
    )
    @action(detail=True, methods=["get"], url_path="cards")
    def cards(self, request, pk=None):
        deck = self.get_object()
        if deck.owner == request.user:
            data = CardSerializer(deck.cards.all(), many=True).data
        elif deck.is_public:
            data = PublicCardSerializer(deck.cards.all(), many=True).data
        else:
            raise PermissionDenied("This deck is private.")
        return Response(data)

    @extend_schema(
        summary="Add cards to this deck",
        description="Owner only. Accepts one or more card_ids you own.",
    )
    @action(detail=True, methods=["post"], url_path="cards/add")
    def add_cards(self, request, pk=None):
        deck = self.get_object()
        self._require_owner(deck)
        serializer = CardIdsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cards = self._owned_cards_or_400(serializer.validated_data["card_ids"])
        try:
            add_cards_to_deck(cards, deck)
        except ValueError as e:
            raise ValidationError(str(e))
        return Response(CardSerializer(deck.cards.all(), many=True).data)

    @extend_schema(
        summary="Remove cards from this deck",
        description="Owner only.",
    )
    @action(detail=True, methods=["post"], url_path="cards/remove")
    def remove_cards(self, request, pk=None):
        deck = self.get_object()
        self._require_owner(deck)
        serializer = CardIdsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cards = self._owned_cards_or_400(serializer.validated_data["card_ids"])
        remove_cards_from_deck(cards, deck)
        return Response(CardSerializer(deck.cards.all(), many=True).data)

    @extend_schema(
        summary="Move cards to another of your decks",
        description="Both decks must be owned by you.",
    )
    @action(detail=True, methods=["post"], url_path="cards/move")
    def move_cards(self, request, pk=None):
        source = self.get_object()
        self._require_owner(source)
        serializer = MoveCardsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        target = get_object_or_404(
            Deck, pk=serializer.validated_data["target_deck_id"], owner=request.user
        )
        cards = self._owned_cards_or_400(serializer.validated_data["card_ids"])
        try:
            move_cards_between_decks(cards, source, target)
        except ValueError as e:
            raise ValidationError(str(e))
        return Response(DeckSerializer(target, context={"request": request}).data)

    @extend_schema(
        summary="Copy a deck",
        description=(
            "Creates your own independent copy of a public (or your own) deck, "
            "including fresh copies of its cards with no progress history."
        ),
    )
    @action(detail=True, methods=["post"], url_path="copy")
    def copy(self, request, pk=None):
        deck = get_object_or_404(
            Deck.objects.filter(Q(owner=request.user) | Q(is_public=True)), pk=pk
        )
        new_deck = copy_deck(deck, new_owner=request.user)
        return Response(
            DeckSerializer(new_deck, context={"request": request}).data, status=201
        )

    def _require_owner(self, deck):
        if deck.owner != self.request.user:
            raise PermissionDenied("Only the deck owner can modify its cards.")

    def _owned_cards_or_400(self, card_ids):
        cards = list(Card.objects.filter(id__in=card_ids, owner=self.request.user))
        if len(cards) != len(set(card_ids)):
            raise ValidationError("One or more card_ids don't exist or aren't yours.")
        return cards


@extend_schema(tags=["Hierarchy Items"])
@extend_schema_view(
    list=extend_schema(
        summary="List your hierarchy items",
        description="Returns all hierarchy items owned by the authenticated user.",
    ),
    retrieve=extend_schema(
        summary="Retrieve a hierarchy item",
        description="Returns a single hierarchy item owned by the authenticated user.",
    ),
    create=extend_schema(
        summary="Create a hierarchy item",
        description="Creates a new hierarchy item, optionally nested under a parent hierarchy item you own.",
    ),
    update=extend_schema(
        summary="Replace a hierarchy item",
        description="Replaces all fields of a hierarchy item you own.",
    ),
    partial_update=extend_schema(
        summary="Update a hierarchy item",
        description="Updates one or more fields of a hierarchy item you own.",
    ),
    destroy=extend_schema(
        summary="Delete a hierarchy item",
        description="Deletes a hierarchy item you own.",
    ),
)
class HierarchyItemViewSet(viewsets.ModelViewSet):
    serializer_class = HierarchyItemSerializer

    def get_queryset(self):
        return HierarchyItem.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        create_hierarchy_item(owner=self.request.user, **serializer.validated_data)

    def perform_update(self, serializer):
        update_hierarchy_item(serializer.instance, **serializer.validated_data)
