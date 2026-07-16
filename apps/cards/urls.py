from rest_framework.routers import DefaultRouter
from apps.cards.api.views import CardViewSet, DeckViewSet, HierarchyItemViewSet

router = DefaultRouter()
router.register(r"cards", CardViewSet, basename="card")
router.register(r"decks", DeckViewSet, basename="deck")
router.register(r"hierarchy-items", HierarchyItemViewSet, basename="hierarchyitem")

urlpatterns = router.urls
