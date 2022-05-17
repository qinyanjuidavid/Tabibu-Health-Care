import datetime

from accounts.models import (Departments, Doctor, Patient, Receptionist,
                             TrackingModel)
from django.db import models
from django.utils.translation import gettext as _

# Create your models here.


class Appointments(TrackingModel):
    status_choices = (
        ("Admitted", "Admitted"),
        ("Cancelled", "Cancelled"),
        ("Discharged", "Discharged"),
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Treated", "Treated")
    )
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    appointment_fee = models.PositiveIntegerField(
        _("appointment fee"), default=100
    )
    department = models.ForeignKey(Departments, blank=True, null=True,
                                   on_delete=models.DO_NOTHING
                                   )
    appointment_date = models.DateField(
        _("appointment date"), default=datetime.date.today
    )
    receptionist = models.ForeignKey(
        Receptionist, blank=True, null=True,
        on_delete=models.DO_NOTHING)
    doctor = models.ForeignKey(Doctor, blank=True, null=True,
                               on_delete=models.DO_NOTHING
                               )
    notes = models.TextField(_("medical notes"),
                             blank=True, null=True, help_text="Signs  & Symptoms."
                             )
    findings = models.TextField(_("findings"), blank=True, null=True)
    expired = models.BooleanField(_("expired"), default=False)
    status = models.CharField(
        _("status"), max_length=20, choices=status_choices,
        default="Pending"
    )
    paid = models.BooleanField(_("paid"), default=False)

    def __str__(self):
        return f"{self.id}. {self.patient.user.username} {self.appointment_date}"

    class Meta:
        verbose_name_plural = "Appointments"
        ordering = ("-id",)
