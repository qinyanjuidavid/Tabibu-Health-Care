from billing.models import Payment, Invoice
from rest_framework import serializers
from appointments.serializers import patientAppointmentSerializer


class PaymentSerializer(serializers.ModelSerializer):
    appointment = patientAppointmentSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ("id", "item", "appointment",
                  "quantity", "total_amount", "sub_unit",
                  "payment_date", "tax_rate", "paid_amount",
                  "balance", "status", "payment_method",
                  "receptionist", "payment_type",
                  "description", "type", "reference",
                  "first_name", "middle_name", "last_name",
                  "phone_number", "organization_balance")
        read_only_fields = ("id", "organization_balance")


class InvoiceSerializer(serializers.ModelSerializer):
    appointment = patientAppointmentSerializer(read_only=True)
    payment = PaymentSerializer(read_only=True)

    class Meta:
        model = Invoice
        fields = ("id", "payment", "invoiced_date",
                  "total_amount", "balance", "appointment",
                  "paid", "status", "receptionist")
        read_only_fields = ("id",)
