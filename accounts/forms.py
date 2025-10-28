from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Event  
from django.contrib.auth.forms import AuthenticationForm
from .models import Member, Announcement
from .models import Achievement


def no_numbers_in_username(value):
    """Disallow digits in username."""
    if any(char.isdigit() for char in value):
        raise ValidationError("Username cannot contain numbers.")



class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": "Enter your email"})
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Choose a username"}),
            "password1": forms.PasswordInput(attrs={"placeholder": "Enter password"}),
            "password2": forms.PasswordInput(attrs={"placeholder": "Confirm password"}),
        }

    def clean_username(self):
        username = self.cleaned_data.get("username")
        no_numbers_in_username(username)
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered. Try logging in.")
        return email

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "w-full border rounded-lg px-3 py-2 mt-1 focus:ring focus:ring-blue-200",
            "placeholder": "Email Address"
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "w-full border rounded-lg px-3 py-2 mt-1 focus:ring focus:ring-blue-200",
            "placeholder": "Password"
        })
    )


class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": "Update your email"})
    )

    class Meta:
        model = User
        fields = ("username", "email")
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Update username"}),
        }

    def clean_username(self):
        username = self.cleaned_data.get("username")
        no_numbers_in_username(username)
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Another account is already using this email.")
        return email

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "description", "start_datetime", "end_datetime", "location", "max_slots"]

        widgets = {
            "start_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["start_datetime"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["end_datetime"].input_formats = ["%Y-%m-%dT%H:%M"]


class MemberEditForm(forms.ModelForm):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = Member
        fields = ['user', 'student_id', 'course', 'year', 'role', 'status', 'achievements']

        widgets = {
            "role": forms.Select(),
            "membership_status": forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        
        instance = kwargs.get("instance", None)
        super().__init__(*args, **kwargs)
        if instance and instance.user:
            self.fields["first_name"].initial = instance.user.first_name
            self.fields["last_name"].initial = instance.user.last_name
            self.fields["email"].initial = instance.user.email

    def save(self, commit=True):
        member = super().save(commit=False)
        email = self.cleaned_data.get("email")
        first = self.cleaned_data.get("first_name")
        last = self.cleaned_data.get("last_name")
        if member.user:
            if email:
                member.user.email = email
            member.user.first_name = first or member.user.first_name
            member.user.last_name = last or member.user.last_name
            if commit:
                member.user.save()
        if commit:
            member.save()
        return member

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["student_id", "course", "year", "role", "status"]

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ["title", "content"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 4}),
        }

class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ['title', 'description', 'date_earned', 'certificate']
