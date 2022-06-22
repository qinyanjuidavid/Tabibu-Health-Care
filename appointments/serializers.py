from accounts.models import Pharmacist
from rest_framework import serializers
from accounts.serializers import DepartmentsSerializer, DoctorProfileSerializer, LabtechProfileSerializer, PatientProfileSerializer, PharmacistProfileSerializer, ReceptionistProfileSerializer
from appointments.models import AmbulanceBooking, Appointments, Medication, Medication_Bag, Test, Tests
from records.serializers import MedicineSerializer, TestSerializer


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
            "lab_tech", "results", "appointment",
            "doctor"
        )
        read_only_fields = ("id", "price", "paid")
    # Doctor --->appointment,test
    # labtech---> lab_tech,results,date_tested(Now),tested
    # Recepionist---> Bill(paid)


class testsSerializer(serializers.ModelSerializer):
    appointment = patientAppointmentSerializer(read_only=True)
    test = testSerializer(read_only=True, many=True)

    class Meta:
        model = Tests
        fields = (
            "id", "test", "appointment",
            "tested", "date_tested",
            "paid"
        )
        read_only_fields = ("id", "paid")

        # Doctor---> test, appointment
        # labtech---> date_tested,tested
        # Receptionist---> paid


class medicationSerializer(serializers.ModelSerializer):
    # appointment = patientAppointmentSerializer(read_only=True)
    # medicine = MedicineSerializer(read_only=True)
    # pharmacist = PharmacistProfileSerializer(read_only=True)
    # doctor = DoctorProfileSerializer(read_only=True)

    class Meta:
        model = Medication
        fields = (
            "id", "medicine", "appointment",
            "price", "quantity", "notes", "paid",
            "duration", "doctor", "pharmacist",
            "dispenced", "prescription_date",
            "date_dispenced"
        )
        read_only_fields = ("id", "price", "paid")


class MedicationBagSerializer(serializers.ModelSerializer):
    appointment = patientAppointmentSerializer(read_only=True)
    medication = medicationSerializer(read_only=True, many=True)

    class Meta:
        model = Medication_Bag
        fields = (
            "id", "medication", "appointment",
            "paid", "dispenced"
        )
        read_only_fields = ("id", "paid")


class AmbulanceBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmbulanceBooking
        fields = ("id", "patient", "driver", "arrived"
                  "longitude", "latitude", "reason", "price",
                  "pick_up_time", "drop_off_time", "confirmed",
                  "cancelled", 'receptionist',
                  "created_at", "updated_at")
        read_only_fields = ("id",)
