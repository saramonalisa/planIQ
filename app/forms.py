from django import forms
from django.core.exceptions import ValidationError
from tinymce.widgets import TinyMCE
from .models import Usuario, Tarefa
from .profile import Profile

class CadastroUsuarioForm(forms.ModelForm):
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password_confirm = forms.CharField(
        label='Confirme a senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Usuario
        fields = ['username', 'nome', 'email', 'avatar', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Usuario.objects.filter(username=username).exists():
            raise ValidationError("Este nome de usuário já está em uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError("Este e-mail já está em uso.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get('password')
        confirmacao = cleaned_data.get('password_confirm')

        if senha and confirmacao and senha != confirmacao:
            self.add_error('password_confirm', "As senhas não coincidem.")


class TarefaForm(forms.ModelForm):
    
    class Meta:
        model = Tarefa
        fields = ['titulo', 'prazo', 'descricao', 'prioridade', 'notificacoes']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o título da tarefa'}),
            'prazo': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'descricao': TinyMCE(attrs={
                'cols': 80,
                'rows': 10,
                'placeholder': 'Descreva os detalhes da tarefa (opcional)'
            }),
            'prioridade': forms.Select(attrs={'class': 'form-control'}),
            'notificacoes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'prazo'):
            self.fields['prazo'].initial = self.instance.prazo 

    def save(self, commit=True):
        tarefa = super().save(commit=False)
        
        if not tarefa.status:
            tarefa.status = 'pendente'
        
        if commit:
            tarefa.save()
        return tarefa
    
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo', 'bio']

class UserForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'nome', 'avatar']