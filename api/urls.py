from records.views import AdministratorAPIView, AppointmentsAPIView, DepartmentAPIView, DoctorAPIView, DriverAPIView, InvoiceAPIView, LabtechAPIView, MedicineAPIView, NurseAPIView, PatientAPIView, PaymentAPIView, PharmacistAPIView, ReceptionistAPIView, TestAPIView, UserAPIView
from rest_framework.routers import SimpleRouter
from django.views.generic import TemplateView
from django.urls import path
from rest_framework_simplejwt.views import (TokenRefreshView)

from accounts.views import (
    AdministratorProfileAPIView, DoctorProfileAPIViewSet, DriverProfileAPIView,
    LabtechProfileAPIView, LoginViewSet, NurseProfileAPIView,
    PasswordResetTokenCheck, PatientProfileAPIView, PatientRegistrationViewSet,
    PharmacistProfileAPIView, ReceptionistProfileAPIView, RefreshViewSet,
    RegistrationViewSet, RequestPasswordResetEmail, SetNewPasswordAPIView,
    VerifyEmail
)

from appointments.views import (
    AdminAmbulanceTrips, AmbulanceAPIView, AmbulanceBookingAPIView, DoctorAppointmentApiView, DoctorMedicineAPIView,
    DoctorTestAPIView, DriverAmbulanceTrips, LabtechTestCartAPIView,
    LabtechTestsAPIView, MedicineRecommendation,
    PatientAppointmentsApiView, PatientTestAPIView, PatientTestsCartAPIView,
    PharmacistMedicationAPIView, PharmacistPrescriptionCartAPIView,
    ReceptionistApointmentApiView, ReceptionistMedicationAPIView,
    ReceptionistPrescriptionAPIView, ReceptionistTestCartAPIView,
    ReceptionistTestsAPIView, TestRecommendation)
app_name = "api"
routes = SimpleRouter()
routes.register('login', LoginViewSet, basename='login')
routes.register('register', RegistrationViewSet, basename='register')
routes.register('auth/refresh', RefreshViewSet, basename='auth-refresh')
routes.register('password-reset', RequestPasswordResetEmail,
                basename="requestPasswordReset")
routes.register('password-reset-complete', SetNewPasswordAPIView,
                basename="password-reset-complete")
routes.register('patient/register', PatientRegistrationViewSet,
                basename="patient-register")
routes.register('admin/profile', AdministratorProfileAPIView,
                basename="admin-profile")
routes.register('pharmacist/profile', PharmacistProfileAPIView,
                basename="pharmacist-profile")
routes.register('nurse/profile', NurseProfileAPIView,
                basename="nurse-profile")
routes.register('doctor/profile', DoctorProfileAPIViewSet,
                basename="doctor-profile")
routes.register('labtech/profile', LabtechProfileAPIView,
                basename="labtech-profile")
routes.register('receptionist/profile', ReceptionistProfileAPIView,
                basename="receptionist-profile")
routes.register('patient/profile', PatientProfileAPIView,
                basename="patient-profile")
routes.register("driver/profile", DriverProfileAPIView,
                basename="driver-profile")  # Untested
# Appointment Routes
routes.register('appointment', PatientAppointmentsApiView,
                basename='appointment')
routes.register('receptionist-appointments', ReceptionistApointmentApiView,
                basename="receptionistAppointment")
routes.register("doctor-appointments", DoctorAppointmentApiView,
                basename="doctorsAppointment")
routes.register("test/recommendation", TestRecommendation,
                basename="test-recommendation")
routes.register("doctor/medicine", DoctorMedicineAPIView,
                basename="doctor-medicine")
routes.register("medicine/recommendation", MedicineRecommendation,
                basename="medicine-recommendation")
routes.register("receptionist/test/cart", ReceptionistTestCartAPIView,
                basename="receptionist-test-cart")
routes.register("receptionist/tests", ReceptionistTestsAPIView,
                basename="receptionist-tests")
routes.register("receptionist/prescriptions", ReceptionistPrescriptionAPIView,
                basename="receptionist-prescription")
routes.register("receptionist/medications", ReceptionistMedicationAPIView,
                basename="receptionist-medications")
routes.register("labtech/test/cart", LabtechTestCartAPIView,
                basename="labtech-test-cart")
routes.register("labtech/tests", LabtechTestsAPIView,
                basename="labtech-tests")
routes.register("pharmacist/prescriptions", PharmacistPrescriptionCartAPIView,
                basename="pharmacist-prescription")
routes.register("pharmacist/medications", PharmacistMedicationAPIView,
                basename="pharmacist-medications")
routes.register("patient/tests/cart", PatientTestsCartAPIView,
                basename="patientTests")
routes.register("patient/test", PatientTestAPIView,
                basename="patientTest")
routes.register("ambulance", AmbulanceAPIView,
                basename="ambulance")  # Not tested
routes.register("ambulance-booking", AmbulanceBookingAPIView,
                basename="ambulance-booking")  # Not tested
routes.register("driver-ambulance-trips", DriverAmbulanceTrips,
                basename="driver-ambulance-trips")  # Not tested
routes.register("admin-ambulance-trips", AdminAmbulanceTrips,
                basename="admin-trips")  # Not Tested

# Records Routes
routes.register("tests", TestAPIView, basename="tests")
routes.register("medicine", MedicineAPIView, basename="medicine")
routes.register("doctor-tests", DoctorTestAPIView,
                basename="doctorTests")
routes.register('departments', DepartmentAPIView,
                basename="departments")
routes.register('users', UserAPIView,
                basename="users")
routes.register("admins", AdministratorAPIView,
                basename="administrators")
routes.register("pharmacists", PharmacistAPIView,
                basename="pharmacists")
routes.register("nurses", NurseAPIView,
                basename="nurses")
routes.register("doctors", DoctorAPIView,
                basename="doctors")
routes.register("labtechs", LabtechAPIView,
                basename="labtechs")
routes.register("receptionists", ReceptionistAPIView,
                basename="receptionists")
routes.register("patients", PatientAPIView,
                basename="patients")
routes.register("appointments", AppointmentsAPIView,
                basename="appointments")
routes.register("payments", PaymentAPIView,
                basename="payment")
routes.register("invoices", InvoiceAPIView,
                basename="invoices")
routes.register("drivers", DriverAPIView,
                basename="drivers")  # Untested
urlpatterns = [
    *routes.urls,
    path('activate/', VerifyEmail,
         name="email-verify"),
    path('password-reset/<uidb64>/<token>', PasswordResetTokenCheck,
         name='password-reset-confirm'),
    path('password-reset-successful/',
         TemplateView.as_view(
             template_name="accounts/password_reset_success.html"),
         name="passwordResetSuccess"
         ),
]
