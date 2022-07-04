from django.db import models
from accounts.models import Administrator, TrackingModel
from django.utils.translation import gettext as _
from phonenumber_field.modelfields import PhoneNumberField
from appointments.models import Appointments


class Ward(TrackingModel):
    gender_choices = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    ward_type_choices = (
        ("Causality ward", "Causality ward"),
        ("General ward", "General ward"),
        ("Critical Care Unit", "Critical Care Unit"),
        ("Intensive Care Unit", "Intensive Care Unit"),
    )
    ward_name = models.CharField(
        _("ward name"), max_length=56,
        unique=True
    )
    ward_type = models.CharField(
        _("ward type"),
        max_length=56,
        choices=ward_type_choices)
    gender = models.CharField(
        _("gender"), max_length=57,
        choices=gender_choices
    )
    added_by = models.ForeignKey(Administrator, blank=True,
                                 on_delete=models.DO_NOTHING,
                                 null=True)

    def __str__(self):
        return self.ward_name

    class Meta:
        verbose_name_plural = "Wards"


class Rooms(TrackingModel):
    room_type_choices = (
        ("Single Room", "Single Room"),
        ("Twin-Shared Room", "Twin-Shared Room"),
        ("Multi-Bed Room", "Multi-Bed Room")
    )
    room_number = models.CharField(
        _("room number"), max_length=56
    )
    room_type = models.CharField(_("room type"),
                                 max_length=57,
                                 choices=room_type_choices)
    ward = models.ForeignKey(Ward, on_delete=models.PROTECT)
    added_by = models.ForeignKey(Administrator,
                                 on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.room_number

    class Meta:
        verbose_name_plural = "Rooms"
        ordering = ["-id"]


class Slot(TrackingModel):
    bed_number = models.CharField(_("bed number"),
                                  max_length=57)
    room = models.ForeignKey(Rooms, on_delete=models.PROTECT)
    price_per_night = models.FloatField(default=0.00)
    added_by = models.ForeignKey(Administrator,
                                 on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.bed_number

    class Meta:
        verbose_name_plural = "Slots"
        ordering = ["-id"]


class WardBooking(TrackingModel):
    nok_relationship_choices = (
        ("", "")
    )  # Parent,Spouse,Friend,Relative,gurdian,sibling
    slot = models.CharField(
        _("slot"), max_length=27)
    appointment = models.ForeignKey(
        Appointments,
        on_delete=models.CASCADE)
    admission_date = models.DateTimeField(
        _("admission date"),
        null=True)
    date_expected_to_leave = models.DateTimeField(
        _("date expected to leave"),
        null=True)
    discharge_date = models.DateTimeField(
        _("discharge date"),
        null=True)
    total_amount = models.FloatField(
        _("total amount"),
        default=0.00)
    nok_full_name = models.CharField(
        _("NOK full names"),
        max_length=109)
    relationship = models.CharField(
        _("relationship"),
        max_length=57,
        choices=nok_relationship_choices)
    nok_phone = PhoneNumberField(
        _('NOK phone number'), unique=True,
        blank=True, null=True, max_length=27)
    on_waiting_list = models.BooleanField(
        _("on waiting list"), default=False)

    def __str__(self):
        return self.appointment.patient.user.username

    class Meta:
        verbose_name_plural = "Ward Booking"
        ordering = ["-id"]
