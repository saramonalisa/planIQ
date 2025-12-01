from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.contrib import messages
from django.utils import timezone
from django.db.models import Case, When, Value, IntegerField, Q
from collections import defaultdict
from .models import Tarefa, Periodo, Materia
from .forms import TarefaForm, PeriodoForm, MateriaForm
from .utils import gerar_calendario, lista_por_status
from datetime import datetime, date
import calendar

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

    # Validar status
    if novo_status not in ['pendente', 'em_progresso', 'concluida']:
        return HttpResponseForbidden("Status inválido")

    tarefa.status = novo_status
    tarefa.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'id': tarefa.id,
            'status': tarefa.status
        })

    referer = request.META.get('HTTP_REFERER')
    return redirect(referer or 'home')


@login_required
@require_POST
def alterar_prioridade_tarefa(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, id=tarefa_id, usuario=request.user)
    nova_prioridade = request.POST.get('prioridade')

    if nova_prioridade not in ['alta', 'media', 'baixa', 'sem_prioridade']:
        return HttpResponseForbidden("Prioridade inválida")

    tarefa.prioridade = nova_prioridade
    tarefa.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'id': tarefa.id,
            'prioridade': tarefa.prioridade
        })  


@login_required
def meus_periodos(request):
    periodos = Periodo.objects.filter(usuario=request.user).order_by('-data_inicio')
    
    for periodo in periodos:
        periodo.num_materias = Materia.objects.filter(periodo=periodo, usuario=request.user).count()
        periodo.num_tarefas = Tarefa.objects.filter(
            usuario=request.user,
            periodo=periodo
        ).count()
    
    return render(request, 'academico/periodos/meus_periodos.html', {
        'periodos': periodos
    })


@login_required
def novo_periodo(request):
    if request.method == 'POST':
        form = PeriodoForm(request.POST)
        if form.is_valid():
            periodo = form.save(commit=False, usuario=request.user)
            periodo.save()
            messages.success(request, "Período criado com sucesso!")
            return redirect('app:meus_periodos')
    else:
        form = PeriodoForm()
    
    return render(request, 'academico/periodos/novo_periodo.html', {
        'form': form,
        'titulo': 'Novo Período'
    })


@login_required
def editar_periodo(request, periodo_id):
    periodo = get_object_or_404(Periodo, id=periodo_id, usuario=request.user)
    
    if request.method == 'POST':
        form = PeriodoForm(request.POST, instance=periodo)
        if form.is_valid():
            form.save()
            messages.success(request, "Período atualizado com sucesso!")
            return redirect('app:meus_periodos')
    else:
        form = PeriodoForm(instance=periodo)
    
    return render(request, 'academico/periodos/novo_periodo.html', {
        'form': form,
        'titulo': 'Editar Período',
        'periodo': periodo
    })


@login_required
@require_POST
def excluir_periodo(request, periodo_id):
    periodo = get_object_or_404(Periodo, id=periodo_id, usuario=request.user)
    
    materias_count = Materia.objects.filter(periodo=periodo, usuario=request.user).count()
    tarefas_count = Tarefa.objects.filter(periodo=periodo, usuario=request.user).count()
    
    if materias_count > 0 or tarefas_count > 0:
        messages.error(request, 
            f"Não é possível excluir este período. "
            f"Ele possui {materias_count} matéria(s) e {tarefas_count} tarefa(s) associadas.")
        return redirect('app:meus_periodos')
    
    periodo.delete()
    messages.success(request, "Período excluído com sucesso!")
    return redirect('app:meus_periodos')


@login_required
def minhas_materias(request):
    periodos = Periodo.objects.filter(usuario=request.user).order_by('-data_inicio')
    
    for periodo in periodos:
        periodo.materias_list = Materia.objects.filter(
            periodo=periodo, 
            usuario=request.user
        ).order_by('nome')
        
        for materia in periodo.materias_list:
            materia.num_tarefas = Tarefa.objects.filter(
                usuario=request.user,
                materia=materia
            ).count()
    
    return render(request, 'academico/materias/minhas_materias.html', {
        'periodos': periodos,
        'total_materias': Materia.objects.filter(usuario=request.user).count()
    })


@login_required
def nova_materia(request):
    if request.method == 'POST':
        form = MateriaForm(request.POST, usuario=request.user)
        if form.is_valid():
            materia = form.save(commit=False, usuario=request.user)
            materia.save()
            messages.success(request, "Matéria criada com sucesso!")
            return redirect('app:minhas_materias')
    else:
        form = MateriaForm(usuario=request.user)
    
    return render(request, 'academico/materias/nova_materia.html', {
        'form': form,
        'titulo': 'Nova Matéria'
    })


