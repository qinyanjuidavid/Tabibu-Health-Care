from rest_framework import serializers
from accounts.serializers import DepartmentsSerializer, DoctorProfileSerializer, LabtechProfileSerializer, PatientProfileSerializer, ReceptionistProfileSerializer
from appointments.models import Appointments, Test, Tests
from records.serializers import TestSerializer


class patientAppointmentSerializer(serializers.ModelSerializer):
    # department = DepartmentsSerializer(read_only=True)
    # patient = PatientProfileSerializer(read_only=True)
    doctor = DoctorProfileSerializer(read_only=True)
    receptionist = ReceptionistProfileSerializer(read_only=True)

    class Meta:
        model = Appointments
        fields = ("id", "patient", "department", "appointment_fee",
                  "appointment_date", "appointment_time", "receptionist",
                  "doctor", "notes", "findings", "expired", "status", "paid",
                  "completed", "your_message"
                  )
        read_only_fields = ("id", "appointment_fee",)
        # patients Fields---> patient,department,appointment_date,appointment_time,your_message (Ok)
        # Receptionist---> patient[No updates], department,appointment_date,appointment_time,receptionist
        # paid will occur on billing or Invoicing signals
        # Doctor---> doctor,notes,findings,completed
        # Doctor Views


class testSerializer(serializers.ModelSerializer):
    # appointment = patientAppointmentSerializer(read_only=True)
    # test = TestSerializer(read_only=True)  # Lab-test
    # lab_tech = LabtechProfileSerializer(read_only=True)

    class Meta:
        model = Test
        fields = (
            "id", "test", "price",
            "tested", "date_tested", "paid",
            "lab_tech", "results", "appointment"
        )
        read_only_fields = ("id", "price",)
    # Doctor --->appointment,test
    # labtech---> lab_tech,results,date_tested(Now),tested
    # Recepionist---> Bill(paid)


class testsSerializer(serializers.ModelSerializer):
    appointment = patientAppointmentSerializer(read_only=True)
    # test = testSerializer(read_only=True)

    class Meta:
        model = Tests
        fields = (
            "id", "test", "appointment",
            "tested", "date_tested",
            "paid"
        )
        read_only_fields = ("id",)

        # Doctor---> test, appointment
        # labtech---> date_tested,tested
        # Receptionist---> paid
