from django import forms
from django.forms.widgets import PasswordInput
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from allauth.account.forms import SignupForm as AllauthSignupForm

class SignupForm(AllauthSignupForm):
    agreed_to_tos = forms.BooleanField(
        required=True,
        label="I agree to the Terms of Service",
        error_messages={
            "required": "You must agree to the Terms of Service to create an account."
        },
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # allauth typically uses these field names:
        # - email
        # - password1, password2
        # (username may exist depending on your config)

        if "email" in self.fields:
            self.fields["email"].widget.attrs.update({
                "class": "form-control",
                "placeholder": "you@example.com",
                "autocomplete": "email",
            })

        if "password1" in self.fields:
            self.fields["password1"].widget.attrs.update({
                "class": "form-control",
                "placeholder": "Create a password",
                "autocomplete": "new-password",
            })

        if "password2" in self.fields:
            self.fields["password2"].widget.attrs.update({
                "class": "form-control",
                "placeholder": "Repeat your password",
                "autocomplete": "new-password",
            })

        self.fields["agreed_to_tos"].widget.attrs.update({
            "class": "form-check-input",
        })

    def save(self, request):
        """
        allauth calls this to create the user.
        We set agreed_to_tos on the user model here.
        """
        user = super().save(request)
        user.agreed_to_tos = True
        user.save(update_fields=["agreed_to_tos"])
        return user


class BootstrapAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Username",
            "autocomplete": "username",
        })

        self.fields["password"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Password",
            "autocomplete": "current-password",
        })

# class SignupForm(UserCreationForm):
#     agreed_to_tos = forms.BooleanField(
#         required=True,
#         label="I agree to the Terms of Service",
#         error_messages={
#             "required": "You must agree to the Terms of Service to create an account."
#         },
#     )

#     class Meta:
#         model = get_user_model()
#         fields = ("username", "email", "agreed_to_tos", "password1", "password2")

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         self.fields["username"].widget.attrs.update({
#             "class": "form-control",
#             "placeholder": "Choose a username",
#             "autocomplete": "username",
#         })

#         self.fields["email"].widget.attrs.update({
#             "class": "form-control",
#             "placeholder": "you@example.com",
#             "autocomplete": "email",
#         })

#         self.fields["password1"].widget.attrs.update({
#             "class": "form-control",
#             "placeholder": "Create a password",
#             "autocomplete": "new-password",
#         })

#         self.fields["password2"].widget.attrs.update({
#             "class": "form-control",
#             "placeholder": "Repeat your password",
#             "autocomplete": "new-password",
#         })
        
#         # ✅ Checkbox styling (IMPORTANT)
#         self.fields["agreed_to_tos"].widget.attrs.update({
#             "class": "form-check-input",
#         })

#     def clean_email(self):
#         User = get_user_model()
#         email = self.cleaned_data["email"].lower()
#         if User.objects.filter(email__iexact=email).exists():
#             raise forms.ValidationError(
#                 "An account with this email already exists."
#             )
#         return email

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
