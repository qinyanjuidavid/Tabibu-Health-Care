import datetime
from datetime import datetime as dt


from accounts.models import (Departments, Doctor, Patient, Receptionist,
                             TrackingModel)
from django.db import models
from django.utils.translation import gettext as _

# Create your models here.


class Appointments(TrackingModel):
    status_choices = (
        ("Cancelled", "Cancelled"),
        ("Completed", "Completed"),
        ("Pending", "Pending"),
    )
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    department = models.ForeignKey(Departments,
                                   on_delete=models.DO_NOTHING
                                   )
    appointment_fee = models.FloatField(
        _("appointment fee"), default=0.00
    )
    appointment_date = models.DateField(
        _("appointment date"), default=datetime.date.today
    )
    appointment_time = models.TimeField(
        _("appointment time"), default=dt.now().time()
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
    completed = models.BooleanField(_("completed"), default=False)
    your_message = models.TextField(
        _("your message"), help_text="Please, describe your problem.",
        blank=True, null=True)

    def __str__(self):
        return f"{self.id}. {self.patient.user.username} {self.appointment_date}"

    class Meta:
        verbose_name_plural = "Appointments"
        ordering = ("-appointment_date", "-appointment_time")