@login_required
def editar_materia(request, materia_id):
    materia = get_object_or_404(Materia, id=materia_id, usuario=request.user)
    
    if request.method == 'POST':
        form = MateriaForm(request.POST, instance=materia, usuario=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Matéria atualizada com sucesso!")
            return redirect('app:minhas_materias')
    else:
        form = MateriaForm(instance=materia, usuario=request.user)
    
    return render(request, 'academico/materias/nova_materia.html', {
        'form': form,
        'titulo': 'Editar Matéria',
        'materia': materia
    })


@login_required
@require_POST
def excluir_materia(request, materia_id):
    materia = get_object_or_404(Materia, id=materia_id, usuario=request.user)
    
    tarefas_count = Tarefa.objects.filter(materia=materia, usuario=request.user).count()
    
    if tarefas_count > 0:
        messages.error(request, 
            f"Não é possível excluir esta matéria. "
            f"Ela possui {tarefas_count} tarefa(s) associadas.")
        return redirect('app:minhas_materias')
    
    materia.delete()
    messages.success(request, "Matéria excluída com sucesso!")
    return redirect('app:minhas_materias')


@login_required
def detalhar_materia(request, materia_id):
    materia = get_object_or_404(Materia, id=materia_id, usuario=request.user)
    
    tarefas = Tarefa.objects.filter(
        usuario=request.user,
        materia=materia
    ).order_by('prazo', 'prioridade')
    
    tarefas_pendentes = tarefas.filter(status='pendente').count()
    tarefas_em_progresso = tarefas.filter(status='em_progresso').count()
    tarefas_concluidas = tarefas.filter(status='concluida').count()
    
    return render(request, 'academico/materias/detalhar_materia.html', {
        'materia': materia,
        'tarefas': tarefas,
        'tarefas_pendentes': tarefas_pendentes,
        'tarefas_em_progresso': tarefas_em_progresso,
        'tarefas_concluidas': tarefas_concluidas,
        'total_tarefas': tarefas.count()
    })


@login_required
def detalhar_periodo(request, periodo_id):
    periodo = get_object_or_404(Periodo, id=periodo_id, usuario=request.user)
    
    materias = Materia.objects.filter(
        periodo=periodo,
        usuario=request.user
    ).order_by('nome')
    
    tarefas = Tarefa.objects.filter(
        usuario=request.user,
        periodo=periodo
    ).order_by('prazo', 'prioridade')
    
    total_materias = materias.count()
    total_tarefas = tarefas.count()
    
    tarefas_pendentes = tarefas.filter(status='pendente').count()
    tarefas_em_progresso = tarefas.filter(status='em_progresso').count()
    tarefas_concluidas = tarefas.filter(status='concluida').count()
    
    return render(request, 'academico/periodos/detalhar_periodo.html', {
        'periodo': periodo,
        'materias': materias,
        'tarefas': tarefas,
        'total_materias': total_materias,
        'total_tarefas': total_tarefas,
        'tarefas_pendentes': tarefas_pendentes,
        'tarefas_em_progresso': tarefas_em_progresso,
        'tarefas_concluidas': tarefas_concluidas
    })


@login_required
def lista_tarefas(request):
    materia_id = request.GET.get('materia')
    periodo_id = request.GET.get('periodo')
    status = request.GET.get('status')
    prioridade = request.GET.get('prioridade')
    
    tarefas = Tarefa.objects.filter(usuario=request.user)
    
    if materia_id and materia_id != 'todas':
        tarefas = tarefas.filter(materia_id=materia_id)
    
    if periodo_id and periodo_id != 'todos':
        tarefas = tarefas.filter(periodo_id=periodo_id)
    
    if status and status != 'todos':
        tarefas = tarefas.filter(status=status)
    
    if prioridade and prioridade != 'todas':
        tarefas = tarefas.filter(prioridade=prioridade)
    
    ordenacao = request.GET.get('ordenacao', 'prazo')
    if ordenacao == 'prioridade':
        tarefas = tarefas.annotate(
            prioridade_order=Case(
                When(prioridade='alta', then=Value(1)),
                When(prioridade='media', then=Value(2)),
                When(prioridade='baixa', then=Value(3)),
                default=Value(4),
                output_field=IntegerField()
            )
        ).order_by('prioridade_order', 'prazo')
    else:
        tarefas = tarefas.order_by('prazo', 'prioridade')
    
    periodos = Periodo.objects.filter(usuario=request.user)
    materias = Materia.objects.filter(usuario=request.user)
    
    context = {
        'tarefas': tarefas,
        'periodos': periodos,
        'materias': materias,
        'status_choices': Tarefa.STATUS_CHOICES,
        'prioridade_choices': Tarefa.PRIORITY_CHOICES,
        'filtro_materia': materia_id,
        'filtro_periodo': periodo_id,
        'filtro_status': status,
        'filtro_prioridade': prioridade,
        'ordenacao': ordenacao
    }
    
    return render(request, 'academico/lista_tarefas.html', context)


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
