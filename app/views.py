from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.contrib import messages
from django.utils import timezone
from django.db.models import Case, When, Value, IntegerField
from collections import defaultdict
from .models import Tarefa
from .forms import TarefaForm
from .utils import gerar_calendario, lista_por_status
from datetime import datetime, date
import calendar
from django.http import HttpResponse
from .models import Periodo, Materia, Tarefa
from .forms import PeriodoForm, MateriaForm, TarefaForm



def index(request):
    if request.user.is_authenticated:
        return redirect('app:home')
    return render(request, "index.html")


meses_nome_ptbr = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

@login_required
def home(request):
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

    meses_nome = [(i, meses_nome_ptbr[i-1]) for i in range(1, 13)]

    context = gerar_calendario(request.user, ano=ano, mes=mes)

    anos_disponiveis = range(hoje.year - 5, hoje.year + 5)

    context['meses_nome'] = meses_nome 
    context['meses'] = range(1, 13)
    context['anos_disponiveis'] = anos_disponiveis

    tarefas = lista_por_status(request.user)
    context.update(tarefas)

    return render(request, "home.html", context)


@login_required
def detalhar_tarefa(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, id=tarefa_id, usuario=request.user)
    return render(request, "tarefas/detalhar_tarefa.html", {"tarefa": tarefa})


@login_required
def minhas_tarefas(request):
    context = lista_por_status(usuario=request.user)
    return render(request, "tarefas/minhas_tarefas.html", context)


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
            return redirect('app:home')
        else:
            for field in form:
                for error in field.errors:
                    messages.error(request, f"{field.label}: {error}")
    else:
        form = TarefaForm()

    return render(request, 'tarefas/nova_tarefa.html', {'form': form})



@login_required
@csrf_exempt
def editar_tarefa(request, tarefa_id):
    if request.method == 'POST':
        tarefa = get_object_or_404(Tarefa, id=tarefa_id)

        novo_titulo = request.POST.get('titulo')
        novo_prazo = request.POST.get('prazo')
        nova_descricao = request.POST.get('descricao')

        if novo_titulo:
            tarefa.titulo = novo_titulo

        if novo_prazo:
            try:
                novo_prazo = datetime.strptime(novo_prazo, "%Y-%m-%d").date()
                tarefa.prazo = novo_prazo
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Data do prazo inválida'}, status=400)

        tarefa.save()

        if nova_descricao is not None:
            tarefa.descricao = nova_descricao

        tarefa.save()

        return JsonResponse({
            'success': True,
            'titulo': tarefa.titulo,
            'prazo': tarefa.prazo.strftime("%d/%m/%Y") if tarefa.prazo else 'Não definido',
            'descricao': tarefa.descricao or 'Sem descrição',
        })

    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)


@login_required
@require_POST
def excluir_tarefa(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, pk=tarefa_id, usuario=request.user)
    tarefa.delete()
    messages.success(request, "Tarefa excluída com sucesso!")
    return redirect('app:home')


@login_required
@require_POST
def marcar_concluida(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, pk=tarefa_id, usuario=request.user)
    tarefa.concluida = True
    tarefa.save()
    messages.success(request, "Tarefa marcada como concluída!")
    return redirect('app:detalhar_tarefa', tarefa_id=tarefa.id)


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
        return redirect(referer or 'home')

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
        return redirect(referer or 'app:home')

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


@csrf_exempt
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('file'):
        image = request.FILES['file']
        path = default_storage.save(f'tinymce_uploads/{image.name}', image)
        url = default_storage.url(path)
        return JsonResponse({'location': url})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def lista_periodos(request):
    periodos = Periodo.objects.filter(user=request.user)
    return render(request, 'academico/lista_periodos.html', {'periodos': periodos})


@login_required
def novo_periodo(request):
    if request.method == 'POST':
        form = PeriodoForm(request.POST)
        if form.is_valid():
            periodo = form.save(commit=False)
            periodo.user = request.user
            periodo.save()
            return redirect('lista_periodos')
    else:
        form = PeriodoForm()
    return render(request, 'academico/form_periodo.html', {'form': form})


@login_required
def nova_materia(request):
    if request.method == 'POST':
        form = MateriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_periodos')
    else:
        form = MateriaForm()
    return render(request, 'academico/form_materia.html', {'form': form})


@login_required
def nova_tarefa(request):
    if request.method == 'POST':
        form = TarefaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_tarefas')
    else:
        form = TarefaForm()
    return render(request, 'academico/form_tarefa.html', {'form': form})


@login_required
def lista_tarefas(request):
    materia_id = request.GET.get('materia')
    periodo_id = request.GET.get('periodo')

    tarefas = Tarefa.objects.all()
    if materia_id:
        tarefas = tarefas.filter(materia_id=materia_id)
    if periodo_id:
        tarefas = tarefas.filter(materia__periodo_id=periodo_id)

    periodos = Periodo.objects.filter(user=request.user)
    materias = Materia.objects.filter(periodo__in=periodos)

    context = {
        'tarefas': tarefas,
        'periodos': periodos,
        'materias': materias
    }
    return render(request, 'academico/lista_tarefas.html', context)