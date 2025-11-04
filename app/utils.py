from collections import defaultdict 
from django.utils import timezone
from django.db.models import Case, When, Value, IntegerField
from accounts.models import Usuario
from app.models import Tarefa
import calendar

def gerar_calendario(usuario, ano=None, mes=None):
    hoje = timezone.localdate()
    
    ano = int(ano) if ano else hoje.year
    mes = int(mes) if mes else hoje.month
    
    if mes < 1 or mes > 12:
        mes = hoje.month

    meses_pt = [
        '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    mes_nome = meses_pt[mes]

    ano_ant, mes_ant = (ano - 1, 12) if mes == 1 else (ano, mes - 1)
    ano_prox, mes_prox = (ano + 1, 1) if mes == 12 else (ano, mes + 1)

    tarefas_por_dia = defaultdict(list)

    if getattr(usuario, "is_authenticated", False):
        tarefas = Tarefa.objects.filter(
            usuario=usuario,
            prazo__year__in=[ano_ant, ano, ano_prox],
            prazo__month__in=[mes_ant, mes, mes_prox]
        ).order_by('prazo')

        for t in tarefas:
            chave = f"{t.prazo.year}-{t.prazo.month}-{t.prazo.day}"
            tarefas_por_dia[chave].append(t)

    cal = calendar.Calendar(firstweekday=6)
    semanas_brutas = list(cal.monthdayscalendar(ano, mes))
    _, dias_mes_ant = calendar.monthrange(ano_ant, mes_ant)

    semanas = []
    for idx_semana, semana in enumerate(semanas_brutas):
        semana_formatada = []
        for idx_dia, dia in enumerate(semana):
            if dia == 0:
                if idx_semana == 0:
                    dia_real = dias_mes_ant - semana.count(0) + idx_dia + 1
                    semana_formatada.append({
                        "numero": dia_real,
                        "mes": "anterior",
                        "ano_link": ano_ant,
                        "mes_link": mes_ant,
                        "chave": f"{ano_ant}-{mes_ant}-{dia_real}"
                    })
                else:
                    primeiro_zero = semana.index(0)
                    dia_real = idx_dia - primeiro_zero + 1
                    semana_formatada.append({
                        "numero": dia_real,
                        "mes": "proximo",
                        "ano_link": ano_prox,
                        "mes_link": mes_prox,
                        "chave": f"{ano_prox}-{mes_prox}-{dia_real}"
                    })
            else:
                semana_formatada.append({
                    "numero": dia,
                    "mes": "atual",
                    "ano_link": ano,
                    "mes_link": mes,
                    "chave": f"{ano}-{mes}-{dia}"
                })
        semanas.append(semana_formatada)

    return {
        "ano": ano,
        "mes": mes,
        "mes_nome": mes_nome,
        "semanas": semanas,
        "tarefas_por_dia": tarefas_por_dia,
        "ano_ant": ano_ant,
        "mes_ant": mes_ant,
        "ano_prox": ano_prox,
        "mes_prox": mes_prox
    }


def lista_por_status(usuario):
    prioridade_order = Case(
        When(prioridade='alta', then=Value(1)),
        When(prioridade='media', then=Value(2)),
        When(prioridade='baixa', then=Value(3)),
        default=Value(4),
        output_field=IntegerField()
    )

    tarefas_pendentes = Tarefa.objects.filter(usuario=usuario, status='pendente')
    tarefas_pendentes = tarefas_pendentes.annotate(prioridade_order=prioridade_order).order_by('prioridade_order')

    tarefas_andamento = Tarefa.objects.filter(usuario=usuario, status='em_progresso')
    tarefas_andamento = tarefas_andamento.annotate(prioridade_order=prioridade_order).order_by('prioridade_order')

    tarefas_concluidas = Tarefa.objects.filter(usuario=usuario, status='concluida')
    tarefas_concluidas = tarefas_concluidas.annotate(prioridade_order=prioridade_order).order_by('prioridade_order')

    return {
        'tarefas_pendentes': tarefas_pendentes,
        'tarefas_andamento': tarefas_andamento,
        'tarefas_concluidas': tarefas_concluidas,
    }