from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.contrib import messages
from django.utils import timezone
from django.db.models import Case, When, Value, IntegerField
from collections import defaultdict
from .models import Usuario
from .forms import UserProfileForm, EditProfileForm
from django.http import HttpResponse

def cadastro(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data['password'])
            usuario.save()
            return redirect('app:home')
    else:
        form = UserProfileForm()
    return render(request, 'profile/cadastro.html', {'form': form})


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('app:home')
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    return render(request, "profile/login.html")


@login_required
def logout(request):
    auth_logout(request)
    return redirect('app:index')


@login_required
def editar_perfil(request):
    usuario = request.user

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('accounts:configuracoes')
    else:
        form = EditProfileForm(instance=usuario)

    return render(request, 'profile/configuracoes.html', {'form': form})