from rest_framework.routers import SimpleRouter
from django.views.generic import TemplateView
from django.urls import path
from rest_framework_simplejwt.views import (TokenRefreshView)

from accounts.views import (
    LoginViewSet, PasswordResetTokenCheck, RefreshViewSet, RegistrationViewSet, RequestPasswordResetEmail, SetNewPasswordAPIView, VerifyEmail
)
app_name = "api"
routes = SimpleRouter()
routes.register('login', LoginViewSet, basename='login')
routes.register('register', RegistrationViewSet, basename='register')
routes.register('auth/refresh', RefreshViewSet, basename='auth-refresh')
routes.register('password-reset', RequestPasswordResetEmail,
                basename="requestPasswordReset")
routes.register('password-reset-complete', SetNewPasswordAPIView,
                basename="password-reset-complete")

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
