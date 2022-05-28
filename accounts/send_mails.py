import datetime

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.reverse import reverse
from rest_framework_simplejwt.tokens import RefreshToken


from accounts.models import User


def send_activation_mail(user_data, request):
    user = User.objects.get(email=user_data['email'])
    current_site = get_current_site(request).domain
    mail_subject = "Verify Your Account."
    to_mail = user.email
    token = RefreshToken.for_user(user).access_token
    relativeLink = reverse('api:email-verify')
    absurl = "http://"+current_site+relativeLink+"?token="+str(token)
    message = f"""
Welcome To Tabibu Hospital,

Hi {user.username},
Click on the link below to verify your account,
{absurl}

This is an automatically generated email. Please do not reply.
@{datetime.date.today().year} Tabibu| Nairobi city
    """
    email = EmailMessage(
        subject=mail_subject,
        body=message,
        to=[to_mail]
    )
    email.send()


def send_random_password_mail(user, password, request):
    to_mail = user["email"]
    current_site = get_current_site(request).domain
    mail_subject = "Account Random Password"

    message = f"""
Hello {user["username"]},

Your registration to Tabibu Health Care was successful, Credentials
are as follows:
Email: {user["email"]}
Password: {password}

Kindly, activate your account and reset your password.
If you have no prior idea of what is going on, Please disregard this email.

Thank you!
The Tabibu Health Care Team.
    """
    email = EmailMessage(
        subject=mail_subject,
        body=message,
        to=[to_mail]
    )
    email.send()


def send_password_reset_email(user_data, request):
    uidb64 = urlsafe_base64_encode(smart_bytes(user_data.id))
    token = PasswordResetTokenGenerator().make_token(user_data)
    to_mail = user_data.email
    current_site = get_current_site(request).domain
    relative_link = reverse("api:password-reset-confirm",
                            kwargs={'uidb64': uidb64,
                                    'token': token}
                            )
    absurl = "http://"+current_site+relative_link
    mail_subject = "Reset Your Password"
    message = f"""
Hello {user_data.username},

You recently requested a password reset for your Tabibu Health Care Account,
click the link below to reset it:
{absurl}

If you did not request a password reset, Please ignore this email
or reply to let us know. If clicking the link above doesn't work, copy
and paste it in a new browsers tab.

Thanks, Tabibu Team.
    """
    email = EmailMessage(
        subject=mail_subject,
        body=message,
        to=[to_mail]
    )
    email.send()
