from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import (Administrator, Doctor, Labtech, Nurse, Patient,
                             Pharmacist, Receptionist, User)


@receiver(post_save, sender=User)
def create_users(sender, instance, created, **kwargs):
    if created:
        if (instance.role == "Administrator" or
                instance.is_admin or instance.is_staff):
            Administrator.objects.update_or_create(user=instance)
        elif instance.role == "Doctor":
            Doctor.objects.update_or_create(user=instance)
        elif instance.role == "Patient":
            Patient.objects.update_or_create(user=instance)
        elif instance.role == "Receptionist":
            Receptionist.objects.update_or_create(user=instance)
        elif instance.role == "Pharmacist":
            Pharmacist.objects.update_or_create(user=instance)
        elif instance.role == "Nurse":
            Nurse.objects.update_or_create(user=instance)
        elif instance.role == "Labtech":
            Labtech.objects.update_or_create(user=instance)
