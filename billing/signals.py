from re import M
from django.db.models.signals import (
    post_save, m2m_changed, pre_delete,
    pre_save, post_delete)
from django.dispatch import receiver
from appointments.models import Appointments, Medication, Medication_Bag, Test, Tests
from billing.models import Payment, Invoice
from datetime import datetime
from django.utils import timezone
from django.db.models import Q


@receiver(post_save, sender=Appointments)
def createAppointmentPayment(sender, instance, created, *args, **kwargs):
    invoiceQs = Invoice.objects.filter(
        Q(appointment=instance)
    )
    instance.paid = False
    print(instance.paid)
    instance.appointment_fee = instance.department.consultation_fee
    if invoiceQs.exists():
        invoiceQs = invoiceQs[0]
        if invoiceQs.payment.filter(
            item="Appointment",
            appointment=instance,
        ).exists():
            paymentObj = Payment.objects.get(
                appointment=instance,
                item="Appointment"
            )
            appObj = Appointments.objects.filter(id=instance.id)
            appObj.update(paid=False,
                          appointment_fee=instance.appointment_fee)
            paymentObj.total_amount = instance.Total_appointment_price()
            paymentObj.quantity = 1
            paymentObj.paid = False
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
                total_amount=instance.Total_appointment_price(),
                quantity=1
            )
            paymentQs.save()
    else:
        paymentQs, _ = Payment.objects.update_or_create(
            item="Appointment",
            appointment=instance,
            sub_unit=instance.appointment_fee,
            balance=instance.appointment_fee,
            type="Appointment",
            total_amount=instance.department.consultation_fee,
            quantity=1
        )
        paymentQs.save()


@receiver(post_save, sender=Payment)
def createInvoicePayment(sender, instance, *args, **kwargs):
    invoiceQs = Invoice.objects.filter(
        Q(appointment__id=instance.appointment.id)
    )
    if invoiceQs.exists():
        invoiceQs = invoiceQs[0]
        if invoiceQs.payment.filter(
            appointment__id=instance.appointment.id,
            item=instance.item
        ).exists():
            invoiceQs.total_amount = invoiceQs.Invoice_Total()
            invoiceQs.invoiced_date = datetime.now()
            invoiceQs.save()
        else:
            invoiceQs.payment.add(instance)
            invoiceQs.invoiced_date = datetime.now()
            invoiceQs.total_amount = invoiceQs.Invoice_Total()
            invoiceQs.save()
    else:
        i, _ = Invoice.objects.update_or_create(
            total_amount=instance.total_amount,
            appointment=instance.appointment,
            invoiced_date=datetime.now()
        )
        i.payment.add(instance.id)
        i.save()


@receiver(post_save, sender=Payment)
def appointmentPayment(sender, instance, *args, **kwargs):
    appointmentQs = Appointments.objects.filter(
        id=instance.appointment.id
    )
    if appointmentQs.exists():
        appointmentQs = appointmentQs[0]
        if Payment.objects.filter(
            item="Appointment",
            appointment=appointmentQs
        ).exists():
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
                  instance.total_amount <= instance.paid_amount):
                paymentObj.update(paid=False, status="Partial")
                appointmentObj.update(paid=False, status="Pending")
            elif (instance.type == "Appointment" and
                  instance.paid_amount == 0.0):
                paymentObj.update(paid=False, status="Pending")
                appointmentObj.update(paid=False, status="Pending")


@receiver(m2m_changed, sender=Invoice.payment.through)
def paymentChanged(sender, instance, action, model, pk_set, *args, **kwargs):
    print(action)
    if action == "post_add":
        qs = model.objects.get(
            pk__in=pk_set
        )
        invoiceQs = Invoice.objects.filter(
            appointment__id=qs.appointment.id
        )
        if invoiceQs.exists():
            invoiceQs = invoiceQs[0]
            if invoiceQs.payment.filter(
                appointment__id=qs.appointment.id,
                item=qs.item
            ).exists():
                print("Exists")
                invoiceQs.total_amount = invoiceQs.Invoice_Total()
                invoiceQs.invoiced_date = timezone.now()
                invoiceQs.save()
            else:
                print("Doesn't Exists")
                invoiceQs.payment.add(qs)
                invoiceQs.invoiced = timezone.now()
                invoiceQs.total_amount = invoiceQs.Invoice_Total()
                invoiceQs.save()
        else:
            print("No Invoice")
            i, _ = Invoice.objects.update_or_create(
                total_amount=instance.total_amount,
                appointment=instance.appointment,
                invoiced_date=timezone.now()
            )
            i.paymebt.add(qs)
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


