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
from .models import Usuario, Tarefa
from .forms import CadastroUsuarioForm, TarefaForm
from .utils import gerar_calendario
from datetime import date
import calendar
from .profile import Profile
from django.http import HttpResponse

def index(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    return render(request, "index.html")


def cadastro(request):
    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data['password'])
            usuario.save()
            return redirect('inicio')
    else:
        form = CadastroUsuarioForm()
    return render(request, 'registration/cadastro.html', {'form': form})


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

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
    hoje = timezone.localdate()
    ano = request.GET.get('ano')
    mes = request.GET.get('mes')

    try:
        ano = int(ano)
    except (TypeError, ValueError):
        ano = hoje.year

    try:
        mes = int(mes)
    except (TypeError, ValueError):
        mes = hoje.month

    if mes < 1:
        mes = 12
        ano -= 1
    elif mes > 12:
        mes = 1
        ano += 1

    context = gerar_calendario(request.user, ano=ano, mes=mes)

    # 🔽 Aqui a separação das tarefas por status
    tarefas_pendentes = Tarefa.objects.filter(usuario=request.user, status='pendente').annotate(
        prioridade_order=Case(
            When(prioridade='alta', then=Value(1)),
            When(prioridade='media', then=Value(2)),
            When(prioridade='baixa', then=Value(3)),
            default=Value(4),
            output_field=IntegerField()
        )
    ).order_by('prioridade_order')

    tarefas_andamento = Tarefa.objects.filter(usuario=request.user, status='em_progresso').annotate(
        prioridade_order=Case(
            When(prioridade='alta', then=Value(1)),
            When(prioridade='media', then=Value(2)),
            When(prioridade='baixa', then=Value(3)),
            default=Value(4),
            output_field=IntegerField()
        )
    ).order_by('prioridade_order')

    tarefas_concluidas = Tarefa.objects.filter(usuario=request.user, status='concluida').annotate(
        prioridade_order=Case(
            When(prioridade='alta', then=Value(1)),
            When(prioridade='media', then=Value(2)),
            When(prioridade='baixa', then=Value(3)),
            default=Value(4),
            output_field=IntegerField()
        )
    ).order_by('prioridade_order')

    # Atualiza o contexto que vai pro HTML
    context.update({
        'tarefas_pendentes': tarefas_pendentes,
        'tarefas_andamento': tarefas_andamento,
        'tarefas_concluidas': tarefas_concluidas,
        'ano': ano,
        'mes': mes
    })

    return render(request, "inicio.html", context)


@login_required
def detalhar_tarefa(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, id=tarefa_id, usuario=request.user)
    return render(request, "tarefas/detalhar_tarefa.html", {"tarefa": tarefa})


@login_required
def minhas_tarefas(request):
    tarefas = Tarefa.objects.filter(usuario=request.user).annotate(
        prioridade_order=Case(
            When(prioridade='alta', then=Value(1)),
            When(prioridade='media', then=Value(2)),
            When(prioridade='baixa', then=Value(3)),
            default=Value(4),
            output_field=IntegerField()
        )
    ).order_by('prioridade_order')
    return render(request, "tarefas/minhas_tarefas.html", {"tarefas": tarefas})


@login_required
def tarefas_do_dia(request, ano, mes, dia):
    data_escolhida = date(ano, mes, dia)
    tarefas = Tarefa.objects.filter(
        usuario=request.user,
        prazo=data_escolhida
    ).annotate(
        prioridade_order=Case(
            When(prioridade='alta', then=Value(1)),
            When(prioridade='media', then=Value(2)),
            When(prioridade='baixa', then=Value(3)),
            default=Value(4),
            output_field=IntegerField()
        )
    ).order_by('prioridade_order')

    context = {
        'data': data_escolhida,
        'tarefas': tarefas,
        'ano': ano,
        'mes': mes,
        'mes_nome': gerar_calendario(request.user)['mes_nome'],
        'semanas': gerar_calendario(request.user)['semanas'],
        'tarefas_por_dia': gerar_calendario(request.user)['tarefas_por_dia']
    }

    return render(request, 'tarefas/tarefas_do_dia.html', context)

    

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
            for field in form:
                for error in field.errors:
                    messages.error(request, f"{field.label}: {error}")
    else:
        form = TarefaForm()

    return render(request, 'tarefas/nova_tarefa.html', {'form': form})


@login_required
def editar_tarefa(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, id=tarefa_id)

    if request.method == 'POST':
        form = TarefaForm(request.POST, instance=tarefa)
        if form.is_valid():
            form.save()
            messages.success(request, "Tarefa editada com sucesso!")
            return redirect('detalhar_tarefa', tarefa_id=tarefa.id)
        else:
            for field in form:
                for error in field.errors:
                    messages.error(request, f"{field.label}: {error}")
    else:
        form = TarefaForm(instance=tarefa)

    return render(request, 'tarefas/editar_tarefa.html', {
    'form': form,
    'tarefa': tarefa,  # aqui dentro do dicionário
})


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
@require_POST
def alterar_status_tarefa(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, id=tarefa_id, usuario=request.user)
    novo_status = request.POST.get('status')

    if novo_status in ['pendente', 'em_progresso', 'concluida']:
        tarefa.status = novo_status
        tarefa.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'id': tarefa.id,
                'status': tarefa.status
            })

        referer = request.META.get('HTTP_REFERER')
        return redirect(referer or 'inicio')

    return HttpResponseForbidden("Status inválido")


@login_required
def alterar_prioridade_tarefa(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, id=tarefa_id, usuario=request.user)
    nova_prioridade = request.POST.get('prioridade')

    if nova_prioridade in ['alta', 'media', 'baixa', 'sem_prioridade']:
        tarefa.prioridade = nova_prioridade
        tarefa.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'id': tarefa.id,
                'prioridade': tarefa.prioridade
            })

        referer = request.META.get('HTTP_REFERER')
        return redirect(referer or 'inicio')

    return HttpResponseForbidden("Prioridade inválida")


@login_required
def calendario(request):
    hoje = timezone.localdate()
    ano = request.GET.get('ano')
    mes = request.GET.get('mes')

    try:
        ano = int(ano)
    except (TypeError, ValueError):
        ano = hoje.year

    try:
        mes = int(mes)
    except (TypeError, ValueError):
        mes = hoje.month

    if mes < 1:
        mes = 12
        ano -= 1
    elif mes > 12:
        mes = 1
        ano += 1

    context = gerar_calendario(request.user, ano=ano, mes=mes)

    tarefas = Tarefa.objects.filter(usuario=request.user).annotate(
        prioridade_order=Case(
            When(prioridade='alta', then=Value(1)),
            When(prioridade='media', then=Value(2)),
            When(prioridade='baixa', then=Value(3)),
            default=Value(4),
            output_field=IntegerField()
        )
    ).order_by('prioridade_order')

    context.update({
        'tarefas': tarefas,
        'ano': ano,
        'mes': mes
    })
    return render(request, "tarefas/calendario.html", context)

<<<<<<< HEAD

@csrf_exempt
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('file'):
        image = request.FILES['file']
        path = default_storage.save(f'tinymce_uploads/{image.name}', image)
        url = default_storage.url(path)
        return JsonResponse({'location': url})
    return JsonResponse({'error': 'Invalid request'}, status=400)
=======
def editar_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')  
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)

    return render(request, 'edit_profile.html', {'user_form': user_form, 'profile_form': profile_form})

def home(request):
    return HttpResponse("Bem-vindo à página inicial!")
>>>>>>> d48cc9c50b7152f44c66b1925064b48b2850d1a7
