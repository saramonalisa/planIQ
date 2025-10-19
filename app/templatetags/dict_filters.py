from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    return d.get(key)

@register.filter
def tarefas_pendentes(tarefas):
    """
    Retorna a quantidade de tarefas pendentes (não concluídas)
    """
    if not tarefas:
        return 0
    return sum(1 for t in tarefas if not getattr(t, "concluida", False))
