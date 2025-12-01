from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from .models import Usuario
from django.core.exceptions import ValidationError

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Adapter personalizado para contas sociais"""
    
    def pre_social_login(self, request, sociallogin):
        """
        Chamado antes do login social.
        Pode ser usado para conectar contas sociais a contas existentes.
        """
        email = sociallogin.account.extra_data.get('email')
        
        if email:
            try:
                usuario_existente = Usuario.objects.get(email=email)
                
                if not sociallogin.is_existing:
                    sociallogin.connect(request, usuario_existente)
            except Usuario.DoesNotExist:
                pass
    
    def populate_user(self, request, sociallogin, data):
        """
        Popula informações do usuário a partir dos dados da conta social.
        """
        user = super().populate_user(request, sociallogin, data)
        
        extra_data = sociallogin.account.extra_data
        
        if extra_data.get('given_name') and extra_data.get('family_name'):
            user.first_name = extra_data.get('given_name', '')
            user.last_name = extra_data.get('family_name', '')
        elif extra_data.get('name'):
            name_parts = extra_data['name'].split(' ', 1)
            user.first_name = name_parts[0]
            if len(name_parts) > 1:
                user.last_name = name_parts[1]
        
        if extra_data.get('picture'):
            user.foto_url = extra_data.get('picture')
        
        return user
    
    def save_user(self, request, sociallogin, form=None):
        """
        Salva o usuário após o login social.
        """
        user = super().save_user(request, sociallogin, form=form)
        
        return user
    
    def authentication_error(self, request, provider_id, error=None, exception=None, extra_context=None):
        """
        Manipula erros de autenticação.
        """
        messages.error(request, f"Erro ao fazer login com Google: {error}")
        return redirect('usuarios:login')

class CustomAccountAdapter(DefaultAccountAdapter):
    """Adapter personalizado para contas regulares"""
    
    def get_login_redirect_url(self, request):
        """
        Redirecionamento personalizado após login.
        """
        redirect_to = request.GET.get('next', '')
        if redirect_to:
            return redirect_to
        return super().get_login_redirect_url(request)