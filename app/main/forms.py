from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from .models import User

class UserLoginForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField()

    class Meta:
        model = User

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username',)

class UserProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username',)
