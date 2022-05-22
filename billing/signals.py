from django.db.models.signals import (
    post_save, m2m_changed, pre_delete,
    pre_save, post_delete)
from django.dispatch import receiver
from appointments.models import Appointments, Test, Tests
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


@receiver(post_save, sender=Test)
def createTestPayment(sender, instance, created, *args, **kwargs):
    invoiceQs = Invoice.objects.filter(
        appointment=instance.appointment,
        paid=False
    )

    if invoiceQs.exists():
        invoiceQs = invoiceQs[0]
        if invoiceQs.payment.filter(
                item=instance.text.lab_test,
                appointment=instance.appointment,
                paid=False).exists():
            paymentObj = Payment.objects.get(
                appointment=instance.appointment,
                paid=False,
                item=instance.test.lab_test
            )
            paymentObj.total_amount = instance.Total_unit_Price()
            paymentObj.quantity = 1
            paymentObj.sub_unit = instance.price
            paymentObj.type = "Lab Test"
            paymentObj.save()
            invoiceQs.total_cost = invoiceQs.Invoice_Total()
            invoiceQs.save()
        else:
            paymentObj, created = Payment.objects.get_or_create(
                item=instance.test.lab_test,
                appointment=instance.appointment,
                sub_unit=instance.price,
                type="Lab Test",
                total_amount=instance.Total_unit_Price()
            )
            paymentObj.quantity = 1
            paymentObj.save()
    else:
        paymentObj, _ = Payment.objects.update_or_create(
            item=instance.test.lab_test,
            appointment=instance.appointment,
            sub_unit=instance.test.price,
            type="Lab Test",
            total_amount=instance.Total_unit_Price()
        )
        paymentObj.quantity = 1
        paymentObj.save()


@receiver(post_delete, sender=Test)
def removeTestPayment(sender, instance, *args, **kwargs):
    invoiceQs = Invoice.objects.filter(
        appointment=instance.appointment,
        paid=False
    )
    if invoiceQs.exists():
        invoiceQs = invoiceQs[0]
        if invoiceQs.payment.filter(
                item=instance.test.lab_test,
                appointment=instance.appointment,
                paid=False).exists():
            paymentQs = Payment.objects.filter(
                appointment=instance.appointment,
                paid=False,
                item=instance.test.lab_test
            )
            for paymentQs in paymentQs:
                invoiceQs.payment.remove(paymentQs)
                paymentQs.delete()
    else:
        paymentQs = Payment.objects.filter(
            appointment=instance.appointment,
            paid=False,
            item=instance.test.lab_test
        )
        for payment in paymentQs:
            payment.delete()


@receiver(post_save, sender=Appointments)
def cancelAppointmentTests(sender, instance, created, *args, **kwargs):
    testQs = Tests.objects.filter(
        appointment=instance,
        tested=False,
        paid=False
    )
    if testQs.exists():
        testQs = testQs[0]
        if (instance.status == "Cancelled" and
                instance.paid is False):
            if testQs.test.filter(
                    appointment=instance,
                    tested=False,
                    paid=False).exists():
                testObj = Test.objects.filter(
                    appointment=instance, paid=False,
                    tested=False)
                for test in testObj:
                    testQs.test.remove(test)
                    test.delete()
                testQs.delete()
            else:
                testQs.delete()
# Remove tests upon appointment deletion


@receiver(post_delete, sender=Appointments)
def removeTests(sender, instance, *args, **kwargs):
    testQs = Tests.objects.filter(
        appointment=instance,
        tested=False,
        paid=False
    )
    if testQs.exists():
        testQs = testQs[0]
        if testQs.test.filter(
                appointment=instance,
                tested=False,
                paid=False).exists():
            testObj = Test.objects.filter(
                appointment=instance, tested=False,
                paid=False)
            for testObj in testObj:
                testQs.test.remove(testObj)
                testObj.delete()
            testQs.delete()
        else:
            testQs.delete()
    else:
        testObj = Test.objects.filter(
            appointment=instance, paid=False,
            tested=False
        )
        for test in testObj:
            test.delete()

# Tesr Payment


@receiver(post_save, sender=Payment)
def testPayment(sender, instance, created, *args, **kwargs):
    testQs = Test.objects.filter(appointment=instance.appointment,
                                 test__lab_test=instance.item)
    if testQs.exists():
        testQs = testQs[0]
        if Payment.objects.filter(
                item=testQs.test.lab_test,
                appointment=testQs.appointment).exists():
            paymentQuery = Payment.objects.filter(
                item=testQs.test.lab_test,
                appointment=testQs.appointment
            )
            testQuery = Test.objects.filter(
                appointment=instance.appointment,
                test__lab_test=instance.item,
                price=instance.total_amount
            )
            if (instance.type == "Lab Test" and
                    instance.total_amount <= instance.paid_amount):
                paymentQuery.update(paid=True, status="Completed")
                testQuery.update(paid=True)
            elif (instance.type == "Lab Test" and instance.paid_amount > 0 and
                  instance.total_amount >
                  instance.paid_amount):
                paymentQuery.update(paid=False, status="Partial")
                testQuery.update(paid=False)
            elif (instance.type == "Lab Test" and instance.paid_amount == 0):
                paymentQuery.update(paid=False, status="Pending")
                testQuery.update(paid=False)
