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
            paymentObj.balance = instance.appointment_fee
            paymentObj.sub_unit = instance.appointment_fee
            paymentObj.save()
            invoiceQs.total_amount = invoiceQs.Invoice_Total()
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
            balance=instance.appointment_fee,
            type="Appointment",
            total_amount=instance.Total_appointment_price()
        )
        paymentQs.quantity = 1
        paymentQs.save()


@receiver(post_save, sender=Appointments)
def cancelAppointmentPayment(sender, instance, created, *args, **kwargs):
    invoiceQs = Invoice.objects.filter(
        Q(appointment=instance),
        Q(paid=False)
    )
    if invoiceQs.exists():
        invoiceQs = invoiceQs[0]
        if instance.status == "Cancelled" and instance.paid is False:
            if invoiceQs.payment.filter(item="Appointment",
                                        appointment=instance,
                                        paid=False).exists():
                paymentQs = Payment.objects.filter(
                    appointment=instance,
                    paid=False,
                )
                for paymentQs in paymentQs:
                    invoiceQs.payment.remove(paymentQs)
                    paymentQs.delete()
                invoiceQs.delete()
            else:
                invoiceQs.delete()
    else:
        print("Doesn't Exists")


@receiver(post_save, sender=Payment)
def createInvoicePayment(sender, instance, *args, **kwargs):
    invoiceQs = Invoice.objects.filter(
        appointment__id=instance.appointment.id
    )
    if invoiceQs.exists():
        invoiceQs = invoiceQs[0]
        if invoiceQs.payment.filter(
                appointment__id=instance.appointment.id,
                item=instance.item).exists():
            invoiceQs.total_amount = invoiceQs.Invoice_Total()
            invoiceQs.invoiced_date = timezone.now()
            invoiceQs.save()
        else:
            invoiceQs.payment.add(instance)
            invoiceQs.invoiced_date = timezone.now()
            invoiceQs.total_amount = invoiceQs.Invoice_Total()
            invoiceQs.save()
    else:
        i, _ = Invoice.objects.update_or_create(
            total_amount=instance.total_amount,
            appointment=instance.appointment,
            invoiced_date=timezone.now())
        i.payment.add(instance.id)
        i.save()


@receiver(m2m_changed, sender=Invoice.payment.through)
def paymentChanged(sender, instance, action, model, pk_set, *args, **kwargs):
    print(action)
    if action == "post_add":
        qs = model.objects.get(pk__in=pk_set)
        invoiceQs = Invoice.objects.filter(
            appointment__id=qs.appointment.id
        )
        if invoiceQs.exists():
            invoiceQs = invoiceQs[0]
            if invoiceQs.payment.filter(appointment__id=qs.appointment.id,
                                        item=qs.item).exists():
                print("Exists")
                invoiceQs.total_amount = invoiceQs.Invoice_Total()
                invoiceQs.invoiced_date = timezone.now()
                invoiceQs.save()
            else:
                print("Doesn't Exists")
                invoiceQs.payment.add(qs)
                invoiceQs.invoiced = datetime.now()
                invoiceQs.total_amount = invoiceQs.Invoice_Total()
                invoiceQs.save()
        else:
            print("No Invoice")
            i, _ = Invoice.objects.update_or_create(
                total_amount=instance.total_amount,
                appointment=instance.appointment,
                invoiced_date=timezone.now()
            )
            i.payment.add(qs)
            i.save()
    elif action == "post_remove":
        qs = model.objects.get(pk__in=pk_set)
        invoiceQs = Invoice.objects.filter(
            appointment__id=qs.appointment.id
        )
        if invoiceQs.exists():
            invoiceQs = invoiceQs[0]
            invoiceQs.total_amount = invoiceQs.Invoice_Total()
            invoiceQs.invoiced_date = timezone.now()
            invoiceQs.save()


@receiver(post_save, sender=Payment)
def appointmentPayment(sender, instance, *args, **kwargs):
    appointmentQs = Appointments.objects.filter(
        id=instance.appointment.id,
    )
    if appointmentQs.exists():
        appointmentQs = appointmentQs[0]
        if Payment.objects.filter(
                item="Appointment",
                appointment=appointmentQs).exists():
            paymentObj = Payment.objects.filter(
                item="Appointment",
                appointment=appointmentQs
            )
            appointmentObj = Appointments.objects.filter(
                id=instance.appointment.id,
                appointment_fee=instance.total_amount
            )
            if (instance.type == "Appointment" and
                    instance.total_amount <= instance.paid_amount):
                paymentObj.update(paid=True, status="Completed")
                appointmentObj.update(paid=True, status="In Progress")
            elif (instance.type == "Appointment" and
                  instance.paid_amount > 0 and
                  instance.total_amount > instance.paid_amount):
                paymentObj.update(paid=False, status="Partial")
                appointmentObj.update(paid=False, status="Pending")
            elif (instance.type == "Appointment"
                  and instance.paid_amount == 0.0):
                paymentObj.update(paid=False, status="Pending")
                appointmentObj.update(paid=False, status="Pending")
