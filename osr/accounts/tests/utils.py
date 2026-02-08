# accounts/tests/utils.py
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
from django.urls import reverse

User = get_user_model()


def create_user(
    email: str = "test@example.com",
    password: str = "Passw0rd!123",
    is_staff: bool = False,
    is_superuser: bool = False,
    username: str | None = None,
):
    # If your manager still requires username, generate one from email.
    if username is None:
        username = email.split("@")[0]

    # Works for models/managers that still require username
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        is_staff=is_staff,
        is_superuser=is_superuser,
    )
    return user


def set_email_verified(user, email: str | None = None, primary: bool = True):
    """
    Mark the given user's email as verified in django-allauth.
    Required when ACCOUNT_EMAIL_VERIFICATION='mandatory' to allow login.
    """
    email = email or user.email
    ea, _ = EmailAddress.objects.get_or_create(user=user, email=email)
    ea.verified = True
    ea.primary = primary
    ea.save()
    return ea

def login_via_allauth(client, email: str, password: str):
    """
    End-to-end login through allauth's login view.
    Requires verified email when verification is mandatory.
    """
    resp = client.post(
        reverse("account_login"),
        data={"login": email, "password": password},
        follow=True,
    )
    return resp