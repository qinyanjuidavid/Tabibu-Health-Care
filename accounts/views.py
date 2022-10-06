from accounts.permissions import (
    IsAdministrator,
    IsDoctor,
    IsDriver,
    IsLabtech,
    IsNurse,
    IsPatient,
    IsPharmacist,
    IsReceptionist,
)
from accounts.send_mails import (
    send_activation_mail,
    send_password_reset_email,
    send_random_password_mail,
)
import jwt
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.encoding import (
    DjangoUnicodeDecodeError,
    force_str,
    smart_bytes,
    smart_str,
)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import generics, serializers, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q, query
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.exceptions import AuthenticationFailed
from accounts.models import (
    Administrator,
    Doctor,
    Driver,
    Labtech,
    Nurse,
    Patient,
    Pharmacist,
    Receptionist,
    User,
)
from accounts.serializers import (
    AdministratorProfileSerializer,
    DoctorProfileSerializer,
    DriverProfileSerializer,
    LabtechProfileSerializer,
    LoginSerializer,
    NurseProfileSerializer,
    PatientProfileSerializer,
    PatientRegisterSerializer,
    PharmacistProfileSerializer,
    ReceptionistProfileSerializer,
    ResetPasswordEmailRequestSerializer,
    SetNewPasswordSerializer,
    UserSerializer,
    RegisterSerializer,
)


class LoginViewSet(ModelViewSet, TokenObtainPairSerializer):
    serializer_class = LoginSerializer
    permission_classes = [
        AllowAny,
    ]
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class RefreshViewSet(viewsets.ViewSet, TokenRefreshView):
    permission_classes = (AllowAny,)
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class RegistrationViewSet(ModelViewSet, TokenObtainPairView):
    serializer_class = RegisterSerializer
    permission_classes = [
        AllowAny,
    ]
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(is_active=False)
        password = User.objects.make_random_password()
        user.set_password(password)
        user.save()
        user_data = serializer.data
        user_data["password"] = password
        send_activation_mail(user_data, request)
        send_random_password_mail(user_data, user_data["password"], request)
        refresh = RefreshToken.for_user(user)
        res = {"refresh": str(refresh), "access": str(refresh.access_token)}
        return Response(
            {
                "user": serializer.data,
                "refresh": res["refresh"],
                "token": res["access"],
            },
            status=status.HTTP_201_CREATED,
        )


