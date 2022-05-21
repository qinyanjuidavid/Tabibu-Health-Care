from django.contrib import admin

from appointments.models import (Appointments, Lab_test,)


@admin.register(Appointments)
class appointmentAdmin(admin.ModelAdmin):
    list_display = ("get_patient_username", "department", "appointment_fee",
                    "doctor", "status", "appointment_date", "appointment_time",
                    "paid", "expired"
                    )

    list_filter = ("paid", "status", "department", "expired")

    def get_patient_username(self, obj):
        return obj.patient.user.username
    get_patient_username.short_description = "Patient"
    get_patient_username.admin_order_field = "patient__user__username"


@admin.register(Lab_test)
class LabtestAdmin(admin.ModelAdmin):
    list_display = ("lab_test", "price",
                    "available", "description")
    list_filter = ("available",)
