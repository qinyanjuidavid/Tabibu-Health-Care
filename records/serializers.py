from accounts.serializers import AdministratorProfileSerializer
from rest_framework import serializers
from accounts.models import (Administrator,)
from appointments.models import (Lab_test, Medicine)


class TestSerializer(serializers.ModelSerializer):
    added_by = AdministratorProfileSerializer(read_only=True)

    class Meta:
        model = Lab_test
        fields = ("id", "lab_test", "price",
                  "available", "description",
                  "added_by")
        read_only_fields = ("id",)


class MedicineSerializer(serializers.ModelSerializer):
    added_by = AdministratorProfileSerializer(read_only=True)

    class Meta:
        model = Medicine
        fields = ("id", "price", "on_stock",
                  "description", "added_by")
        read_only_fields = ("id",)