class PatientRegistrationViewSet(ModelViewSet, TokenObtainPairView):
    serializer_class = PatientRegisterSerializer
    permission_classes = [
        AllowAny,
    ]
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if (
            serializer.validated_data["password"]
            and serializer.validated_data["password_confirmation"]
            and serializer.validated_data["password"]
            == serializer.validated_data["password_confirmation"]
        ):
            user = serializer.save(is_active=False)
            user_data = serializer.data
            send_activation_mail(user_data, request)
            refresh = RefreshToken.for_user(user)
            res = {"refresh": str(refresh), "access": str(refresh.access_token)}
            return Response(
                {
                    "user": serializer.data,
                    "refresh": res["refresh"],
                    "token": res["access"],
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            raise serializers.ValidationError({"Error": ("Passwords don't match!")})


def VerifyEmail(request):
    token = request.GET.get("token")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
        user = User.objects.get(id=payload["user_id"])
        if not user.is_active:
            user.is_active = True
            user.save()
            messages.success(request, "Account was Successfully Verified.")
        else:
            messages.info(
                request,
                """Your Account has already been activated.
                          You can now login and
                          book an appointment today.
                        """,
            )
    except jwt.ExpiredSignatureError as identifier:
        messages.warning(request, "The Activation Link Expired!")
    except jwt.exceptions.DecodeError as identifier:
        messages.warning(request, "Invalid Activation Link!")
    context = {}
    return render(request, "accounts/verify.html", context)


# Password Reset
class RequestPasswordResetEmail(ModelViewSet):
    serializer_class = ResetPasswordEmailRequestSerializer
    permission_classes = (AllowAny,)
    http_method_names = [
        "post",
    ]

    def create(self, request, *args, **kwargs):
        self.get_serializer(data=request.data)
        email = request.data["email"]
        if User.objects.filter(email=email):
            user = User.objects.get(email=email)
            if user.is_active:
                send_password_reset_email(user, request)
            return Response(
                {
                    "Success": "If there’s an account associated with this email address, we’ll send you an email with reset instructions. If you don’t get an email, contact the Support team."
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "Success": "If there’s an account associated with this email address, we’ll send you an email with reset instructions. If you don’t get an email, contact the Support team."
            }
        )


def PasswordResetTokenCheck(request, uidb64, token):
    try:
        id = smart_bytes(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=id)
        if not PasswordResetTokenGenerator().check_token(user, token):
            messages.info(
                request,
                "Password Reset link is no longer valid, Please request a new one.",
            )
    except DjangoUnicodeDecodeError as identifier:
        if not PasswordResetTokenGenerator().check_token(user, token):
            messages.info(
                request, "Password is no longer valid, Please request a new one."
            )
    context = {
        "uidb64": uidb64,
        "token": token,
    }
    return render(request, "accounts/password_reset.html", context)


class SetNewPasswordAPIView(ModelViewSet):
    serializer_class = SetNewPasswordSerializer
    permission_classes = (AllowAny,)
    http_method_names = [
        "post",
    ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            password = request.data["password"]
            password_confirmation = request.data["password_confirmation"]
            token = request.data["token"]
            uidb64 = request.data["uidb64"]
            if password and password_confirmation and password != password_confirmation:
                raise serializers.ValidationError({"Error": ("Passwords don't match!")})
            else:
                id = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(id=id)
                if not PasswordResetTokenGenerator().check_token(user, token):
                    raise AuthenticationFailed(
                        "The Reset Link is Invalid!",
                        401,
                    )
                else:
                    user.set_password(password)
                    user.save()
                    return Response(
                        {"success": "Password reset successful"},
                        status=status.HTTP_201_CREATED,
                    )
        except Exception as e:
            raise AuthenticationFailed("The Reset Link is Invalid!", 401)
        return Response(serializer.data)


class AdministratorProfileAPIView(ModelViewSet):
    serializer_class = AdministratorProfileSerializer
    permission_classes = [IsAuthenticated, IsAdministrator]
    http_method_names = (
        "put",
        "get",
    )

    def get_queryset(self):
        user = self.request.user
        adminQuery = Administrator.objects.filter(Q(user=user))
        return adminQuery

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        userSerializer = UserSerializer(request.user, data=request.data["user"])
        userSerializer.is_valid(raise_exception=True)
        userSerializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class PharmacistProfileAPIView(ModelViewSet):
    serializer_class = PharmacistProfileSerializer
    permission_classes = [IsAuthenticated, IsPharmacist]
    http_method_names = ("put", "get")

    def get_queryset(self):
        user = self.request.user
        pharmacistQuery = Pharmacist.objects.filter(Q(user=user))
        return pharmacistQuery

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        userSerializer = UserSerializer(request.user, data=request.data["user"])
        userSerializer.is_valid(raise_exception=True)

        instance.user.username = userSerializer.validated_data["username"]
        instance.user.full_name = userSerializer.validated_data["full_name"]
        instance.user.phone = userSerializer.validated_data["phone"]
        instance.user.save()
        # userSerializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class NurseProfileAPIView(ModelViewSet):
    serializer_class = NurseProfileSerializer
    permission_classes = [IsAuthenticated, IsNurse]
    http_method_names = ("put", "get")

    def get_queryset(self):
        user = self.request.user
        nurseQuery = Nurse.objects.filter(Q(user=user))
        return nurseQuery

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        userSerializer = UserSerializer(request.user, data=request.data["user"])
        userSerializer.is_valid(raise_exception=True)
        userSerializer.is_valid(raise_exception=True)
        instance.user.username = userSerializer.validated_data["username"]
        instance.user.full_name = userSerializer.validated_data["full_name"]
        instance.user.phone = userSerializer.validated_data["phone"]
        instance.user.save()
        # userSerializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class DoctorProfileAPIViewSet(ModelViewSet):
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsAuthenticated, IsDoctor]
    http_method_names = ("put", "get")

    def get_queryset(self):
        user = self.request.user
        doctorQuery = Doctor.objects.filter(Q(user=user))
        return doctorQuery

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.is_valid()
        serializer.save()
        userSerializer = UserSerializer(request.user, data=request.data["user"])
        userSerializer.is_valid(raise_exception=True)
        instance.user.username = userSerializer.validated_data["username"]
        instance.user.full_name = userSerializer.validated_data["full_name"]
        instance.user.phone = userSerializer.validated_data["phone"]
        instance.user.save()
        # userSerializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class LabtechProfileAPIView(ModelViewSet):
    serializer_class = LabtechProfileSerializer
    permission_classes = [IsAuthenticated, IsLabtech]
    http_method_names = ("put", "get")

    def get_queryset(self):
        user = self.request.user
        labtechQuery = Labtech.objects.filter(Q(user=user))
        return labtechQuery

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        userSerializer = UserSerializer(request.user, data=request.data["user"])
        userSerializer.is_valid(raise_exception=True)
        instance.user.username = userSerializer.validated_data["username"]
        instance.user.full_name = userSerializer.validated_data["full_name"]
        instance.user.phone = userSerializer.validated_data["phone"]
        instance.user.save()
        # userSerializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class ReceptionistProfileAPIView(ModelViewSet):
    serializer_class = ReceptionistProfileSerializer
    permission_classes = [IsAuthenticated, IsReceptionist]
    http_method_names = ("put", "get")

    def get_queryset(self):
        user = self.request.user
        receptionistQuery = Receptionist.objects.filter(Q(user=user))
        return receptionistQuery

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        userSerializer = UserSerializer(request.user, data=request.data["user"])
        userSerializer.is_valid(raise_exception=True)
        instance.user.username = userSerializer.validated_data["username"]
        instance.user.full_name = userSerializer.validated_data["full_name"]
        instance.user.phone = userSerializer.validated_data["phone"]
        instance.user.save()
        # userSerializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class PatientProfileAPIView(ModelViewSet):
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated, IsPatient]
    http_method_names = ("put", "get")

    def get_queryset(self):
        user = self.request.user
        patientQuery = Patient.objects.filter(Q(user=user))
        return patientQuery

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        userSerializer = UserSerializer(request.user, data=request.data["user"])
        userSerializer.is_valid(raise_exception=True)
        instance.user.username = userSerializer.validated_data["username"]
        instance.user.full_name = userSerializer.validated_data["full_name"]
        instance.user.phone = userSerializer.validated_data["phone"]
        instance.user.save()
        # userSerializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class DriverProfileAPIView(ModelViewSet):
    serializer_class = DriverProfileSerializer
    permission_classes = [IsAuthenticated, IsDriver]
    http_method_names = ("get", "put")

    def get_queryset(self):
        user = self.request.user
        driverQs = Driver.objects.filter(Q(user=user))
        return driverQs

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_object()
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        userSerializer = UserSerializer(request.user, data=request.data["user"])
        userSerializer.is_valid(raise_exception=True)
        instance.user.username = userSerializer.validated_data["username"]
        instance.user.full_name = userSerializer.validated_data["full_name"]
        instance.user.phone = userSerializer.validated_data["phone"]
        instance.user.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
