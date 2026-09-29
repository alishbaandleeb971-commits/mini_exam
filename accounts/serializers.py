import re
from rest_framework import serializers
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "password"]   # no "role": clients can't set it

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value):
        if len(value) < 8 or not re.search(r"[A-Z]", value) or not re.search(r"\d", value):
            raise serializers.ValidationError(
                "Min 8 characters, 1 uppercase letter and 1 number."
            )
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)  # hashes the password


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "role"]