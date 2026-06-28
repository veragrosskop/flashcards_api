from django.contrib.auth import get_user_model
from rest_framework import serializers

from common.enums.language import LanguageChoice

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    native_languages = serializers.ListField(child=serializers.ChoiceField(choices=LanguageChoice.choices), required=False)
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "native_languages"]
        read_only_fields = ["id"]

    def validate_email(self, value):
        queryset = User.objects.filter(email__iexact=value)

        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError("A user with this email already exists.")

        return value


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    native_languages = serializers.ListField(
        child=serializers.ChoiceField(choices=LanguageChoice.choices),
        required=False,
    )
    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "native_languages"]
        read_only_fields = ["id"]

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)