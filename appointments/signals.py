from django.db.models.signals import (
    post_save, m2m_changed, pre_delete,
    pre_save, post_delete
)
from django.dispatch import receiver
from appointments.models import Appointments
from accounts.models import Departments
from datetime import datetime
from django.utils import timezone
from django.db.models import Q

# Consultation Fees


@receiver(post_save, sender=Appointments)
def generateConsultationFee(sender, instance, created, **kwargs):
    appointmentQs = Appointments.objects.filter(
        Q(id=instance.id) &
        Q(patient=instance.patient) &
        Q(appointment_date=instance.appointment_date)
    )
    if appointmentQs.exists():
        appointmentQs = appointmentQs[0]
        departmentObj = Departments.objects.filter(
            id=appointmentQs.department.id
        )
        if (appointmentQs.paid == False and
                appointmentQs.completed == False):
            departmentObj = departmentObj[0]
            appointmentObj = Appointments.objects.filter(
                Q(id=instance.id) &
                Q(patient=instance.patient) &
                Q(appointment_date=instance.appointment_date)
            )
            appointmentObj.update(
                appointment_fee=departmentObj.consultation_fee
            )
        else:
            print("Can't update price of already paid or completed Appointment")
    else:
        print("Doesn't exists")
