from django import forms
from django.forms.widgets import PasswordInput
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

class UserModelForm(UserCreationForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name", "username", "email", "password1", "password2"]

class UserLoginForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ["username", "password"]

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name", "email"]
