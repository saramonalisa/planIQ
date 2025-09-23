from django import forms
from .models import Tarefa

class TarefaForm(forms.ModelForm):
    class Meta:
        model = Tarefa
        fields = ['titulo', 'prazo', 'descricao', 'concluida']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o título da tarefa'
            }),
            'prazo': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'  # importante para exibir calendário no navegador
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descreva os detalhes da tarefa (opcional)'
            }),
            'concluida': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
