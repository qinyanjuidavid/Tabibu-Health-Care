from ast import Is
from datetime import datetime
import re

from accounts.models import Departments, Doctor, Patient, Receptionist
from accounts.permissions import (IsAdministrator, IsDoctor, IsLabtech,
                                  IsNurse, IsPatient, IsPharmacist,
                                  IsReceptionist)
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from records.serializers import TestSerializer
from rest_framework import generics, serializers, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from appointments.models import Appointments, Lab_test, Test, Tests
from appointments.serializers import patientAppointmentSerializer, testSerializer, testsSerializer


class PatientAppointmentsApiView(ModelViewSet):
    serializer_class = patientAppointmentSerializer
    permission_classes = [IsAuthenticated, IsPatient, ]
    http_method_names = ["get", "post", "put", "delete"]

    def get_queryset(self):
        user = self.request.user
        patientQuery = Patient.objects.get(user=user)
        appointmentQuery = Appointments.objects.filter(
            Q(patient=patientQuery)
        )
        return appointmentQuery

    def list(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        departmentObj = serializer.validated_data["department"]
        appointment_date = serializer.validated_data["appointment_date"]
        appointment_time = serializer.validated_data["appointment_time"]
        message = serializer.validated_data["your_message"]
        patientQuery = Patient.objects.get(user=request.user)
        if departmentObj.avail == True:
            if appointment_date >= datetime.now().date():
                appointmentExists = Appointments.objects.filter(
                    Q(patient=patientQuery) &
                    Q(appointment_date=appointment_date)
                    & Q(department=departmentObj))
                if appointmentExists.exists():
                    return Response(
                        {"message": "Appointment already exists"},
                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    appointment = Appointments.objects.create(
                        patient=patientQuery,
                        department=departmentObj,
                        appointment_date=appointment_date,
                        appointment_time=appointment_time,
                        your_message=message
                    )
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Appointment can't be scheduled on a past date."},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"message": "This department is not available for patients use."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
        appointment_time = serializer.validated_data["appointment_time"]
        message = serializer.validated_data["your_message"]
        department = serializer.validated_data["department"]
        if department.avail == True:
            if appointment_date >= datetime.now().date():
                if (queryset.status == "Completed" or
                        queryset.completed == True or
                            queryset.appointment_date < datetime.now().date() or
                            queryset.expired == True
                            # queryset.paid == True
                        ):
                    return Response(
                        {"message": "Appointment already completed, paid or expired."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                else:
                    queryset.appointment_date = appointment_date
                    queryset.appointment_time = appointment_time
                    # queryset.department = department
                    queryset.your_message = message
                    queryset.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"message": "Appointment can't be rescheduled to a past date."},
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"message": "Department not available for patients use."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        if (queryset.status == "Completed" or queryset.paid == True
            or queryset.completed == True
            ):
            return Response(
                {"message": "Can't cancel a paid or completed appointment."},
            )
        else:
            queryset.status = "Cancelled"
            queryset.save()
        return Response(
            {"message": "Appointment was Successfully cancelled."},
            status=status.HTTP_204_NO_CONTENT
        )


class ReceptionistApointmentApiView(ModelViewSet):
    serializer_class = patientAppointmentSerializer
    permission_classes = [IsAuthenticated, IsPatient]
    http_method_names = ["get", "post", "put", "delete"]

    def get_queryset(self):
        appointmentQuery = Appointments.objects.all()
        return appointmentQuery

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
        departmentObj = serializer.validated_data["department"]
        appointment_date = serializer.validated_data["appointment_date"]
        appointment_time = serializer.validated_data["appointment_time"]
        patientQs = serializer.validated_data["patient"]
        # paid = serializer.validated_data["paid"]
        receptionistQuery = Receptionist.objects.get(user=request.user)
        if departmentObj.avail == True:
            if appointment_date >= datetime.now().date():
                appointmentExists = Appointments.objects.filter(
                    Q(patient=patientQs) &
                    Q(appointment_date=appointment_date) &
                    Q(department=departmentObj)
                )
                if appointmentExists.exists():
                    return Response(
                        {"message": "Appointment already exists."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                else:
                    appointment = Appointments.objects.create(
                        department=departmentObj,
                        appointment_date=appointment_date,
                        appointment_time=appointment_time,
                        patient=patientQs,
                        receptionist=receptionistQuery)
                    return Response(
                        serializer.data, status=status.HTTP_201_CREATED
                    )
            else:
                return Response(
                    {"message": "Appointment can't be scheduled to a past date."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"message": "This department is not available for patients use."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset, data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment_date = serializer.validated_data["appointment_date"]
        appointment_time = serializer.validated_data["appointment_time"]
        department = serializer.validated_data["department"]
        if department.avail == True:
            if appointment_date >= datetime.now().date():
                if (queryset.completed == True or queryset.status == "Complete"
                        or queryset.expired == True):
                    return Response(
                        {"message": "Can't update a completed or expired appointment."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                else:
                    queryset.receptionist = Receptionist.objects.get(
                        user=request.user)
                    queryset.appointment_date = appointment_date
                    queryset.appointment_time = appointment_time
                    queryset.department = department
                    queryset.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"message": "Appointment can't be rescheduled to a past date."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"message": "Department not available for patients use."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        if (queryset.paid == True or queryset.completed == True
                or queryset.status == "Completed"):
            queryset.status = "Cancelled"
        else:
            return Response(
                {"message": "Can't cancel a paid or completed appointment."}
            )
        return Response(
            {"message": "Appointment was Successfully cancelled."},
            status=status.HTTP_204_NO_CONTENT
        )


class DoctorAppointmentApiView(ModelViewSet):
    serializer_class = patientAppointmentSerializer
    permission_classes = [IsAuthenticated, IsDoctor, ]
    http_method_names = ["get", "put"]

    def get_queryset(self):
        user = self.request.user
        doctorObj = Doctor.objects.get(user=user)
        appointmentQuery = Appointments.objects.filter(
            Q(paid=True) &
            Q(department=doctorObj.department)
        )
        return appointmentQuery

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
        if queryset.appointment_date >= datetime.now().date():
            if queryset.expired == False:
                queryset.doctor = Doctor.objects.get(user=request.user)
                queryset.notes = serializer.validated_data["notes"]
                queryset.findings = serializer.validated_data["findings"]
                queryset.completed = serializer.validated_data["completed"]
                queryset.save()
                return Response(serializer.data, status.HTTP_201_CREATED)
            else:
                return Response(
                    {"message": "Can't update an expired appointment."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"message": "Can't update an outdated appointment."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.data, status=status.HTTP_200_OK)


class DoctorTestAPIView(ModelViewSet):
    serializer_class = TestSerializer
    permission_classes = [IsAuthenticated, IsDoctor]
    http_method_names = ["get", ]

    def get_queryset(self):
        labTestQuery = Lab_test.objects.filter(
            available=True
        )
        return labTestQuery

    def list(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)
# List of tests in patients appointment
# patient appointment


class TestRecommendation(ModelViewSet):
    serializer_class = testsSerializer
    permission_classes = [IsAuthenticated, IsDoctor]
    http_method_names = ["get", "post", "put", "delete"]

    def get_queryset(self):
        testsCart = Tests.objects.all()
        return testsCart

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
        serializer = testSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializedTest = serializer.validated_data["test"]
        serializedAppointment = serializer.validated_data["appointment"]
        if serializedAppointment.appointment_date >= datetime.now().date():
            recoTest, created = Test.objects.get_or_create(
                test=serializedTest,
                appointment=serializedAppointment,
                price=serializedTest.price
            )
            testsObj = Tests.objects.filter(
                Q(appointment=serializedAppointment)
            )
            if testsObj.exists():
                testsObj = testsObj[0]
                if testsObj.test.filter(
                        Q(test__id=serializedTest.id)).exists():
                    recoTest.save()
                    return Response(
                        {"message": "Test already exists in the appointment."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                else:
                    testsObj.test.add(recoTest)
                    return Response(
                        {"message": "Test was successfully added to the appointment."},
                        status=status.HTTP_201_CREATED
                    )
            else:
                testsObj = Tests.objects.create(
                    appointment=serializedAppointment
                )
                testsObj.test.add(recoTest)
                return Response(
                    {"message": "Test was successfully added to the appointment."}
                )
        else:
            return Response(
                {"message": "Test can't be added to an outdated or expired appointment."}
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None, *args, **kwargs):
        pass
