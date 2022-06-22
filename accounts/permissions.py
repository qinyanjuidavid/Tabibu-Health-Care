from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsPatient(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        if request.user.role == "Patient":
            return True
        if request.method in SAFE_METHODS:
            return True
        return False


class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        if request.user.role == "Doctor":
            return True
        if request.method in SAFE_METHODS:
            return True
        return False


class IsPharmacist(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        if request.user.role == "Pharmacist":
            return True
        if request.method in SAFE_METHODS:
            return True
        return False


class IsNurse(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        if request.user.role == "Nurse":
            return True
        if request.method in SAFE_METHODS:
            return True
        return False


class IsLabtech(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        if request.user.role == "Labtech":
            return True
        if request.method in SAFE_METHODS:
            return True
        return False


class IsReceptionist(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        if request.user.role == "Receptionist":
            return True
        if request.method in SAFE_METHODS:
            return True
        return False


class IsAdministrator(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        if (request.user.role == "Administrator" or
                request.user.is_superuser or
                request.user.is_staff or
                request.user.is_admin):
            return True
        if request.method in SAFE_METHODS:
            return True
        return False


class IsDriver(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        if request.user.role == "Driver":
            return True
        if request.method in SAFE_METHODS:
            return True
        return False


class ExpiredAppointmentAdministratoruserOnly(BasePermission):
    message = "This appointment is expired!"

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.is_administrator:
            return True
        return False

    def object_expired(self, obj):
        expired_on = ""  # Midnight of the day the object was created
        return obj.created_on < expired_on

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and request.user.is_administrator:
            return True
        else:
            return False