@receiver(post_save, sender=Appointments)
def cancelAppointmentPayment(sender, instance, created, *args, **kwargs):
    invoiceQs = Invoice.objects.filter(
        Q(appointment=instance)
    )
    if invoiceQs.exists():
        invoiceQs = invoiceQs[0]
        if instance.status == "Cancelled" and instance.paid is False:
            if invoiceQs.payment.filter(
                    Q(item="Appointment"),
                    Q(appointment=instance), Q(paid=False)).exists():
                appObj = Appointments.objects.filter(
                    Q(id=instance.id),
                    Q(paid=False)
                )
                appObj.update(status="Cancelled")
                paymentQs = Payment.objects.filter(
                    Q(appointment=instance)
                )
                for payment in paymentQs:
                    invoiceQs.payment.remove(payment)
                    payment.delete()
                invoiceQs.delete()
            else:
                invoiceQs.delete()
    else:
        print("Doesn't Exists")


@receiver(post_save, sender=Test)
def createTestPayment(sender, instance, created, *args, **kwargs):
    invoiceQs = Invoice.objects.filter(
        Q(appointment=instance.appointment),
    )
    if invoiceQs.exists():
        invoiceQs = invoiceQs[0]
        if invoiceQs.payment.filter(
            item=instance.test.lab_test,
            appointment=instance.appointment,
        ).exists():
            paymentObj = Payment.objects.get(
                appointment=instance.appointment,
                item=instance.test.lab_test
            )
            paymentObj.total_amount = instance.Total_unit_Price()
            paymentObj.quantity = 1
            paymentObj.sub_unit = instance.price
            paymentObj.type = "Lab Test"
            paymentObj.save()
            invoiceQs.total_amount = invoiceQs.Invoice_Total()
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
        Q(appointment=instance.appointment)
    )
    if invoiceQs.exists():
        invoiceQs = invoiceQs[0]
        if invoiceQs.payment.filter(
            Q(appointment=instance.appointment),
            Q(item=instance.test.lab_test),
            Q(paid=False)
        ).exists():
            paymentQs = Payment.objects.filter(
                Q(appointment=instance.appointment),
                Q(item=instance.test.lab_test)
            )
            for paymentQs in paymentQs:
                invoiceQs.payment.remove(paymentQs)
                paymentQs.delete()
    else:
        paymentQs = Payment.objects.filter(
            Q(appointment=instance.appointment),
            Q(item=instance.test.lab_test),
            Q(paid=False)
        )
        for payment in paymentQs:
            payment.delete()


@receiver(post_save, sender=Appointments)
def cancelAppointmentTests(sender, instance, created, *args, **kwargs):
    testQs = Tests.objects.filter(
        Q(appointment=instance),
        Q(tested=False),
        Q(paid=False)
    )
    if testQs.exists():
        testQs = testQs[0]
        if (instance.status == "Cancelled" and instance.paid is False):
            if testQs.test.filter(
                Q(appointment=instance),
                Q(tested=False),
                Q(paid=False)
            ).exists():
                testObj = Test.objects.filter(
                    Q(appointment=instance), Q(paid=False),
                    Q(tested=False)
                )
                for test in testObj:
                    testQs.test.remove(test)
                    test.delete()
                testQs.delete()
            else:
                testQs.delete()


@receiver(post_delete, sender=Appointments)
def removeTestsOnAppointmentDelete(sender, instance, *args, **kwargs):
    testQs = Tests.objects.filter(
        Q(appointment=instance),
        Q(tested=False),
        Q(paid=False)
    )
    if testQs.exists():
        testQs = testQs[0]
        if testQs.test.filter(
            Q(appointment=instance),
            Q(tested=False),
            Q(paid=False)
        ).exists():
            testObj = Test.objects.filter(
                Q(appointment=instance), Q(tested=False),
                Q(paid=False)
            )
            for test in testObj:
                testQs.test.remove(testObj)
                testObj.delete()
            testQs.delete()
        else:
            testQs.delete()
    else:
        testObj = Test.objects.filter(
            Q(appointment=instance), Q(paid=False),
            Q(tested=False)
        )
        for test in testObj:
            test.delete()


