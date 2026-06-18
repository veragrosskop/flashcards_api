from rest_framework import serializers
from apps.cards.models import Card
from common.enums.language import LanguageChoice

class CardSerializer(serializers.ModelSerializer):
    native_language = serializers.ChoiceField(choices=LanguageChoice.choices)
    foreign_language = serializers.ChoiceField(choices=LanguageChoice.choices)
    class Meta:
        model = Card
        fields = "__all__"
        read_only_fields = ["id", "date_created"]

    def validate(self, data):
        native = data.get("native")
        foreign = data.get("foreign")

        if not native or not foreign:
            raise serializers.ValidationError("Both native and foreign are required.")

        if native == foreign:
            raise serializers.ValidationError("Native and foreign cannot be the same.")

        return data