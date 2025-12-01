from django import forms
from django.forms import ClearableFileInput
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Usuario

class UserProfileForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=True,
        label="Confirmar Senha"
    )

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

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise ValidationError("Este e-mail já está em uso.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("As senhas não coincidem.")
        return cleaned_data

    def save(self, commit=True):
        user = super(UserProfileForm, self).save(commit=False)
        if commit:
            user.set_password(self.cleaned_data['password'])
            user.save()
        return user

class EditProfileForm(forms.ModelForm):
    current_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        label="Senha Atual"
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        label="Nova Senha"
    )
    confirm_new_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        label="Confirmar Nova Senha"
    )

    class Meta:
        model = Usuario
        fields = ['username', 'nome', 'email', 'avatar']

    avatar = forms.ImageField(
        widget=ClearableFileInput(),
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get('current_password')
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')

        if new_password and current_password:
            if not self.instance.check_password(current_password):
                raise ValidationError("A senha atual está incorreta.")
            if new_password != confirm_new_password:
                raise ValidationError("As novas senhas não coincidem.")

        return cleaned_data

    def save(self, commit=True):
        user = super(EditProfileForm, self).save(commit=False)
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
        return user