@receiver(post_save, sender=Payment)
def testPayment(sender, instance, created, *args, **kwargs):
    testQs = Test.objects.filter(
        Q(appointment=instance),
        Q(test__lab_test=instance.item)
    )
    if testQs.exists():
        testQs = testQs[0]
        if Payment.objects.filter(
            Q(item=testQs.test.lab_test),
            Q(appointment=testQs.appointment)
        ).exists():
            paymentQuery = Payment.objects.filter(
                Q(item=testQs.test.lab_test),
                Q(appointment=testQs.appointment)
            )
            testQuery = Test.objects.filter(
                Q(appointment=instance.appointment),
                Q(test__lab_test=instance.item),
                Q(price=instance.total_amount)
            )
            if (instance.type == "Lab Test" and
                    instance.total_amount <= instance.paid_amount):
                paymentQuery.update(paid=True, status="Completed")
                testQuery.update(paid=True)
            elif (instance.type == "Lab Test" and instance.paid_amount > 0 and
                  instance.total_amount > instance.paid_amount):
                paymentQuery.update(paid=False)


def createMedicationPayment(sender, instance, created, *args, **kwargs):
    invoiceObj = Invoice.objects.filter(
        Q(appointment=instance.appointment)
    )
    if invoiceObj.exists():
        invoiceObj = invoiceObj[0]
        if invoiceObj.payment.filter(
            Q(item=instance.appointment)
        ).exists():
            paymentObj = Payment.objects.get(
                appointment=instance.appointment,
                item=instance.medicine.drug)
            paymentObj.total_amount = instance.Total_medication_price()
            paymentObj.quantity = instance.quantity
            paymentObj.sub_unit = instance.medicine.price
            paymentObj.type = "Medicine"
            paymentObj.save()
            paymentObj.total_coats = invoiceObj.Invoive_Total()
            invoiceObj.save()
        else:
            paymentObj, created = Payment.objects.get_or_create(
                itam=instance.medicine.drug,
                appointment=instance.appointment,
                type="Medicine",
                sub_unit=instance.medicine.price,
                total_amount=instance.Total_medication_price()
            )
            paymentObj.quantity = instance.quantity
            paymentObj.save()
    else:
        paymentObj, created = Payment.objects.get_or_create(
            item=instance.medicine.drug,
            appointment=instance.appointment,
            sub_unit=instance.medicine.price,
            type="Medicine",
            total_amount=instance.Total_medictaion_price()
        )
        paymentObj.quantity = instance.quantity
        paymentObj.save()


@receiver(post_delete, sender=Medication)
def removeMedicationPayment(sender, instance, *args, **kwargs):
    invoiceQs = Invoice.objects.filter(
        Q(appointment=instance.appointment),
        Q(paid=False)
    )
    if invoiceQs.exists():
        invoiceQs = invoiceQs[0]
        if invoiceQs.payment.filter(
            Q(item=instance.medicine.drug),
            Q(appointment=instance.appointment),
        ).exitsts():
            paymentObj = Payment.objects.filter(
                Q(appointment=instance.appointment),
                Q(item=instance.medicine.drug)
            )
            for paymentObj in paymentObj:
                invoiceQs.payment.remove(paymentObj)
                paymentObj.delete()
    else:
        paymentObj = Payment.objects.filter(
            Q(appointment=instance.appointment),
            Q(item=instance.medicine.drug)
        )
        for paymentObj in paymentObj:
            paymentObj.delete()


@receiver(post_save, sender=Appointments)
def cancelAppointmentMedication(sender, instance, created, *args, **kwargs):
    prescriptionQs = Medication_Bag.objects.filter(
        Q(appointment=instance),
        Q(paid=False),
        Q(dispenced=False)
    )
    if prescriptionQs.exists():
        prescriptionQs = prescriptionQs[0]
        if instance.status == "Cancelled" and instance.paid is False:
            if prescriptionQs.medication.filter(
                Q(appointment=instance), Q(dispenced=False),
                Q(paid=False)
            ).exists():
                medicationObj = Medication.objects.filter(
                    Q(appointment=instance), Q(dispenced=False),
                    Q(paid=False)
                )
                for med in medicationObj:
                    prescriptionQs.medication.remove(med)
                    med.delete()
                prescriptionQs.delete()
            else:
                prescriptionQs.delete()


@receiver(post_delete, sender=Appointments)
def removeMedication(sender, instance, *args, **kwargs):
    prescriptionObj = Medication_Bag.objects.filter(
        Q(appointment=instance), Q(paid=False),
        Q(dispenced=False)
    )
    if prescriptionObj.exists():
        prescriptionObj = prescriptionObj[0]
        if prescriptionObj.medication.filter(
            Q(appointment=instance), Q(dispenced=False),
            Q(paid=False)
        ).exists():
            medicationQs = Medication.objects.filter(
                Q(appointment=instance), Q(dispenced=False),
                Q(paid=False)
            )
            for med in medicationQs:
                prescriptionObj.medication.remove(med)
                med.delete()
            prescriptionObj.delete()
        else:
            medicationQs = Medication.objects.filter(
                Q(appointment=instance), Q(dispenced=False),
                Q(paid=False)
            )
            for med in medicationQs:
                med.delete()


