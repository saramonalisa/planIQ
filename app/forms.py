from django import forms
from tinymce.widgets import TinyMCE
from .models import Tarefa

class TarefaForm(forms.ModelForm):
    
    class Meta:
        model = Tarefa
        fields = ['titulo', 'prazo', 'descricao', 'prioridade', 'notificacoes']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o título da tarefa'}),
            'prazo': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'descricao': TinyMCE(attrs={
                'cols': 80,
                'rows': 10,
                'placeholder': 'Descreva os detalhes da tarefa (opcional)'
            }),
            'prioridade': forms.Select(attrs={'class': 'form-control'}),
            'notificacoes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'prazo'):
            self.fields['prazo'].initial = self.instance.prazo 

    def save(self, commit=True):
        tarefa = super().save(commit=False)
        
        if not tarefa.status:
            tarefa.status = 'pendente'
        
        if commit:
            tarefa.save()
        return tarefa
    