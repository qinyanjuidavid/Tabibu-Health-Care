from rest_framework import serializers
from accounts.serializers import DepartmentsSerializer, DoctorProfileSerializer, PatientProfileSerializer, ReceptionistProfileSerializer
from appointments.models import Appointments


class patientAppointmentSerializer(serializers.ModelSerializer):
    # department = DepartmentsSerializer(read_only=True)
    patient = PatientProfileSerializer(read_only=True)
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