@receiver(post_save, sender=Payment)
def medicationPayment(sender, instance, created, *args, **kwargs):
    medQs = Medication.objects.filter(
        Q(appointment=instance.appointment),
        Q(medicine__drug=instance.item)
    )
    if medQs.exists():
        medQs = medQs[0]
        if Payment.objects.filter(Q(item=medQs.medicine.drug),
                                  Q(appointment=medQs.appointment)).exists():
            paymentObj = Payment.objects.filter(
                Q(item=medQs.medicine.drug),
                Q(appointment=medQs.appointment)
            )
            medQuery = Medication.objects.filter(
                Q(appointment=instance.appointment),
                Q(medicine__drug=instance.item),
                Q(price=instance.sub_unit)
            )
            if (instance.type == "Medicine" and instance.total_amount <= instance.paid_amount):
                paymentObj.update(paid=True, status="Completed")
                medQuery.update(paid=True)
            elif (instance.type == "Medicine" and instance.paid_amount > 0 and
                  instance.total_amount > instance.paid_amount):
                paymentObj.update(paid=False, status="Partial")
                medQuery.update(paid=False)
            elif (instance.type == "Medicine" and instance.paid_amount == 0):
                paymentObj.update(paid=False, status="Pending")
                medQuery.update(paid=False)
    else:
        print("Medication does not exist.....")


