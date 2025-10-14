from collections import defaultdict
from django.utils import timezone
import calendar
from .models import Tarefa

def gerar_calendario(usuario, ano=None, mes=None):
    hoje = timezone.localdate()
    ano = ano or hoje.year
    mes = mes or hoje.month

    meses_pt = [
        '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    mes_nome = meses_pt[mes]

    tarefas = Tarefa.objects.filter(
        usuario=usuario,
        prazo__year=ano,
        prazo__month=mes
    ).order_by('prazo')

    tarefas_por_dia = defaultdict(list)
    for tarefa in tarefas:
        tarefas_por_dia[tarefa.prazo.day].append(tarefa)

    cal = calendar.Calendar(firstweekday=6)
    semanas = list(cal.monthdayscalendar(ano, mes))

    return {
        "ano": ano,
        "mes_nome": mes_nome,
        "semanas": semanas,
        "tarefas_por_dia": tarefas_por_dia,
        "tarefas": tarefas
    }
