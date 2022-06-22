import datetime
from datetime import datetime as dt
from this import d
from time import timezone


from accounts.models import (Administrator, Departments, Doctor, Driver, Patient, Pharmacist, Receptionist,
                             Labtech, TrackingModel)
from django.db import models
from django.utils.translation import gettext as _

# Create your models here.


class Appointments(TrackingModel):
    status_choices = (
        ("Cancelled", "Cancelled"),
        ("Completed", "Completed"),
        ("In Progress", "In Progress"),
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
    time = dt.now().time()
    appointment_time = models.TimeField(
        _("appointment time"), default=time
        # dt.now().time()
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

    def Total_appointment_price(self):
        return self.appointment_fee


class Lab_test(TrackingModel):
    lab_test = models.CharField(_("test"), max_length=60,
                                unique=True)
    price = models.FloatField(_("price"))
    available = models.BooleanField(_("available"), default=True)
    description = models.TextField(_("description"), blank=True,
                                   null=True)
    added_by = models.ForeignKey(Administrator, on_delete=models.CASCADE)

    def __str__(self):
        return self.lab_test

    class Meta:
        verbose_name = "Lab Test"
        verbose_name_plural = "Lab Tests"
        ordering = ["-id", ]


class Test(TrackingModel):
    test = models.ForeignKey(Lab_test, on_delete=models.DO_NOTHING)
    appointment = models.ForeignKey(
        Appointments, on_delete=models.PROTECT
    )
    price = models.FloatField(_("price"),)
    tested = models.BooleanField(_("tested"), default=False)
    date_tested = models.DateTimeField(_("date tested"),
                                       null=True, blank=True)
    paid = models.BooleanField(_("paid"), default=False)
    lab_tech = models.ForeignKey(
        Labtech, related_name="lab_technicians",
        on_delete=models.DO_NOTHING, blank=True,
        null=True
    )
    doctor = models.ForeignKey(Doctor, on_delete=models.DO_NOTHING,
                               blank=True, null=True)

    results = models.TextField(_("results"), blank=True, null=True)

    def __str__(self):
        return f"{self.appointment.id}. {self.test.lab_test}"

    def Total_unit_Price(self):
        return self.price

    class Meta:
        verbose_name_plural = "Patient Test"


class Tests(TrackingModel):
    test = models.ManyToManyField(Test, related_name="tests")
    appointment = models.OneToOneField(Appointments,
                                       on_delete=models.PROTECT)
    tested = models.BooleanField(_("tested"), default=False)
    date_tested = models.DateTimeField(_("date tested"),
                                       null=True)
    paid = models.BooleanField(_("paid"), default=False)

    def __str__(self):
        return self.appointment.patient.user.username

    def Total_price(self):
        total = 0
        for test in self.test.all():
            total += test.Total_unit_Price()
        return total

    class Meta:
        verbose_name_plural = "Tests Cart"


class Medicine(TrackingModel):
    drug = models.CharField(_("medicine name"), max_length=56,
                            unique=True)
    price = models.FloatField(_("price"))
    on_stock = models.BooleanField(_("on stock"), default=True)
    description = models.TextField(_("description"),
                                   blank=True,
                                   null=True)
    added_by = models.ForeignKey(Administrator, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.drug

    class Meta:
        verbose_name_plural = "Medicine"


class Medication(TrackingModel):
    medicine = models.ForeignKey(Medicine, on_delete=models.DO_NOTHING)
    appointment = models.ForeignKey(Appointments, on_delete=models.PROTECT)
    price = models.FloatField(_("price"))
    paid = models.BooleanField(_("paid"), default=False)
    quantity = models.PositiveIntegerField(_("quantity"), default=1)
    notes = models.TextField(
        _("prescription guidelines"), blank=True, null=True)
    duration = models.CharField(
        _("duration"), max_length=57,
        blank=True, null=True
    )
    doctor = models.ForeignKey(Doctor, on_delete=models.DO_NOTHING,
                               blank=True, null=True)
    pharmacist = models.ForeignKey(
        Pharmacist, blank=True, null=True,
        on_delete=models.DO_NOTHING
    )
    date_dispenced = models.DateTimeField(_("date dispenced"),
                                          null=True)
    prescription_date = models.DateField(
        _("prescription date"), default=datetime.date.today)
    dispenced = models.BooleanField(_("dispenced"), default=False)

    def __str__(self):
        return self.medicine.drug

    def Total_medication_price(self):
        return self.quantity*self.price

    class Meta:
        verbose_name_plural = "Prescription"


class Medication_Bag(TrackingModel):
    appointment = models.OneToOneField(Appointments, on_delete=models.PROTECT)
    medication = models.ManyToManyField(Medication, related_name="medications")
    paid = models.BooleanField(_("paid"), default=False)
    dispenced = models.BooleanField(_("dispenced"), default=False)

    def __str__(self):
        return self.appointment.patient.user.username

    def Total_Prescription_price(self):
        total = 0
        for med in self.medication.all():
            total += med.Total_medication_price()
        return total

    class Meta:
        verbose_name_plural = "Prescription Cart"


class AmbulanceBooking(TrackingModel):
    patient = models.ForeignKey(Patient,
                                on_delete=models.DO_NOTHING)
    driver = models.ForeignKey(Driver,
                               on_delete=models.DO_NOTHING)
    receptionist = models.ForeignKey(Receptionist, blank=True, null=True,
                                     on_delete=models.DO_NOTHING)
    longitude = models.FloatField(_("longitude"),
                                  default=36.817223)
    latitude = models.FloatField(_("latitude"),
                                 default=-1.286389)
    reason = models.TextField(_("reason"), blank=True,
                              null=True)
    price = models.FloatField(_("price"), blank=True,
                              null=True)
    arrived = models.BooleanField(_("arrived"),
                                  default=False)
    confirmed = models.BooleanField(_("confirmed"),
                                    default=False)
    cancelled = models.BooleanField(_("cancelled"),
                                    default=False)
    pick_up_time = models.DateTimeField(_("pick up time"),
                                        null=True)
    drop_off_time = models.DateTimeField(_("drop off time"),
                                         null=True)

    def __str__(self):
        return self.patient.user.username

    class Meta:
        ordering = ["id", ]
        verbose_name = "Ambulance Booking"
        verbose_name_plural = "Ambulance Booking"
