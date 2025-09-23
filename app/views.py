from django.shortcuts import render, redirect, get_object_or_404
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login as auth_login
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from .models import Tarefa
from .forms import TarefaForm

def index(request):
    if request.user.is_authenticated:
        return redirect('inicio') 
    return render(request, "index.html")

def inicio(request):
    tarefas = Tarefa.objects.all().order_by('prazo')
    return render(request, "inicio.html", {"tarefas": tarefas})

def login(request):
    return render(request, "login.html")

def detalhar_tarefa(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, id=tarefa_id)
    return render(request, "detalhar_tarefa.html", {"tarefa": tarefa})

def nova_tarefa(request):
    if request.method == 'POST':
        form = TarefaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Tarefa criada com sucesso!")
            return redirect('inicio') 
    else:
        form = TarefaForm()

    return render(request, 'nova_tarefa.html', {'form': form})

def editar_tarefa(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, pk=tarefa_id)

    if request.method == 'POST':
        form = TarefaForm(request.POST, instance=tarefa)
        if form.is_valid():
            form.save()
            messages.success(request, "Tarefa atualizada com sucesso!")
            return redirect('detalhar_tarefa', tarefa_id=tarefa.id)
    else:
        form = TarefaForm(instance=tarefa)

    return render(request, 'editar_tarefa.html', {'form': form, 'tarefa': tarefa})

@require_POST
def excluir_tarefa(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, pk=tarefa_id)
    tarefa.delete()
    messages.success(request, "Tarefa excluída com sucesso!")
    return redirect('inicio')

@require_POST
def marcar_concluida(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, pk=tarefa_id)
    tarefa.concluida = True
    tarefa.save()
    messages.success(request, "Tarefa  marcada como concluída com sucesso!")
    return redirect('detalhar_tarefa', tarefa_id=tarefa.id)