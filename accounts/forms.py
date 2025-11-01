from django import forms
from django.core.exceptions import ValidationError
from .models import Usuario
from django.forms import ClearableFileInput

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'nome', 'email', 'avatar', 'password']

    avatar = forms.ImageField(
        widget=ClearableFileInput(),
        required=False
    )
    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=True
    )

    def save(self, commit=True):
        user = super(UserProfileForm, self).save(commit=False)
        if commit:
            user.set_password(self.cleaned_data['password'])
            user.save()
        return user

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'nome', 'email', 'avatar']

    avatar = forms.ImageField(
        widget=ClearableFileInput(),
        required=False
    )

    def save(self, commit=True):
        user = super(EditProfileForm, self).save(commit=False)
        if commit:
            user.save()
        return user
