# accounts/adapters.py

import logging

from allauth.account.adapter import DefaultAccountAdapter
from django.utils.text import slugify

logger = logging.getLogger(__name__)

class AccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)

        # Force username generation at signup time if missing
        self.populate_username(request, user)

        if commit:
            user.save()
        return user

    def populate_username(self, request, user):
        logger.warning("Populate username called.")
        if getattr(user, "username", None):
            return

        email = (getattr(user, "email", "") or "").strip()
        base = slugify(email.split("@")[0]) or "user"
        candidate = base
        i = 0

        User = user.__class__
        while User.objects.filter(username=candidate).exists():
            i += 1
            candidate = f"{base}{i}"

        user.username = candidate
        