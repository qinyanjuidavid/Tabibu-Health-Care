from ast import Is
from datetime import datetime
import re
from time import timezone

from accounts.models import Departments, Doctor, Labtech, Patient, Pharmacist, Receptionist
from accounts.permissions import (IsAdministrator, IsDoctor, IsLabtech,
                                  IsNurse, IsPatient, IsPharmacist,
                                  IsReceptionist)
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from records.serializers import MedicineSerializer, TestSerializer
from rest_framework import generics, serializers, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from appointments.models import Appointments, Lab_test, Medication, Medication_Bag, Medicine, Test, Tests
from appointments.serializers import MedicationBagSerializer, medicationSerializer, patientAppointmentSerializer, testSerializer, testsSerializer


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

    def list(self, request, *args, **kwargs):  # (Done)
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):  # (Done)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        departmentObj = serializer.validated_data["department"]
        appointment_date = serializer.validated_data["appointment_date"]
        appointment_time = serializer.validated_data["appointment_time"]
        message = serializer.validated_data["your_message"]
        print("llllllllllllllll")
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

    def retrieve(self, request, pk=None, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):  # (Done)
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
                    queryset.status = "Pending"
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

    def list(self, request, *args, **kwargs):  # (Done)
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):  # (Done)
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

    def update(self, request, pk=None, *args, **kwargs):  # (Done)
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
                    queryset.status = "Pending"
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

    def destroy(self, request, pk=None, *args, **kwargs):  # Done
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        if (queryset.paid == True or queryset.completed == True
                or queryset.status == "Completed"):
            return Response(
                {"message": "Can't cancel a paid or completed appointment."}
            )
        else:
            queryset.status = "Cancelled"
            queryset.save()
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

    def list(self, request, *args, **kwargs):  # (Done)
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):  # (Done)
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

    def list(self, request, *args, **kwargs):  # (Done)
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)
# List of tests in patients appointment
# patient appointment


