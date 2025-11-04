from django.db import models
from django.utils import timezone
from accounts.models import Usuario
from django.conf import settings
from tkinter import CASCADE

class Tarefa(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_progresso', 'Em Progresso'),
        ('concluida', 'Concluída'),
    ]

    PRIORITY_CHOICES = [
        ('alta', 'Alta'),
        ('media', 'Média'),
        ('baixa', 'Baixa'),
        ('sem_prioridade', 'Sem Prioridade'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='tarefas')
    titulo = models.CharField(max_length=200) 
    descricao = models.TextField(blank=True, null=True) 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    data_criacao = models.DateTimeField(auto_now_add=True) 
    prazo = models.DateField(blank=True, null=True) 
    prioridade = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='sem_prioridade')
    notificacoes = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo

    @property
    def atrasada(self):
        if self.prazo and self.status != 'concluida':
            return timezone.now().date() > self.prazo
        return False
    
class Periodo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='periodos')
    nome = models.CharField(max_length=100)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    
    def __str__(self):
        return self.nome

class Materia(models.Model):
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, related_name='materias')
    nome = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nome} ({self.periodo.nome})"
