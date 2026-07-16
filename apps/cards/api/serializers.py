from rest_framework import serializers
from apps.cards.models import Card, Deck, HierarchyItem
from common.enums.language import LanguageChoice


class CardSerializer(serializers.ModelSerializer):
    native_language = serializers.ChoiceField(
        choices=LanguageChoice.choices,
        help_text="Language code of the `native` field (e.g. EN).",
    )
    foreign_language = serializers.ChoiceField(
        choices=LanguageChoice.choices,
        help_text="Language code of the `foreign` field (e.g. NL). Must differ from native_language.",
    )

    class Meta:
        model = Card
        fields = "__all__"
        read_only_fields = ["id", "owner", "date_created"]
        extra_kwargs = {
            "native": {
                "help_text": "The word or phrase in the user's native language."
            },
            "foreign": {
                "help_text": "The word or phrase in the foreign language being learned."
            },
            "box_ntf": {
                "help_text": "Spaced-repetition box (1-5) for native-to-foreign review. Defaults to 1."
            },
            "box_ftn": {
                "help_text": "Spaced-repetition box (1-5) for foreign-to-native review. Defaults to 1."
            },
        }

    def validate(self, data):
        native = data.get("native")
        foreign = data.get("foreign")
        native_language = data.get("native_language")
        foreign_language = data.get("foreign_language")
        box_ntf = data.get("box_ntf")
        box_ftn = data.get("box_ftn")

        if self.instance is not None:
            native = native if native is not None else self.instance.native
            foreign = foreign if foreign is not None else self.instance.foreign
            native_language = (
                native_language
                if native_language is not None
                else self.instance.native_language
            )
            foreign_language = (
                foreign_language
                if foreign_language is not None
                else self.instance.foreign_language
            )
            box_ntf = box_ntf if box_ntf is not None else self.instance.box_ntf
            box_ftn = box_ftn if box_ftn is not None else self.instance.box_ftn

        if not native or not foreign:
            raise serializers.ValidationError("Both native and foreign are required.")

        if native_language == foreign_language:
            raise serializers.ValidationError(
                "Native and foreign language cannot be the same."
            )

        return data


class PublicCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ["id", "native", "foreign", "native_language", "foreign_language"]


class CardIdsSerializer(serializers.Serializer):
    card_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)


class MoveCardsSerializer(CardIdsSerializer):
    target_deck_id = serializers.IntegerField()


class DeckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deck
        fields = "__all__"
        read_only_fields = ["id", "owner", "cards"]
        validators = []  # auto UniqueTogetherValidator can't handle read-only `owner`; enforced in validate() below

    def validate(self, data):
        name = data.get("name", getattr(self.instance, "name", None))
        parent = data.get("parent", getattr(self.instance, "parent", None))
        owner = self.context["request"].user

        if parent is not None and parent.owner != owner:
            raise serializers.ValidationError("Parent hierarchy item must be one of your own.")

        qs = Deck.objects.filter(owner=owner, name=name, parent=parent)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "You already have a deck with this name under this parent."
            )
        return data


class HierarchyItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = HierarchyItem
        fields = "__all__"
        read_only_fields = ["id", "owner"]

    def validate(self, data):
        parent = data.get("parent", getattr(self.instance, "parent", None))
        owner = self.context["request"].user

        if parent is not None and parent.owner != owner:
            raise serializers.ValidationError("Parent hierarchy item must be one of your own.")

        if self.instance is not None and parent is not None:
            node, visited = parent, set()
            while node is not None:
                if node.pk == self.instance.pk:
                    raise serializers.ValidationError(
                        "A hierarchy item cannot be its own ancestor."
                    )
                if node.pk in visited:
                    break  # defensive: pre-existing cycle, don't loop forever
                visited.add(node.pk)
                node = node.parent
        return data
