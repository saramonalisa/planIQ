from django import forms
from django.forms import ClearableFileInput
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Usuario
from django.core.validators import MinLengthValidator, EmailValidator
from django.contrib.auth.password_validation import validate_password
import re

class UserProfileForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite novamente sua senha'
        }),
        required=True,
        label="Confirmar Senha",
        validators=[MinLengthValidator(8, message="A senha deve ter pelo menos 8 caracteres.")]
    )

    class Meta:
        model = Usuario
        fields = ['username', 'nome', 'email', 'avatar', 'password']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Escolha um nome de usuário'
            }),
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Seu nome completo'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'seu@email.com'
            }),
        }
        labels = {
            'username': 'Nome de Usuário',
            'nome': 'Nome de Exibição',
            'email': 'E-mail',
        }
        help_texts = {
            'username': 'Obrigatório. 150 caracteres ou menos. Letras, números e @/./+/-/_ apenas.',
        }

    avatar = forms.ImageField(
        widget=ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        required=False,
        help_text="Opcional. Tamanho máximo: 2MB."
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua senha'
        }),
        required=True,
        validators=[MinLengthValidator(8, message="A senha deve ter pelo menos 8 caracteres.")],
        help_text="Mínimo de 8 caracteres."
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if get_user_model().objects.filter(username=username).exists():
            raise ValidationError("Este nome de usuário já está em uso.")
        
        # Validação adicional para username
        if not re.match(r'^[\w.@+-]+\Z', username):
            raise ValidationError("Use apenas letras, números e os caracteres @/./+/-/_.")
        
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        
        # Validação de formato de email
        email_validator = EmailValidator(message="Informe um endereço de e-mail válido.")
        email_validator(email)
        
        if get_user_model().objects.filter(email=email).exists():
            raise ValidationError("Este e-mail já está em uso.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        
        # Validação de senha usando validadores do Django
        try:
            validate_password(password)
        except ValidationError as e:
            raise ValidationError(e.messages)
        
        return password

    def clean_nome(self):
        nome = self.cleaned_data['nome']
        if not nome.strip():
            raise ValidationError("O nome de exibição é obrigatório.")
        return nome

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        
        if avatar:
            # Verificar tamanho do arquivo (2MB máximo)
            max_size = 2 * 1024 * 1024  # 2MB
            if avatar.size > max_size:
                raise ValidationError("A imagem deve ter no máximo 2MB.")
            
            # Verificar extensão do arquivo
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
            import os
            ext = os.path.splitext(avatar.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError("Formato de imagem não suportado. Use JPG, PNG ou GIF.")
        
        return avatar

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("As senhas não coincidem.")
        
        # Verificar se todos os campos obrigatórios estão preenchidos
        required_fields = ['username', 'nome', 'email', 'password', 'confirm_password']
        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, "Este campo é obrigatório.")
        
        return cleaned_data

    def save(self, commit=True):
        user = super(UserProfileForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
            
            # Salvar avatar se fornecido
            if 'avatar' in self.cleaned_data and self.cleaned_data['avatar']:
                user.avatar = self.cleaned_data['avatar']
                user.save()
        
        return user

class EditProfileForm(forms.ModelForm):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        label="Senha Atual",
        help_text="Necessária apenas se desejar alterar a senha."
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        label="Nova Senha",
        validators=[MinLengthValidator(8, message="A senha deve ter pelo menos 8 caracteres.")]
    )
    confirm_new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        label="Confirmar Nova Senha"
    )

    class Meta:
        model = Usuario
        fields = ['username', 'nome', 'email', 'avatar']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    avatar = forms.ImageField(
        widget=ClearableFileInput(attrs={'class': 'form-control'}),
        required=False
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        # Verificar se o email já existe, exceto para o usuário atual
        qs = get_user_model().objects.filter(email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Este e-mail já está em uso.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get('current_password')
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')

        if new_password:
            if not current_password:
                raise ValidationError("Para alterar a senha, informe a senha atual.")
            
            if not self.instance.check_password(current_password):
                raise ValidationError("A senha atual está incorreta.")
            
            if new_password != confirm_new_password:
                raise ValidationError("As novas senhas não coincidem.")
            
            # Validar a nova senha
            try:
                validate_password(new_password, self.instance)
            except ValidationError as e:
                raise ValidationError(e.messages)

        return cleaned_data

    def save(self, commit=True):
        user = super(EditProfileForm, self).save(commit=False)
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
        return user