class TestRecommendation(ModelViewSet):
    serializer_class = testsSerializer
    permission_classes = [IsAuthenticated, IsDoctor]
    http_method_names = ["get", "post", "delete"]
    """
    1. Creation of tests basing on the appointment,
    2. Removal of single test from the patient's test cart
    3. Removal of all the tests from the patient's test cart
    """

    def get_queryset(self):
        testsCart = Tests.objects.all()
        return testsCart

    def list(self, request, *args, **kwargs):  # (Done)
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):  # (Done)
        serializer = testSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializedTest = serializer.validated_data["test"]
        serializedAppointment = serializer.validated_data["appointment"]
        if serializedAppointment.appointment_date >= datetime.now().date():
            if serializedTest.available == True:

                recoTest, created = Test.objects.get_or_create(
                    test=serializedTest,
                    appointment=serializedAppointment,
                    doctor=Doctor.objects.get(user=request.user),
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
                    testsObj.save()
                    return Response(
                        {"message": "Test was successfully added to the appointment."},
                        status=status.HTTP_201_CREATED
                    )
            else:
                return Response(
                    {"message": "Test not been offered currently."},
                    status=status.HTTP_400_BAD_REQUEST

                )
        else:
            return Response(
                {"message": "Test can't be added to an outdated or expired appointment."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # The Doctor can remove a single test from the patients test cart

    @action(detail=True, methods=["delete"],
            permission_classes=[IsAuthenticated, IsDoctor])
    def remove_single_test(self, request, pk=None, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        cartSerializer = self.get_serializer(queryset)
        serializer = testSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializedTest = serializer.validated_data["test"]
        # serializedAppointment = serializer.validated_data["appointment"]
        serializedAppointment = queryset.appointment
        if serializedAppointment.appointment_date >= datetime.now().date():
            recoTest, created = Test.objects.get_or_create(
                test=serializedTest,
                appointment=serializedAppointment,
                price=serializedTest.price)
            if recoTest.tested == False or recoTest.paid == False:
                testsObj = Tests.objects.filter(
                    Q(appointment=serializedAppointment))
                if testsObj.exists():
                    testsObj = testsObj[0]
                    if testsObj.test.filter(
                            Q(test__id=serializedTest.id)).exists():
                        testsObj.test.remove(recoTest)
                        recoTest.delete()
                        if testsObj.test.count() < 1:
                            testsObj.delete()
                        return Response(
                            {"message": "Test was successfully removed from the patient's test cart."},
                            status=status.HTTP_200_OK)
                    else:
                        # testsObj.delete()
                        return Response(
                            {"message": "Test or appointment does not exist."},
                            status=status.HTTP_204_NO_CONTENT)
                else:
                    return Response(
                        {"message": "Test does not exist in the patient's test cart."},
                        status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(
                    {"message": "Can't remove a used or a test that has been paid for."},
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"message": "Test can't be removed from an outdated or expired appointment"},
                status=status.HTTP_400_BAD_REQUEST)
        return Response(cartSerializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        if queryset.appointment.completed == False:
            for test in queryset.test.all():
                if test.paid == False or test.tested == False:
                    test.delete()
            if queryset.test.count() > 0:
                return Response(
                    {"message": "Can't delete test cart with some paid or tested lab tests."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                queryset.delete()
                return Response(
                    {"message": "Patient's tests were successfully deleted"},
                    status=status.HTTP_204_NO_CONTENT
                )
        else:
            return Response(
                {"message": "Can't delete prescriptions of a completed appointment."},
                status=status.HTTP_204_NO_CONTENT
            )


class DoctorMedicineAPIView(ModelViewSet):
    serializer_class = MedicineSerializer
    permission_classes = [IsAuthenticated, IsDoctor]
    http_method_names = ["get", ]

    def get_queryset(self):
        medQuery = Medicine.objects.filter(
            on_stock=True
        )
        return medQuery

    def list(self, request, *args, **kwargs):  # (Done)
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MedicineRecommendation(ModelViewSet):
    serializer_class = MedicationBagSerializer
    permission_classes = [IsAuthenticated, IsDoctor]
    http_method_names = ["get", "post", "delete"]
    """
    1. Creation of medicine recommendations basing on the appointment,
    2. Quantity increament and decreament
    3. Removal of single medicine from the patients medication cart
    4. Removal of all the tests from the patients medication cart
    """

    def get_queryset(self):
        medicationCart = Medication_Bag.objects.all()
        return medicationCart

    def list(self, request, *args, **kwargs):  # (Done)
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):  # (Done)
        serializer = medicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializedMedicine = serializer.validated_data["medicine"]
        serializedAppointment = serializer.validated_data["appointment"]
        if serializedAppointment.appointment_date >= datetime.now().date():
            if serializedMedicine.on_stock == True:
                prescribedMed, created = Medication.objects.get_or_create(
                    medicine=serializedMedicine,
                    doctor=Doctor.objects.get(user=request.user),
                    appointment=serializedAppointment,
                    price=serializedMedicine.price
                )
                medCartObj = Medication_Bag.objects.filter(
                    Q(appointment=serializedAppointment)
                )
                if medCartObj.exists():
                    medCartObj = medCartObj[0]
                    if medCartObj.medication.filter(
                            Q(medicine__id=serializedMedicine.id)).exists():
                        prescribedMed.doctor = Doctor.objects.get(
                            user=request.user)
                        prescribedMed.quantity += 1
                        prescribedMed.save()
                        return Response(
                            {"message": "Medicine quantity was successfully added."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    else:
                        medCartObj.medication.add(prescribedMed)
                        return Response(
                            {"message": "Medicine was successfully added to the appointment."},
                            status=status.HTTP_201_CREATED
                        )
                else:
                    medCartObj = Medication_Bag.objects.create(
                        appointment=serializedAppointment
                    )
                    medCartObj.medication.add(prescribedMed)
                    medCartObj.save()
                    return Response(
                        {"message": "Medicine was successfully added to the prescription cart."},
                        status=status.HTTP_201_CREATED
                    )
            else:
                return Response(
                    {"message": "Medicine out of stock."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"message": "Medicine can't be prescribed using an outdated or expired appointment"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'],
            permission_classes=[IsAuthenticated, IsDoctor])
    def remove_single_medicine(self, request, pk=None, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = medicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializedMedicine = serializer.validated_data["medicine"]
        # serializedAppointment = serializer.validated_data["appointment"]
        serializedAppointment = queryset.appointment
        if serializedAppointment.appointment_date >= datetime.now().date():
            recoMed, created = Medication.objects.get_or_create(
                medicine=serializedMedicine,
                appointment=serializedAppointment,
                price=serializedMedicine.price)
            if recoMed.dispenced == False or recoMed.paid == False:
                medCartObj = Medication_Bag.objects.filter(
                    Q(appointment=serializedAppointment))
                if medCartObj.exists():
                    medCartObj = medCartObj[0]
                    if medCartObj.medication.filter(
                        Q(medicine__id=serializedMedicine.id)
                    ).exists():
                        medCartObj.medication.remove(recoMed)
                        recoMed.delete()
                        if medCartObj.medication.count() < 1:
                            medCartObj.delete()
                        return Response(
                            {"message": "Medicine was successfully removed from the patient's prescription cart."},
                            status=status.HTTP_200_OK
                        )
                else:
                    return Response(
                        {"message": "Medicine does not exist in the patient's prescription cart."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {"message": "Can't remove medicine from a dispenced or a paid prescription."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"message": "Medicine can't be removed from an outdated or expired appointment."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"message": "Medicine not available in the patient's prescription cart."},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["delete", ],
            permission_classes=[IsAuthenticated, IsDoctor])
    def decrease_medicine_quantity(self, request, pk=None, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = medicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializedMedicine = serializer.validated_data["medicine"]
        # serializedAppointment = serializer.validated_data["appointment"]
        serializedAppointment = queryset.appointment
        if serializedAppointment.appointment_date >= datetime.now().date():
            recoMed, created = Medication.objects.get_or_create(
                medicine=serializedMedicine,
                appointment=serializedAppointment,
                price=serializedMedicine.price)
            if recoMed.dispenced == False or recoMed.paid == False:
                medCartObj = Medication_Bag.objects.filter(
                    Q(appointment=serializedAppointment)
                )
                if medCartObj.exists():
                    medCartObj = medCartObj[0]
                    if medCartObj.medication.filter(
                            Q(medicine__id=serializedMedicine.id)).exists():
                        if recoMed.quantity > 1:
                            recoMed.quantity -= 1
                            recoMed.save()
                            return Response(
                                {"message": "The medicine quantity was reduced."},
                                status=status.HTTP_200_OK
                            )
                        else:
                            medCartObj.medication.remove(recoMed)
                            recoMed.delete()
                            medCartObj.delete()
                            return Response(
                                {"message": "The medicine was successfully removed"},
                                status=status.HTTP_200_OK
                            )
                else:
                    return Response(
                        {"message": "Medicine no longer exists in the prescription cart."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {"message": "Quantity can't be added to an already paid or dispenced medicine."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"message": "Medicine of an outdated or expired appointment can't be altered."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {"message": "The Medicine does not exist in the patient's prescription cart."},
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, pk=None, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        if queryset.appointment.completed == False:
            for med in queryset.medication.all():
                if med.paid == False or med.dispenced == False:
                    med.delete()
            if queryset.medication.count() > 0:
                return Response(
                    {"message": "Can't delete a prescription with some paid or dispenced medications."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                queryset.delete()
                return Response(
                    {"message": "Patient's prescription were successfully deleted."},
                    status=status.HTTP_204_NO_CONTENT
                )
        else:
            return Response(
                {"message": "Can't delete prescriptions of a completed appointment."},
                status=status.HTTP_400_BAD_REQUEST
            )


class ReceptionistTestCartAPIView(ModelViewSet):
    serializer_class = testsSerializer
    permission_classes = [IsAuthenticated, IsReceptionist]
    http_method_names = ["get", "post"]

    def get_queryset(self):
        testsQuery = Tests.objects.all()
        return testsQuery

    def list(self, request, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReceptionistTestsAPIView(ModelViewSet):
    serializer_class = testSerializer
    permission_classes = [IsAuthenticated, IsReceptionist]
    http_method_names = ["get", ]

    def get_qeuryset(self):
        testQuery = Test.objects.all()
        return testQuery

    def list(self, request, *args, **kwargs):  # (Done)
        queryset = self.get_qeuryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):  # (Done)
        queryset = self.get_qeuryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReceptionistPrescriptionAPIView(ModelViewSet):
    serializer_class = MedicationBagSerializer
    permission_classes = [IsAuthenticated, IsReceptionist]
    http_method_names = ["get", ]

    def get_queryset(self):
        prescriptionQuery = Medication_Bag.objects.all()
        return prescriptionQuery

    def list(self, request, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReceptionistMedicationAPIView(ModelViewSet):
    serializer_class = medicationSerializer
    permission_classes = [IsAuthenticated, IsReceptionist]
    http_method_names = ["get", ]

    def get_queryset(self):
        medicationQuery = Medication.objects.all()
        return medicationQuery

    def list(self, request, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LabtechTestCartAPIView(ModelViewSet):
    serializer_class = testsSerializer
    permission_classes = [IsAuthenticated, IsLabtech]
    http_method_names = ["get", ]

    def get_queryset(self):
        testCartObj = Tests.objects.filter(
            Q(paid=True)
        )
        return testCartObj

    def list(self, request, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LabtechTestsAPIView(ModelViewSet):
    serializer_class = testSerializer
    permission_classes = [IsAuthenticated, IsLabtech]
    http_method_names = ["get", "put"]

    def get_queryset(self):
        testsObj = Test.objects.filter(
            Q(paid=True)
        )
        return testsObj

    def list(self, request, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset, data=request.data)
        serializer.is_valid(raise_exception=True)
        queryset.results = serializer.validated_data["results"]
        queryset.tested = True
        queryset.lab_tech = Labtech.objects.get(user=request.user)
        queryset.date_tested = datetime.now()
        queryset.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PharmacistPrescriptionCartAPIView(ModelViewSet):
    serializer_class = MedicationBagSerializer
    permission_classes = [IsAuthenticated, IsPharmacist]
    http_method_names = ["get", ]

    def get_queryset(self):
        prescriptionCartObj = Medication_Bag.objects.filter(
            Q(paid=True)
        )
        return prescriptionCartObj

    def list(self, request, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PharmacistMedicationAPIView(ModelViewSet):
    serializer_class = medicationSerializer
    permission_classes = [IsAuthenticated, IsPharmacist]
    http_method_names = ["get", "put"]

    def get_queryset(self):
        medicationObj = Medication.objects.filter(
            Q(paid=True)
        )
        return medicationObj

    def list(self, request, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset, data=request.data)
        serializer.is_valid(raise_exception=True)
        queryset.pharmacist = Pharmacist.objects.get(user=request.user)
        queryset.duration = serializer.validated_data["duration"]
        queryset.notes = serializer.validated_data["notes"]
        queryset.dispenced = serializer.validated_data["dispenced"]
        queryset.date_dispenced = datetime.now()
        queryset.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PatientTestsCartAPIView(ModelViewSet):
    serializer_class = testsSerializer
    permission_classes = [IsAuthenticated, IsPatient]
    http_method_names = ["get", ]

    def get_queryset(self):
        patientObj = Patient.objects.get(user=self.request.user)
        testCartQuery = Tests.objects.filter(
            Q(appointment__patient=patientObj)
        )
        return testCartQuery

    def list(self, request, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PatientTestAPIView(ModelViewSet):
    serializer_class = testSerializer
    permission_classes = [IsAuthenticated, IsPatient]
    http_method_names = ["get", ]

    def get_queryset(self):
        patientObj = Patient.objects.get(user=self.request.user)
        testObj = Test.objects.filter(
            Q(appointment__patient=patientObj)
        )
        return testObj

    def list(self, request, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):  # (Done)
        queryset = self.get_queryset()
        queryset = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)
