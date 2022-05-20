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

from appointments.views import DoctorAppointmentApiView, PatientAppointmentsApiView, ReceptionistApointmentApiView
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
routes.register("doctor-appointments", DoctorAppointmentApiView,
                basename="doctorsAppointment")
routes.register('receptionist-appointments', ReceptionistApointmentApiView,
                basename="receptionistAppointment")
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
