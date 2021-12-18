from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import forms
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm, forms.ModelForm):
    """форма регистрации, при необходимости можно гибко добавлять поля к регистрации"""
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class LoginForm(forms.Form):
    """форма логина. при необходимости можно добавить необходимые поля для входа"""
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'password')

