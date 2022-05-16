from accounts.models import (
    Administrator, Departments, Pharmacist,
    User, Patient, Receptionist, Doctor, Nurse, Labtech
)
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db import transaction
from django.utils.encoding import (
    DjangoUnicodeDecodeError, force_str,
    smart_bytes, smart_str
)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth.models import update_last_login
from django.core.exceptions import ObjectDoesNotExist


class UserSerializer(CountryFieldMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username",
                  "full_name", "email",
                  "phone", "timestamp")
        read_only_field = ("id", "email", "timestamp")


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data["user"] = UserSerializer(self.user).data
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)
        return data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128, min_length=4, write_only=True
        required=True
    )
    email = serializers.EmailField(
        required=True, max_length=128
    )

    class Meta:
        model = User
        fields = [
            "username", "email", "phone", "role"
            "full_name", "password"
        ]

    def create(self, validated_data):
        try:
            user = User.objects.get(email=validated_data["email"])
        except ObjectDoesNotExist:
            user = User.objects.create(
                username=validated_data["username"],
                email=validated_data["email"],
                phone=validated_data["phone"],
                is_active=False
                role=validated_data['role']
            )
            user.set_password(validated_data["password"])
            user.save()
        return user
