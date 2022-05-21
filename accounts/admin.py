from django.contrib import admin
from django.contrib.auth.models import Group

from accounts.models import (Administrator, Doctor, Labtech, Nurse, Patient,
                             Pharmacist, Receptionist, User, Departments)
admin.site.unregister(Group)


@admin.register(User)
class UsersAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role",
                    "phone", "is_active", "is_admin",
                    "is_staff", "timestamp")
    list_filter = ("is_active", "is_admin", "is_staff", "role")


@admin.register(Patient)
class PatientsAdmin(admin.ModelAdmin):
    list_display = ("get_username", "blood_group",
                    "weight", "get_active",
                    "town", "gender", "date_of_birth")
    list_filter = ("gender", "marital_status", "blood_group")

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = "Username"
    get_username.admin_order_field = "user__username"

    def get_active(self, obj):
        return obj.user.is_active
    get_active.short_description = "Active"
    get_active.admin_order_field = "user__is_active"


@admin.register(Doctor)
@admin.register(Receptionist)
@admin.register(Pharmacist)
@admin.register(Nurse)
@admin.register(Administrator)
@admin.register(Labtech)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("get_username", "job_id",
                    "department", "get_active",
                    "town", "gender", "date_of_birth")
    list_filter = ("gender", "department", "marital_status")

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = "Username"
    get_username.admin_order_field = "user__username"

    def get_active(self, obj):
        return obj.user.is_active
    get_active.short_description = "Active"
    get_active.admin_order_field = "user__is_active"


@admin.register(Departments)
class DepartmentsAdmin(admin.ModelAdmin):
    list_display = ("department",
                    "room_number", "phone", "added_by",
                    "avail", "consultation_fee",
                    "created_at")
