from django.contrib.auth import validators
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext as _
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField


class TrackingModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class CustomerManager(BaseUserManager):
    def create_user(self, email, username, password=None, is_active=True, is_admin=False, is_staff=False, role=""):
        if not email:
            raise ValueError("Users must have an email address")
        if not password:
            raise ValueError("Users must have a password")
        if not username:
            raise ValueError("Users must have a username")
        user_obj = self.model(
            email=self.normalize_email(email),
            username=username
        )
        user_obj.set_password(password)
        user_obj.is_active = is_active
        user_obj.is_admin = is_admin
        user_obj.is_staff = is_staff
        user_obj.role = role
        user_obj.save(using=self._db)

        return user_obj

    def create_staff(self, email, username, password=None):
        user = self.create_user(
            email, username, password=password, is_active=True,
            is_staff=True, is_admin=False, role="Administrator",
        )
        return user

    def create_superuser(self, email, username, password=None):
        user = self.create_user(
            email, username, password=password, is_active=True,
            is_staff=True, is_admin=True, role="Administrator"
        )
        return user


class User(AbstractBaseUser, TrackingModel):
    username_validator = UnicodeUsernameValidator()

    Role_choices = (
        ('Administrator', 'Administrator'),
        ('Doctor', 'Doctor'),
        ('Labtech', 'Labtech'),
        ('Nurse', 'Nurse'),
        ('Patient', 'Patient'),
        ('Pharmacist', 'Pharmacist'),
        ('Receptionist', 'Receptionist'),
    )
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    full_name = models.CharField(_('full name'),
                                 max_length=150, blank=True, null=True
                                 )
    email = models.EmailField(_('email address'), unique=True, error_messages={
        'unique': ('A user with that email already exists.'),
    })
    phone = PhoneNumberField(
        _('phone number'), blank=True, null=True, max_length=27)
    role = models.CharField(_('Role'), max_length=17, choices=Role_choices)

    is_active = models.BooleanField(_('active'), default=False)
    is_admin = models.BooleanField(_('admin'), default=False)
    is_staff = models.BooleanField(_('staff'), default=False)
    timestamp = models.DateTimeField(_("timestamp"), auto_now_add=True)

    def __str__(self):
        return self.username

    objects = CustomerManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def staff(self):
        return self.staff

    @property
    def active(self):
        return self.active

    @property
    def admin(self):
        return self.admin


class Profile(models.Model):
    gender_choices = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    )
    marital_status_choices = (
        ('Married', 'Married'),
        ('Widowed', 'Widowed'),
        ('Separated', 'Separated'),
        ('Divorced', 'Divorced'),
        ('Single', 'Single'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    bio = models.TextField(_('bio'), blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics', blank=True, null=True)
    id_no = models.CharField(
        _('National ID'), max_length=58, blank=True, null=True
    )
    nationality = CountryField(
        _("Country"), max_length=57, blank_label=('Select Country'), default='KE'
    )
    town = models.CharField(_("town"), max_length=57, blank=True, null=True)
    estate = models.CharField(
        _('estate'), max_length=57, blank=True, null=True
    )
    gender = models.CharField(_('gender'), choices=gender_choices,
                              max_length=20, default="Single"
                              )
    marital_status = models.CharField(
        _('marital status'), choices=marital_status_choices, max_length=20, default="Single")
    date_of_birth = models.DateField(_('date of birth'), blank=True, null=True)
    timestamp = models.DateTimeField(_("timestamp"), auto_now_add=True)

    def __str__(self):
        return self.user.username

    class Meta:
        abstract = True


class Departments(TrackingModel):
    department = models.CharField(
        _("department name"), unique=True, max_length=57
    )
    room_number = models.CharField(
        _("room number"), max_length=15, unique=True
    )
    added_by = models.ForeignKey("Administrator", on_delete=models.CASCADE)

    def __str__(self):
        return self.department

    class Meta:
        verbose_name_plural = "Departments"


class StaffProfile(Profile):
    department = models.ForeignKey(
        Departments,
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_departments',
        blank=True, null=True
    )
    job_id = models.CharField(
        _("Job id"), max_length=30, blank=True, null=True
    )
    available = models.BooleanField(_("available"), default=False)

    class Meta:
        abstract = True


class Administrator(StaffProfile):
    pass

    def __str__(self):
        return self.user.username


class Pharmacist(StaffProfile):
    pass

    def __str__(self):
        return self.user.username


class Nurse(StaffProfile):
    pass

    def __str__(self):
        return self.user.username


class Doctor(StaffProfile):
    pass

    def __str__(self):
        return self.user.username


class Receptionist(StaffProfile):
    pass

    def __str__(self):
        return self.user.username


class Labtech(StaffProfile):
    pass

    def __str__(self):
        return self.user.username


class Patient(Profile):
    blood_group_choices = (
        ("A+", "A+"),
        ("O+", "O+"),
        ("B+", "B+"),
        ("AB+", "AB+"),
        ("A-", "A-"),
        ("O-", "O-"),
        ("B-", "B-"),
        ("AB-", "AB-"),
    )
    blood_group = models.CharField(
        _("blood group"), max_length=15, choices=blood_group_choices, default="A+")
    weight = models.FloatField(
        _("weight"), default=0.0, help_text="Enter the patients in Kgs"
    )
    height = models.FloatField(
        _("height"), default=0.0, help_text="Enter the patients in feets"
    )
    blood_pressure = models.FloatField(
        _("blood pressure"), default=0.0, help_text="Enter the patients in mmHg")
    blood_sugar = models.FloatField(
        _("blood sugar"), default=0.0, help_text="Enter the patients in mg/dl")
    allergies = models.TextField(_("allergies"), blank=True, null=True)

    def __str__(self):
        return self.user.username
