from rest_framework import serializers

from ward.models import Rooms, Slot, Ward, WardBooking


class WardSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedRelatedField(read_only=True)

    class Meta:
        model = Ward
        fields = (
            "id", "url", "ward_name", "gender",
            "added_by", "created_at",
            "updated_at")
        read_only_fields = ("id",)


class RoomsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rooms
        fields = (
            "id", "room_number", "room_type",
            "ward", "added_by", "created_at",
            "updated_at")
        read_only_fields = ("id",)


class SlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slot
        fields = (
            "id", "bed_number", "room",
            "price_per_night", "added_by",
            "created_at", "updated_at")

        read_only_fields = ("id",)


class WardBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = WardBooking
        fields = (
            "id", "slot", "appointment", "admission_date",
            "date_expected_to_leave", "discharde_date",
            "total_amount", "nok_full_name", "relationship",
            "nok_phone", "on_waiting_list"
        )
        read_only_fields = ("id",)
