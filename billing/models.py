from ipaddress import ip_address
from django.db import models
from accounts.models import Receptionist, TrackingModel
from django.utils.translation import gettext as _

from appointments.models import Appointments


# M-pesa Payment models
class MpesaCalls(TrackingModel):
    ip_address = models.GenericIPAddressField()
    caller = models.TextField()
    conversation_id = models.TextField()
    content = models.TextField()

    class Meta:
        verbose_name = "Mpesa Call"
        verbose_name_plural = "Mpesa Calls"


class MpesaCallBacks(TrackingModel):
    ip_address = models.GenericIPAddressField()
    caller = models.TextField()
    conversation_id = models.TextField()
    content = models.TextField()

    class Meta:
        verbose_name = "Mpesa Call Back"
        verbose_name_plural = "Mpesa Call Backs"


class Payment(TrackingModel):
    payment_status = (
        ("Completed", "Completed"),
        ("Partial", "Partial"),
        ("Pending", "Pending"),
        ("Cancelled", "Cancelled"),
    )
    payment_method_choice = (
        ("Cash", "Cash"),
        ("Credit card", "Credit card"),
        ("Jambo Pay", "Jambo Pay"),
        ("Mpesa", "Mpesa"),
        ("NHIF", "NHIF")
    )
    payment_type_choices = (
        ("Appointment", "Appointment"),
        ("Lab Test", "Lab Test"),
        ("Medicine", "Medicine"),
        ("Ward Allortment", "Ward Allortment")
    )
    item = models.CharField(_("item"), max_length=128)
    appointment = models.ForeignKey(Appointments,
                                    on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(_("quantity"), default=1)
    total_amount = models.FloatField(_("total amount"), default=0.00)
    sub_unit = models.FloatField(_("sub unit"), default=0.00)
    payment_date = models.DateTimeField(_("payment date"), null=True)
    tax_rate = models.FloatField(_("tax rate"), default=10.0)
    paid_amount = models.FloatField(_("paid amount"), default=0.00)
    balance = models.FloatField(_("balance"), default=0.00)
    status = models.CharField(
        _("status"), max_length=40, choices=payment_status,
        default="Pending"
    )
    payment_method = models.CharField(
        _("payment method"), max_length=33,
        choices=payment_method_choice
    )
    receptionist = models.ForeignKey(Receptionist, on_delete=models.DO_NOTHING,
                                     blank=True, null=True
                                     )
    payment_type = models.CharField(
        _("payment type"), max_length=15,
        choices=payment_type_choices
    )
    description = models.TextField(_("description"))
    type = models.TextField(_("type"))
    reference = models.TextField(_("reference"))
    first_name = models.CharField(
        _("first name"), max_length=100, blank=True, null=True)
    middle_name = models.CharField(
        _("middle name"), max_length=100, blank=True, null=True)
    last_name = models.CharField(
        _("last name"), max_length=100, blank=True, null=True)
    phone_number = models.CharField(_("phone"), max_length=20)
    organization_balance = models.FloatField(
        _("organization balance"), default=0.00)
    paid = models.BooleanField(_("paid"), default=False)

    def __str__(self):
        return f"{self.appointment.id}.{self.appointment.patient.user.username} - {self.item} {self.total_amount}"

    class Meta:
        verbose_name_plural = "Payments"

    def Total_Payment_amount(self, *args, **kwargs):
        return self.quantity*self.total_amount


class Invoice(TrackingModel):
    payment_status = (
        ("Complete", "Complete"),
        ("Partial", "Partial"),
        ("Pending", "Pending"),
        ("Cancelled", "Cancelled"),
    )
    payment_method_choice = (
        ("Cash", "Cash"),
        ("Credit card", "Credit card"),
        ("Jambo Pay", "Jambo Pay"),
        ("Mpesa", "Mpesa"),
        ("NHIF", "NHIF")
    )
    payment = models.ManyToManyField(
        Payment, related_name="payments"
    )
    payment_method = models.CharField(
        _("payment method"), max_length=33,
        choices=payment_method_choice
    )
    invoiced_date = models.DateTimeField(_("invoiced date"), null=True)
    total_amount = models.FloatField(_("total amount"), default=0.00)
    paid_amount = models.FloatField(_("paid amount"), default=0.00)
    balance = models.FloatField(_("balance"), default=0.00)
    appointment = models.OneToOneField(
        Appointments, on_delete=models.PROTECT, related_name="appointments"
    )
    paid = models.BooleanField(_("paid"), default=False)
    status = models.CharField(_("status"), max_length=40,
                              choices=payment_status)
    receptionist = models.ForeignKey(
        Receptionist, on_delete=models.DO_NOTHING,
        blank=True, null=True
    )

    def Invoice_Total(self, *args, **kwargs):
        total = 0
        for pay in self.payment.all():
            total += pay.Total_Payment_amount()
        self.total_amount = total
        super(Invoice, self).save(*args, **kwargs)
        return total

    def __str__(self):
        return f"{self.appointment.id}. {self.appointment.patient.user.username} - {self.total_amount}"
