from django.contrib import admin
from billing.models import (
    Payment, MpesaCallBacks,
    MpesaCalls, Invoice)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("item", "get_appointment_id",
                    "get_patient_username", "sub_unit",
                    "quantity", "total_amount", "paid_amount",
                    "status", "paid", "payment_method", "status"
                    )
    list_filter = ("paid", "type",
                   "payment_method", "status")

    def get_patient_username(self, obj):
        return obj.appointment.patient.user.username

    get_patient_username.short_description = "Patient"
    get_patient_username.admin_order_field = "appointment__patient__user__username"

    def get_appointment_id(self, obj):
        return obj.appointment.id
    get_appointment_id.short_description = "Appointment ID"
    get_appointment_id.admin_order_field = "appointment__id"

    def get_total_amount(self, obj):
        return obj.Total_Payment_amount()
    get_total_amount.short_description = "Total Amount"


admin.site.register(MpesaCallBacks)
admin.site.register(MpesaCalls)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("get_patient_username", "get_appointment_id",
                    "get_total_amount",
                    "paid_amount", "status", "paid",
                    "payment_method", "invoiced_date",
                    )
    list_filter = ("paid", "payment_method", "status")

    def get_patient_username(self, obj):
        return obj.appointment.patient.user.username

    get_patient_username.short_description = "Patient"
    get_patient_username.admin_order_field = "appointment__patient__user__username"

    def get_appointment_id(self, obj):
        return obj.appointment.id
    get_appointment_id.short_description = "Appointment ID"
    get_appointment_id.admin_order_field = "appointment__id"

    def get_total_amount(self, obj):
        return obj.Invoice_Total()
    get_total_amount.short_description = "Total Amount"
