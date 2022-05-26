from records.views import AdministratorAPIView, AppointmentsAPIView, DepartmentAPIView, DoctorAPIView, InvoiceAPIView, LabtechAPIView, MedicineAPIView, NurseAPIView, PatientAPIView, PaymentAPIView, PharmacistAPIView, ReceptionistAPIView, TestAPIView, UserAPIView
from rest_framework.routers import SimpleRouter
from django.views.generic import TemplateView
from django.urls import path
from rest_framework_simplejwt.views import (TokenRefreshView)

from accounts.views import (
    AdministratorProfileAPIView, DoctorProfileAPIViewSet,
    LabtechProfileAPIView, LoginViewSet, NurseProfileAPIView,
    PasswordResetTokenCheck, PatientProfileAPIView, PatientRegistrationViewSet,
    PharmacistProfileAPIView, ReceptionistProfileAPIView, RefreshViewSet,
    RegistrationViewSet, RequestPasswordResetEmail, SetNewPasswordAPIView,
    VerifyEmail
)

from appointments.views import DoctorAppointmentApiView, DoctorMedicineAPIView, DoctorTestAPIView, MedicineRecommendation, PatientAppointmentsApiView, ReceptionistApointmentApiView, ReceptionistTestCartAPIView, TestRecommendation
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
routes.register("receptionist/test", ReceptionistTestCartAPIView,
                basename="receptionist-test-cart")


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
