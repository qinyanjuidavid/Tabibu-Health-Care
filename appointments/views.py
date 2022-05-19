from datetime import datetime
from accounts.permissions import (IsAdministrator, IsDoctor, IsLabtech,
                                  IsNurse, IsPatient, IsPharmacist,
                                  IsReceptionist)
from django.shortcuts import render, get_object_or_404
from appointments.models import Appointments
from rest_framework import generics, serializers, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from appointments.serializers import patientAppointmentSerializer
from accounts.models import (Patient, Doctor, Departments, Receptionist)
from django.db.models import Q


class PatientAppointmentsApiView(ModelViewSet):
    serializer_class = patientAppointmentSerializer
    permission_classes = [IsAuthenticated, IsPatient, ]
    http_method_names = ["get", "post", "put"]

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
                return Response({"error": "Appointment date is invalid"},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"message": "This department is not available"},
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
        if appointment_date >= datetime.now().date():
            queryset.appointment_date = appointment_date
            queryset.appointment_time = appointment_time
            queryset.your_message = message
            queryset.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"message": "Appointment can't be rescheduled to a past date."},
                status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)
