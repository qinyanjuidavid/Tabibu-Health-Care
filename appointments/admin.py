from django.contrib import admin

from appointments.models import (
    AmbulanceBooking, Appointments, Lab_test, Medication, Medication_Bag, Medicine, Tests, Test)


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


@admin.register(Medication)
class PatientMedicationAdmin(admin.ModelAdmin):
    list_display = ("medicine", "get_patient_id",
                    "get_patient_username", "dispenced", "paid",
                    "price", "quantity",
                    "get_medication_price",
                    "get_appointment_status",
                    "prescription_date"
                    )
    list_filter = ("paid", "dispenced")

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

    def get_medication_price(self, obj):
        return obj.Total_medication_price()
    get_medication_price.short_description = "Total Cost"


@admin.register(Medication_Bag)
class PatientPrescriptioncart(admin.ModelAdmin):
    list_display = ("get_patient_username", "get_patient_id",
                    "dispenced", "paid",
                    "get_medication_price",
                    "get_appointment_status",
                    )
    list_filter = ("paid", "dispenced")

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

    def get_medication_price(self, obj):
        return obj.Total_Prescription_price()
    get_medication_price.short_description = "Total Cost"


@admin.register(AmbulanceBooking)
class AmbulanceBookingAdmin(admin.ModelAdmin):
    list_display = (
        "get_patient_username", "get_driver_username",
        "arrived", "cancelled", "pick_up_time", "drop_off_time",
        "price"
    )

    def get_patient_username(self, obj):
        return obj.appointment.patient.user.username
    get_patient_username.short_description = "Patient"
    get_patient_username.admin_order_field = "patient__user__username"

    def get_driver_username(self, obj):
        return obj.driver.user.username
    get_driver_username.short_description = "Driver"
    get_driver_username.admin_order_field = "driver__user__username"