# @receiver(post_save, sender=Test)
# def createTestPayment(sender, instance, created, *args, **kwargs):
#     invoiceQs = Invoice.objects.filter(
#         Q(appointment=instance.appointment)
#     )
#     if invoiceQs.exists():
#         invoiceQs = invoiceQs[0]
#         if invoiceQs.payment.filter(
#             Q(item=instance.test.lab_test),
#             Q(appointment=instance.appointment),
#         ).exists():
#             paymentObj = Payment.objects.get(
#                 appointment=instance.appointment,
#                 item=instance.test.lab_test
#             )
#             paymentObj.total_amount = instance.Total_unit_Price()
#             paymentObj.quantity = 1
#             paymentObj.sub_unit = instance.price
#             paymentObj.type = "Lab Test"
#             paymentObj.paid = False
#             paymentObj.save()
#             invoiceQs.total_cost = invoiceQs.Invoice_Total()
#             invoiceQs.save()
#         else:
#             paymentObj, _ = Payment.objects.update_or_create(
#                 item=instance.test.lab_test,
#                 appointment=instance.appointment,
#                 sub_unit=instance.test.price,
#                 type="Lab Test",
#                 total_amount=instance.Total_unit_Price(),
#                 quantity=instance.quantity,
#                 paid=False
#             )
#     else:
#         paymentObj, _ = Payment.objects.update_or_create(
#             item=instance.test.lab_test,
#             appointment=instance.appointment,
#             sub_unit=instance.test.price,
#             type="Lab Test",
#             total_amount=instance.Total_unit_Price(),
#             quantity=instance.quantity,
#             paid=False
#         )
    # =================================
    # # Appointment Payment ----->Progress
    # @receiver(post_save, sender=Appointments)
    # def createAppointmentPayment(sender, instance, created, **kwargs):
    #     invoiceQs = Invoice.objects.filter(
    #         Q(appointment=instance) &
    #         Q(paid=False)
    #     )
    #     if invoiceQs.exists():
    #         invoiceQs = invoiceQs[0]
    #         if invoiceQs.payment.filter(
    #                 item="Appointment",
    #                 appointment=instance,
    #                 paid=False).exists():
    #             paymentObj = Payment.objects.get(
    #                 appointment=instance,
    #                 paid=False,
    #                 item="Appointment"
    #             )
    #             paymentObj.total_amount = instance.Total_appointment_price()
    #             paymentObj.quantity = 1
    #             paymentObj.balance = instance.appointment_fee
    #             paymentObj.sub_unit = instance.appointment_fee
    #             paymentObj.save()
    #             invoiceQs.total_amount = invoiceQs.Invoice_Total()
    #             invoiceQs.save()
    #         else:
    #             paymentQs, created = Payment.objects.get_or_create(
    #                 item="Appointment",
    #                 appointment=instance,
    #                 sub_unit=instance.appointment_fee,
    #                 type="Appointment",
    #                 total_amount=instance.Total_appointment_price()
    #             )
    #             paymentQs.quantity = 1
    #             paymentQs.save()
    #     else:
    #         paymentQs, _ = Payment.objects.update_or_create(
    #             item="Appointment",
    #             appointment=instance,
    #             sub_unit=instance.appointment_fee,
    #             balance=instance.appointment_fee,
    #             type="Appointment",
    #             total_amount=instance.Total_appointment_price()
    #         )
    #         paymentQs.quantity = 1
    #         paymentQs.save()

    # @receiver(post_save, sender=Appointments)
    # def cancelAppointmentPayment(sender, instance, created, *args, **kwargs):
    #     invoiceQs = Invoice.objects.filter(
    #         Q(appointment=instance),
    #         Q(paid=False)
    #     )
    #     if invoiceQs.exists():
    #         invoiceQs = invoiceQs[0]
    #         if instance.status == "Cancelled" and instance.paid is False:
    #             if invoiceQs.payment.filter(item="Appointment",
    #                                         appointment=instance,
    #                                         paid=False).exists():
    #                 paymentQs = Payment.objects.filter(
    #                     appointment=instance,
    #                     paid=False,
    #                 )
    #                 for paymentQs in paymentQs:
    #                     invoiceQs.payment.remove(paymentQs)
    #                     paymentQs.delete()
    #                 invoiceQs.delete()
    #             else:
    #                 invoiceQs.delete()
    #     else:
    #         print("Doesn't Exists")

    # @receiver(post_save, sender=Payment)
    # def createInvoicePayment(sender, instance, *args, **kwargs):--------------->
    #     invoiceQs = Invoice.objects.filter(
    #         appointment__id=instance.appointment.id
    #     )
    #     if invoiceQs.exists():
    #         invoiceQs = invoiceQs[0]
    #         if invoiceQs.payment.filter(
    #                 appointment__id=instance.appointment.id,
    #                 item=instance.item).exists():
    #             invoiceQs.total_amount = invoiceQs.Invoice_Total()
    #             invoiceQs.invoiced_date = timezone.now()
    #             invoiceQs.save()
    #         else:
    #             invoiceQs.payment.add(instance)
    #             invoiceQs.invoiced_date = timezone.now()
    #             invoiceQs.total_amount = invoiceQs.Invoice_Total()
    #             invoiceQs.save()
    #     else:
    #         i, _ = Invoice.objects.update_or_create(
    #             total_amount=instance.total_amount,
    #             appointment=instance.appointment,
    #             invoiced_date=timezone.now())
    #         i.payment.add(instance.id)
    #         i.save()

    # @receiver(m2m_changed, sender=Invoice.payment.through)
    # def paymentChanged(sender, instance, action, model, pk_set, *args, **kwargs):---------->
    #     print(action)
    #     if action == "post_add":
    #         qs = model.objects.get(pk__in=pk_set)
    #         invoiceQs = Invoice.objects.filter(
    #             appointment__id=qs.appointment.id
    #         )
    #         if invoiceQs.exists():
    #             invoiceQs = invoiceQs[0]
    #             if invoiceQs.payment.filter(appointment__id=qs.appointment.id,
    #                                         item=qs.item).exists():
    #                 print("Exists")
    #                 invoiceQs.total_amount = invoiceQs.Invoice_Total()
    #                 invoiceQs.invoiced_date = timezone.now()
    #                 invoiceQs.save()
    #             else:
    #                 print("Doesn't Exists")
    #                 invoiceQs.payment.add(qs)
    #                 invoiceQs.invoiced = datetime.now()
    #                 invoiceQs.total_amount = invoiceQs.Invoice_Total()
    #                 invoiceQs.save()
    #         else:
    #             print("No Invoice")
    #             i, _ = Invoice.objects.update_or_create(
    #                 total_amount=instance.total_amount,
    #                 appointment=instance.appointment,
    #                 invoiced_date=timezone.now()
    #             )
    #             i.payment.add(qs)
    #             i.save()
    #     elif action == "post_remove":
    #         qs = model.objects.get(pk__in=pk_set)
    #         invoiceQs = Invoice.objects.filter(
    #             appointment__id=qs.appointment.id
    #         )
    #         if invoiceQs.exists():
    #             invoiceQs = invoiceQs[0]
    #             invoiceQs.total_amount = invoiceQs.Invoice_Total()
    #             invoiceQs.invoiced_date = timezone.now()
    #             invoiceQs.save()

    # @receiver(post_save, sender=Payment)
    # def appointmentPayment(sender, instance, *args, **kwargs):------------>
    #     appointmentQs = Appointments.objects.filter(
    #         id=instance.appointment.id,
    #     )
    #     if appointmentQs.exists():
    #         appointmentQs = appointmentQs[0]
    #         if Payment.objects.filter(
    #                 item="Appointment",
    #                 appointment=appointmentQs).exists():
    #             paymentObj = Payment.objects.filter(
    #                 item="Appointment",
    #                 appointment=appointmentQs
    #             )
    #             appointmentObj = Appointments.objects.filter(
    #                 id=instance.appointment.id,
    #                 appointment_fee=instance.total_amount
    #             )
    #             if (instance.type == "Appointment" and
    #                     instance.total_amount <= instance.paid_amount):
    #                 paymentObj.update(paid=True, status="Completed")
    #                 appointmentObj.update(paid=True, status="In Progress")
    #             elif (instance.type == "Appointment" and
    #                   instance.paid_amount > 0 and
    #                   instance.total_amount > instance.paid_amount):
    #                 paymentObj.update(paid=False, status="Partial")
    #                 appointmentObj.update(paid=False, status="Pending")
    #             elif (instance.type == "Appointment"
    #                   and instance.paid_amount == 0.0):
    #                 paymentObj.update(paid=False, status="Pending")
    #                 appointmentObj.update(paid=False, status="Pending")

    # @receiver(post_save, sender=Test)
    # def createTestPayment(sender, instance, created, *args, **kwargs):
    #     invoiceQs = Invoice.objects.filter(
    #         appointment=instance.appointment,
    #         paid=False
    #     )

    #     if invoiceQs.exists():
    #         invoiceQs = invoiceQs[0]
    #         if invoiceQs.payment.filter(
    #                 item=instance.test.lab_test,
    #                 appointment=instance.appointment,
    #                 paid=False).exists():
    #             paymentObj = Payment.objects.get(
    #                 appointment=instance.appointment,
    #                 paid=False,
    #                 item=instance.test.lab_test
    #             )
    #             paymentObj.total_amount = instance.Total_unit_Price()
    #             paymentObj.quantity = 1
    #             paymentObj.sub_unit = instance.price
    #             paymentObj.type = "Lab Test"
    #             paymentObj.save()
    #             invoiceQs.total_cost = invoiceQs.Invoice_Total()
    #             invoiceQs.save()
    #         else:
    #             paymentObj, created = Payment.objects.get_or_create(
    #                 item=instance.test.lab_test,
    #                 appointment=instance.appointment,
    #                 sub_unit=instance.price,
    #                 type="Lab Test",
    #                 total_amount=instance.Total_unit_Price()
    #             )
    #             paymentObj.quantity = 1
    #             paymentObj.save()
    #     else:
    #         paymentObj, _ = Payment.objects.update_or_create(
    #             item=instance.test.lab_test,
    #             appointment=instance.appointment,
    #             sub_unit=instance.test.price,
    #             type="Lab Test",
    #             total_amount=instance.Total_unit_Price()
    #         )
    #         paymentObj.quantity = 1
    #         paymentObj.save()

    # @receiver(post_delete, sender=Test)
    # def removeTestPayment(sender, instance, *args, **kwargs):
    #     invoiceQs = Invoice.objects.filter(
    #         appointment=instance.appointment,
    #         paid=False
    #     )
    #     if invoiceQs.exists():
    #         invoiceQs = invoiceQs[0]
    #         if invoiceQs.payment.filter(
    #                 item=instance.test.lab_test,
    #                 appointment=instance.appointment,
    #                 paid=False).exists():
    #             paymentQs = Payment.objects.filter(
    #                 appointment=instance.appointment,
    #                 paid=False,
    #                 item=instance.test.lab_test
    #             )
    #             for paymentQs in paymentQs:
    #                 invoiceQs.payment.remove(paymentQs)
    #                 paymentQs.delete()
    #     else:
    #         paymentQs = Payment.objects.filter(
    #             appointment=instance.appointment,
    #             paid=False,
    #             item=instance.test.lab_test
    #         )
    #         for payment in paymentQs:
    #             payment.delete()

    # @receiver(post_save, sender=Appointments)
    # def cancelAppointmentTests(sender, instance, created, *args, **kwargs):
    #     testQs = Tests.objects.filter(
    #         appointment=instance,
    #         tested=False,
    #         paid=False
    #     )
    #     if testQs.exists():
    #         testQs = testQs[0]
    #         if (instance.status == "Cancelled" and
    #                 instance.paid is False):
    #             if testQs.test.filter(
    #                     appointment=instance,
    #                     tested=False,
    #                     paid=False).exists():
    #                 testObj = Test.objects.filter(
    #                     appointment=instance, paid=False,
    #                     tested=False)
    #                 for test in testObj:
    #                     testQs.test.remove(test)
    #                     test.delete()
    #                 testQs.delete()
    #             else:
    #                 testQs.delete()
    # # Remove tests upon appointment deletion

    # @receiver(post_delete, sender=Appointments)
    # def removeTests(sender, instance, *args, **kwargs):
    #     testQs = Tests.objects.filter(
    #         appointment=instance,
    #         tested=False,
    #         paid=False
    #     )
    #     if testQs.exists():
    #         testQs = testQs[0]
    #         if testQs.test.filter(
    #                 appointment=instance,
    #                 tested=False,
    #                 paid=False).exists():
    #             testObj = Test.objects.filter(
    #                 appointment=instance, tested=False,
    #                 paid=False)
    #             for testObj in testObj:
    #                 testQs.test.remove(testObj)
    #                 testObj.delete()
    #             testQs.delete()
    #         else:
    #             testQs.delete()
    #     else:
    #         testObj = Test.objects.filter(
    #             appointment=instance, paid=False,
    #             tested=False
    #         )
    #         for test in testObj:
    #             test.delete()

    # # Tesr Payment

    # @receiver(post_save, sender=Payment)
    # def testPayment(sender, instance, created, *args, **kwargs):
    #     testQs = Test.objects.filter(appointment=instance.appointment,
    #                                  test__lab_test=instance.item)
    #     if testQs.exists():
    #         testQs = testQs[0]
    #         if Payment.objects.filter(
    #                 item=testQs.test.lab_test,
    #                 appointment=testQs.appointment).exists():
    #             paymentQuery = Payment.objects.filter(
    #                 item=testQs.test.lab_test,
    #                 appointment=testQs.appointment
    #             )
    #             testQuery = Test.objects.filter(
    #                 appointment=instance.appointment,
    #                 test__lab_test=instance.item,
    #                 price=instance.total_amount
    #             )
    #             if (instance.type == "Lab Test" and
    #                     instance.total_amount <= instance.paid_amount):
    #                 paymentQuery.update(paid=True, status="Completed")
    #                 testQuery.update(paid=True)
    #             elif (instance.type == "Lab Test" and instance.paid_amount > 0 and
    #                   instance.total_amount >
    #                   instance.paid_amount):
    #                 paymentQuery.update(paid=False, status="Partial")
    #                 testQuery.update(paid=False)
    #             elif (instance.type == "Lab Test" and instance.paid_amount == 0):
    #                 paymentQuery.update(paid=False, status="Pending")
    #                 testQuery.update(paid=False)

    # def createMedicationPayment(sender, instance, created, *args, **kwargs):
    #     invoiceObj = Invoice.objects.filter(
    #         appointment=instance.appointment,
    #         paid=False
    #     )
    #     if invoiceObj.exists():
    #         invoiceObj = invoiceObj[0]
    #         if invoiceObj.payment.filter(
    #                 item=instance.medicine.drug,
    #                 appointment=instance.appointment,
    #                 paid=False).exists():
    #             paymentObj = Payment.objects.get(appointment=instance.appointment,
    #                                              paid=False,
    #                                              item=instance.medicine.drug)
    #             paymentObj.total_amount = instance.Total_medication_price()
    #             paymentObj.quantity = instance.quantity
    #             paymentObj.sub_unit = instance.medicine.price
    #             paymentObj.type = "Medicine"
    #             paymentObj.save()
    #             invoiceObj.total_cost = invoiceObj.Invoice_Total()
    #             invoiceObj.save()

    #         else:
    #             paymentObj, created = Payment.objects.get_or_create(
    #                 item=instance.medicine.drug,
    #                 appointment=instance.appointment,
    #                 type="Medicine",
    #                 sub_unit=instance.medicine.price,
    #                 total_amount=instance.Total_medication_price()
    #             )
    #             paymentObj.quantity = instance.quantity
    #             paymentObj.save()
    #     else:
    #         paymentObj, created = Payment.objects.get_or_create(
    #             item=instance.medicine.drug,
    #             appointment=instance.appointment,
    #             sub_unit=instance.medicine.price,
    #             type="Medicine",
    #             total_amount=instance.Total_medication_price()
    #         )
    #         paymentObj.quantity = instance.quantity
    #         paymentObj.save()

    # @receiver(post_delete, sender=Medication)
    # def removeMedicationPayment(sender, instance, *args, **kwargs):
    #     invoiceQs = Invoice.objects.filter(
    #         appointment=instance.appointment,
    #         paid=False
    #     )
    #     if invoiceQs.exists():
    #         invoiceQs = invoiceQs[0]
    #         if invoiceQs.payment.filter(item=instance.medicine.drug,
    #                                     appointment=instance.appointment,
    #                                     paid=False).exists():
    #             paymentObj = Payment.objects.filter(
    #                 appointment=instance.appointment,
    #                 paid=False,
    #                 item=instance.medicine.drug
    #             )
    #             for paymentObj in paymentObj:
    #                 invoiceQs.payment.remove(paymentObj)
    #                 paymentObj.delete()
    #     else:
    #         paymentObj = Payment.objects.filter(
    #             appointment=instance.appointment,
    #             paid=False,
    #             item=instance.medicine.drug
    #         )
    #         for paymentObj in paymentObj:
    #             paymentObj.delete()

    # @receiver(post_save, sender=Appointments)
    # def cancelAppointmentMedication(sender, instance, created, *args, **kwargs):
    #     prescriptionQs = Medication_Bag.objects.filter(
    #         appointment=instance,
    #         paid=False,
    #         dispenced=False
    #     )
    #     if prescriptionQs.exists():
    #         prescriptionQs = prescriptionQs[0]
    #         if instance.status == "Cancelled" and instance.paid is False:
    #             if prescriptionQs.medication.filter(
    #                     appointment=instance, dispenced=False,
    #                     paid=False).exists():
    #                 medicationObj = Medication.objects.filter(
    #                     appointment=instance, dispenced=False,
    #                     paid=False
    #                 )
    #                 for med in medicationObj:
    #                     prescriptionQs.medication.remove(med)
    #                     med.delete()
    #                 prescriptionQs.delete()
    #             else:
    #                 prescriptionQs.delete()

    # # Remove medications upon Appointment deletion
    # @receiver(post_delete, sender=Appointments)
    # def removeMedication(sender, instance, *args, **kwargs):
    #     prescriptionObj = Medication_Bag.objects.filter(
    #         appointment=instance,
    #         paid=False,
    #         dispenced=False
    #     )
    #     if prescriptionObj.exists():
    #         prescriptionObj = prescriptionObj[0]
    #         if prescriptionObj.medication.filter(
    #                 appointment=instance, dispenced=False,
    #                 paid=False).exists():
    #             medicationQs = Medication.objects.filter(
    #                 appointment=instance, dispenced=False,
    #                 paid=False
    #             )
    #             for med in medicationQs:
    #                 prescriptionObj.medication.remove(med)
    #                 med.delete()
    #             prescriptionObj.delete()
    #         else:
    #             prescriptionObj.delete()
    #     else:
    #         medicationQs = Medication.objects.filter(
    #             appointment=instance, dispenced=False, paid=False
    #         )
    #         for med in medicationQs:
    #             med.delete()

    # @receiver(post_save, sender=Payment)
    # def medicationPayment(sender, instance, created, *args, **kwargs):
    #     medQs = Medication.objects.filter(
    #         appointment=instance.appointment,
    #         medicine__drug=instance.item
    #     )
    #     if medQs.exists():
    #         medQs = medQs[0]
    #         if Payment.objects.filter(item=medQs.medicine.drug,
    #                                   appointment=medQs.appointment).exists():
    #             paymentObj = Payment.objects.filter(
    #                 item=medQs.medicine.drug,
    #                 appointment=medQs.appointment
    #             )
    #             medQuery = Medication.objects.filter(
    #                 appointment=instance.appointment,
    #                 medicine__drug=instance.item,
    #                 price=instance.sub_unit
    #             )
    #             if (instance.type == "Medicine" and instance.total_amount <= instance.paid_amount):
    #                 paymentObj.update(paid=True, status="Completed")
    #                 medQuery.update(paid=True)

    #             elif (instance.type == "Medicine" and
    #                   instance.paid_amount > 0 and
    #                   instance.total_amount > instance.paid_amount):
    #                 paymentObj.update(paid=False, status="Partial")
    #                 medQuery.update(paid=False)
    #             elif (instance.type == "Medicine" and instance.paid_amoint == 0):
    #                 paymentObj.update(paid=False, status="Pending")
    #                 medQuery.update(paid=False)
    #     else:
    #         print("Medication does not exists...")
