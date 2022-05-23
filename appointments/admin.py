from django.contrib import admin

from appointments.models import (Appointments, Lab_test, Medicine, Tests, Test)


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
                    "available", "added_by")
    list_filter = ("available",)


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ("drug", "price", "on_stock",
                    "added_by")
    list_filter = ("on_stock",)


@admin.register(Test)
class PatientTestAdmin(admin.ModelAdmin):
    list_display = ("test", "get_patient_id", "get_patient_username",
                    "tested", "paid",
                    "get_test_price",  "get_appointment_status",
                    "date_tested", "lab_tech")
    list_filter = ("paid", "tested")

    def get_patient_id(self, obj):
        return obj.appointment.id
    get_patient_id.short_description = "Appointment ID"
    get_patient_id.admin_order_field = "appointment__id"

    def get_patient_username(self, obj):
        return obj.appointment.patient.user.username
    get_patient_username.short_description = "Patient"
    get_patient_username.admin_order_field = "appointment__patient__user__username"

    def get_appointment_status(self, obj):
        return obj.appointment.status
    get_appointment_status.short_description = "Appointment Status"
    get_appointment_status.admin_order_field = "appointment__status"

    def get_test_price(self, obj):
        return obj.Total_unit_Price()
    get_test_price.short_description = "Price"


@admin.register(Tests)
class PatientTestCartAdmin(admin.ModelAdmin):
    list_display = ("get_patient_username", "get_patient_id",
                    "tested", "paid",
                    "get_total_test_price",
                    "get_appointment_status", "date_tested"
                    )
    list_filter = ("paid", "tested")

    def get_patient_username(self, obj):
        return obj.appointment.patient.user.username
    get_patient_username.short_description = "Patient"
    get_patient_username.admin_order_field = "appointment__patient__user__username"

    def get_appointment_status(self, obj):
        return obj.appointment.status
    get_appointment_status.short_description = "Appointment Status"
    get_appointment_status.admin_order_field = "appointment__status"

    def get_total_test_price(self, obj):
        return obj.Total_price()
    get_total_test_price.short_description = "Total Cost"

    def get_patient_id(self, obj):
        return obj.appointment.id
    get_patient_id.short_description = "Appointment ID"
    get_patient_id.admin_order_field = "appointment__id"
