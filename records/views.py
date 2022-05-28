from datetime import datetime

from accounts.models import (Administrator, Departments, Doctor, Labtech,
                             Nurse, Patient, Pharmacist, Receptionist, User)
from accounts.permissions import (IsAdministrator, IsDoctor, IsLabtech,
                                  IsNurse, IsPatient, IsPharmacist,
                                  IsReceptionist)
from accounts.serializers import (AdministratorProfileSerializer,
                                  DepartmentsSerializer,
                                  DoctorProfileSerializer,
                                  LabtechProfileSerializer,
                                  NurseProfileSerializer,
                                  PatientProfileSerializer,
                                  PharmacistProfileSerializer,
                                  ReceptionistProfileSerializer,
                                  UserSerializer)
from appointments.models import Appointments, Lab_test, Medicine, Test
from appointments.serializers import patientAppointmentSerializer
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from billing.models import Invoice, Payment
from billing.serializers import InvoiceSerializer, PaymentSerializer
from rest_framework import generics, serializers, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from records.serializers import MedicineSerializer, TestSerializer


class TestAPIView(ModelViewSet):
    serializer_class = TestSerializer
    permission_classes = [IsAuthenticated, IsAdministrator]
    http_method_names = ["get", "post", "put", "delete"]

    def get_queryset(self):
        testObj = Lab_test.objects.all()
        return testObj

    def list(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        adminObj = Administrator.objects.get(user=request.user)
        serializer.save(added_by=adminObj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset, data=request.data)
        serializer.is_valid(raise_exception=True)
        adminObj = Administrator.objects.get(user=request.user)
        serializer.save(added_by=adminObj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        queryset.delete()
        return Response(
            {"message": "Test was successfully deleted."},
            status=status.HTTP_204_NO_CONTENT
        )


class MedicineAPIView(ModelViewSet):
    serializer_class = MedicineSerializer
    permission_classes = [IsAuthenticated, IsAdministrator]
    http_method_names = ["get", "post", "put", "delete"]

    def get_queryset(self):
        medObj = Medicine.objects.all()
        return medObj

    def list(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        adminObj = Administrator.objects.get(user=request.user)
        serializer.save(added_by=adminObj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset, data=request.data)
        serializer.is_valid(raise_exception=True)
        adminObj = Administrator.objects.get(user=request.user)
        serializer.save(added_by=adminObj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        queryset.delete()
        return Response(
            {"message": "Medicine was successfully deleted"},
            status=status.HTTP_204_NO_CONTENT
        )


class DepartmentAPIView(ModelViewSet):
    serializer_class = DepartmentsSerializer
    permission_classes = [IsAuthenticated, IsAdministrator]
    http_method_names = ["get", "post", "put", "delete"]

    def get_queryset(self):
        departmentObj = Departments.objects.all()
        return departmentObj

    def list(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        adminObj = Administrator.objects.get(user=request.user)
        serializer.save(added_by=adminObj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset, data=request.data)
        serializer.is_valid(raise_exception=True)
        adminObj = Administrator.objects.get(user=request.user)
        serializer.save(added_by=adminObj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        queryset.delete()
        return Response(
            {"message": "Department was successfully deleted"},
            status=status.HTTP_204_NO_CONTENT
        )


class UserAPIView(ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdministrator]
    http_method_names = ["get", "put", "delete"]

    def get_queryset(self):
        userObj = User.objects.all()
        return userObj

    def list(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        queryset.is_active = False
        queryset.save()
        return Response(
            {"message": "The user's account was successfully deactivated."},
            status=status.HTTP_204_NO_CONTENT
        )


class AdministratorAPIView(ModelViewSet):
    serializer_class = AdministratorProfileSerializer
    permission_classes = [IsAuthenticated, IsAdministrator]
    http_method_names = ["get", "put", "delete"]

    def get_queryset(self):
        adminObj = Administrator.objects.all()
        return adminObj

    def list(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        userQuery = User.objects.get(id=queryset.user.id)
        userSerializer = UserSerializer(
            userQuery, data=request.data["user"]
        )
        userSerializer.is_valid(raise_exception=True)
        userSerializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        userObj = User.objects.get(id=queryset.user.id)
        userObj.is_active = False
        userObj.save()
        return Response(
            {"message": "Account was successfully deactivated."},
            status=status.HTTP_204_NO_CONTENT)


class PharmacistAPIView(ModelViewSet):
    serializer_class = PharmacistProfileSerializer
    permission_classes = [IsAuthenticated, IsAdministrator]
    http_method_names = ["get", "put", "delete"]

    def get_queryset(self):
        pharmacistObj = Pharmacist.objects.all()
        return pharmacistObj

    def list(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        userQuery = User.objects.get(id=queryset.user.id)
        userSerializer = UserSerializer(
            userQuery, data=request.data["user"]
        )
        userSerializer.is_valid(raise_exception=True)
        userSerializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        userObj = User.objects.get(id=queryset.user.id)
        userObj.is_active = False
        userObj.save()
        return Response(
            {"message": "Account was successfully deactivated."},
            status=status.HTTP_204_NO_CONTENT)


class NurseAPIView(ModelViewSet):
    serializer_class = NurseProfileSerializer
    permission_classes = [IsAuthenticated, IsAdministrator]
    http_method_names = ["get", "put", "delete"]

    def get_queryset(self):
        nurseObj = Nurse.objects.all()
        return nurseObj

    def list(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        userQuery = User.objects.get(id=queryset.user.id)
        userSerializer = UserSerializer(
            userQuery, data=request.data["user"]
        )
        userSerializer.is_valid(raise_exception=True)
        userSerializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        userObj = User.objects.get(id=queryset.user.id)
        userObj.is_active = False
        userObj.save()
        return Response(
            {"message": "Account was successfully deactivated."},
            status=status.HTTP_204_NO_CONTENT)


class DoctorAPIView(ModelViewSet):
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsAuthenticated, IsAdministrator]
    http_method_names = ["get", "put", "delete"]

    def get_queryset(self):
        doctorQs = Doctor.objects.all()
        return doctorQs

    def list(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        userQuery = User.objects.get(id=queryset.user.id)
        userSerializer = UserSerializer(
            userQuery, data=request.data["user"]
        )
        userSerializer.is_valid(raise_exception=True)
        userSerializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        userObj = User.objects.get(id=queryset.user.id)
        userObj.is_active = False
        userObj.save()
        return Response(
            {"message": "Account was successfully deactivated."},
            status=status.HTTP_204_NO_CONTENT)


class LabtechAPIView(ModelViewSet):
    serializer_class = LabtechProfileSerializer
    permission_classes = [IsAuthenticated, IsAdministrator]
    http_method_names = ["get", "put", "delete"]

    def get_queryset(self):
        labtechObj = Labtech.objects.all()
        return labtechObj

    def list(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        userQuery = User.objects.get(id=queryset.user.id)
        userSerializer = UserSerializer(
            userQuery, data=request.data["user"]
        )
        userSerializer.is_valid(raise_exception=True)
        userSerializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        userObj = User.objects.get(id=queryset.user.id)
        userObj.is_active = False
        userObj.save()
        return Response(
            {"message": "Account was successfully deactivated."},
            status=status.HTTP_204_NO_CONTENT)


class ReceptionistAPIView(ModelViewSet):
    serializer_class = ReceptionistProfileSerializer
    permission_classes = [IsAuthenticated, IsAdministrator]
    http_method_names = ["get", "put", "delete"]

    def get_queryset(self):
        receptionistObj = Receptionist.objects.all()
        return receptionistObj

    def list(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        userQuery = User.objects.get(id=queryset.user.id)
        userSerializer = UserSerializer(
            userQuery, data=request.data["user"]
        )
        userSerializer.is_valid(raise_exception=True)
        userSerializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        userObj = User.objects.get(id=queryset.user.id)
        userObj.is_active = False
        userObj.save()
        return Response(
            {"message": "Account was successfully deactivated."},
            status=status.HTTP_204_NO_CONTENT)


class PatientAPIView(ModelViewSet):
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated,
                          IsAdministrator, IsDoctor,
                          IsNurse, IsReceptionist]
    http_method_names = ["get", "put", "delete"]

    def get_queryset(self):
        patientObj = Patient.objects.all()
        return patientObj

    def list(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        userQuery = User.objects.get(id=queryset.user.id)
        userSerializer = UserSerializer(
            userQuery, data=request.data["user"]
        )
        userSerializer.is_valid(raise_exception=True)
        userQuery.username = userSerializer.validated_data["username"]
        userQuery.full_name = userSerializer.validated_data["full_name"]
        userQuery.phone = userSerializer.validated_data["phone"]
        userQuery.is_active = userSerializer.validated_data["is_active"]
        userQuery.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        userObj = User.objects.get(id=queryset.user.id)
        userObj.is_active = False
        userObj.save()
        return Response(
            {"message": "Account was successfully deactivated."},
            status=status.HTTP_204_NO_CONTENT)


class AppointmentsAPIView(ModelViewSet):
    serializer_class = patientAppointmentSerializer
    permission_classes = [IsAuthenticated, IsAdministrator]
    http_method_names = ["get", "put", "post", "delete"]

    def get_queryset(self):
        appointmentObj = Appointments.objects.all()
        return appointmentObj

    def list(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset, data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment_date = serializer.validated_data["appointment_date"]
        departmentObj = serializer.validated_data["department"]
        if appointment_date >= datetime.now().date():
            if (queryset.status == "Completed" or
                queryset.completed == True or
                    queryset.appointment_date < datetime.now().date() or
                    queryset.expired == True):
                return Response(
                    {"message": "Appointment already completed or expired."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"message": "Appointment can't be rescheduled to a past date."},
                status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        departmentObj = serializer.validated_data["department"]
        appointment_date = serializer.validated_data["appointment_date"]
        patientObj = serializer.validated_data["patient"]
        patientQuery = Patient.objects.get(user=patientObj.user)
        print(patientQuery)
        if departmentObj.avail == True:
            if appointment_date >= datetime.now().date():
                appointmentExists = Appointments.objects.filter(
                    Q(patient=patientQuery) &
                    Q(appointment_date=appointment_date)
                    & Q(department=departmentObj))
                if appointmentExists.exists():
                    return Response(
                        {"message": "Appointment already exists."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                else:
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Appointment can't be scheduled on a past date."},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "The department is not available to patients."},
                            status=status.HTTP_400_BAD_REQUEST
                            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        queryset.status = "Cancelled"
        queryset.save()
        return Response(
            {"message", "Appointment was successfully Cancelled."},
            status=status.HTTP_204_NO_CONTENT
        )


class PaymentAPIView(ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsAdministrator]
    http_method_names = ["get", "post", "put", "delete"]

    def get_queryset(self):
        paymentObj = Payment.objects.all()
        return paymentObj

    def list(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)


class InvoiceAPIView(ModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated, IsAdministrator]
    http_method_names = ["get", "post", "put", "delete"]

    def get_queryset(self):
        invoiceObj = Invoice.objects.all()
        return invoiceObj

    def list(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)
