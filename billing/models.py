from ipaddress import ip_address
from django.db import models
from accounts.models import TrackingModel
from django.utils.translation import gettext as _


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


class MpesaPayment(TrackingModel):
    amount = models.FloatField(_("amount"))
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
    organization_balance = models.FloatField(_("organization balance"))

    class Meta:
        verbose_name = "Mpesa Payment"
        verbose_name_plural = "Mpesa Payments"

    def __str__(self):
        return self.first_name
