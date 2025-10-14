from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from collections import defaultdict
from .models import Usuario, Tarefa
from .forms import CadastroUsuarioForm, TarefaForm
from .utils import gerar_calendario
import calendar

def index(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    return render(request, "index.html")


def cadastro(request):
    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            usuario = form.save()
            auth_login(request, usuario)
            return redirect('inicio')
    else:
        form = CadastroUsuarioForm()
    return render(request, "registration/cadastro.html", {"form": form})


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('password')
        user = authenticate(request, username=username, password=senha)
        if user is not None:
            auth_login(request, user)
            return redirect('inicio')
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    return render(request, "registration/login.html")


@login_required
def logout(request):
    auth_logout(request)
    return redirect('index')


@login_required
def inicio(request):
    context = gerar_calendario(request.user)
    return render(request, "inicio.html", context)


@login_required
def detalhar_tarefa(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, id=tarefa_id, usuario=request.user)
    return render(request, "tarefas/detalhar_tarefa.html", {"tarefa": tarefa})


@login_required
def nova_tarefa(request):
    if request.method == 'POST':
        form = TarefaForm(request.POST)
        if form.is_valid():
            tarefa = form.save(commit=False)
            tarefa.usuario = request.user
            tarefa.save()
            messages.success(request, "Tarefa criada com sucesso!")
            return redirect('inicio')
    else:
        form = TarefaForm()
    return render(request, 'tarefas/nova_tarefa.html', {'form': form})


@login_required
def editar_tarefa(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, pk=tarefa_id, usuario=request.user)

    if request.method == 'POST':
        form = TarefaForm(request.POST, instance=tarefa)
        if form.is_valid():
            form.save()
            messages.success(request, "Tarefa atualizada com sucesso!")
            return redirect('detalhar_tarefa', tarefa_id=tarefa.id)
    else:
        form = TarefaForm(instance=tarefa)

    return render(request, 'tarefas/editar_tarefa.html', {'form': form, 'tarefa': tarefa})


@login_required
@require_POST
def excluir_tarefa(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, pk=tarefa_id, usuario=request.user)
    tarefa.delete()
    messages.success(request, "Tarefa excluída com sucesso!")
    return redirect('inicio')


@login_required
@require_POST
def marcar_concluida(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, pk=tarefa_id, usuario=request.user)
    tarefa.concluida = True
    tarefa.save()
    messages.success(request, "Tarefa marcada como concluída!")
    return redirect('detalhar_tarefa', tarefa_id=tarefa.id)


@login_required
def alterar_status_tarefa(request, tarefa_id, novo_status):
    tarefa = get_object_or_404(Tarefa, id=tarefa_id, usuario=request.user)

    if request.method == 'POST':
        if novo_status in ['pendente', 'em_progresso', 'concluida']:
            tarefa.status = novo_status
            tarefa.save()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'id': tarefa.id,
                    'status': tarefa.status
                })

            return redirect('detalhar_tarefa', tarefa_id=tarefa.id)

    return HttpResponseForbidden("Método não permitido")

@login_required
def calendario(request):
    context = gerar_calendario(request.user)
    return render(request, "tarefas/calendario.html", context)