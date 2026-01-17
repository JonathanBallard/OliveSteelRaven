from django import forms
from .models import User
from django.forms import ModelForm
from django.forms.widgets import PasswordInput
from django.contrib.auth import get_user_model

class UserModelForm(ModelForm):
    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name", "username", "email", "password"]

