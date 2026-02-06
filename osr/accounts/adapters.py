# accounts/adapters.py
from allauth.account.adapter import DefaultAccountAdapter
from django.utils.text import slugify

class AccountAdapter(DefaultAccountAdapter):
    def populate_username(self, request, user):
        """
        If your user model still has username required/unique,
        generate one from the email when user signs up.
        """
        if getattr(user, "username", None):
            return  # already set

        email = (getattr(user, "email", "") or "").strip()
        base = slugify(email.split("@")[0]) or "user"
        candidate = base
        i = 0

        User = user.__class__
        while User.objects.filter(username=candidate).exists():
            i += 1
            candidate = f"{base}{i}"

        user.username = candidate
