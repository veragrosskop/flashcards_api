from rest_framework import viewsets
from apps.cards.models import Card
from .serializers import CardSerializer
from apps.cards.services.card_services import create_card, update_card


class CardViewSet(viewsets.ModelViewSet):
    serializer_class = CardSerializer

    def get_queryset(self):
        return Card.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        create_card(owner=self.request.user, **serializer.validated_data)

    def perform_update(self, serializer):
        update_card(serializer.instance, **serializer.validated_data)
