from rest_framework import serializers
from apps.cards.models import Card
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
