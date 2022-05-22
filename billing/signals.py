from django.db.models.signals import (
    post_save, m2m_changed, pre_delete,
    pre_save, post_delete)
from django.dispatch import receiver
from appointments.models import Appointments
from billing.models import Payment, Invoice
from datetime import datetime
from django.utils import timezone
from django.db.models import Q


# Appointment Payment
@receiver(post_save, sender=Appointments)
def createAppointmentPayment(sender, instance, created, **kwargs):
    invoiceQs = Invoice.objects.filter(
        Q(appointment=instance) &
        Q(paid=False)
    )
    if invoiceQs.exists():
        invoiceQs = invoiceQs[0]
        if invoiceQs.payment.filter(
                item="Appointment",
                appointment=instance,
                paid=False).exists():
            paymentObj = Payment.objects.get(
                appointment=instance,
                paid=False,
                item="Appointment"
            )
            paymentObj.total_amount = instance.Total_appointment_price()
            paymentObj.quantity = 1
            paymentObj.sub_unit = instance.appointment_fee
            paymentObj.save()
            invoiceQs.total_cost = invoiceQs.Invoice_Total()
            invoiceQs.save()
        else:
            paymentQs, created = Payment.objects.get_or_create(
                item="Appointment",
                appointment=instance,
                sub_unit=instance.appointment_fee,
                type="Appointment",
                total_amount=instance.Total_appointment_price()
            )
            paymentQs.quantity = 1
            paymentQs.save()
    else:
        paymentQs, _ = Payment.objects.update_or_create(
            item="Appointment",
            appointment=instance,
            sub_unit=instance.appointment_fee,
            type="Appointment",
            total_amount=instance.Total_appointment_price()
        )
        paymentQs.quantity = 1
        paymentQs.save()
