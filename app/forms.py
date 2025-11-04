from django import forms
from django.forms.widgets import ClearableFileInput
from django.core.exceptions import ValidationError
from tinymce.widgets import TinyMCE
from .models import Tarefa
from .models import Periodo, Materia, Tarefa

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
                'placeholder': 'Descreva os detalhes da tarefa.',
            }),
            'prioridade': forms.Select(attrs={'class': 'form-control'}),
            'notificacoes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'prazo'):
            self.fields['prazo'].initial = self.instance.prazo 
        
    def clean(self):
        cleaned_data = super().clean()
        current_prazo = cleaned_data.get('current_prazo')
        new_prazo = cleaned_data.get('new_prazo')
        confirm_new_prazo = cleaned_data.get('confirm_new_prazo')

        if new_prazo and current_prazo:
            if not self.instance.check_prazo(current_prazo):
                raise ValidationError("A senha atual está incorreta.")
            if new_prazo != confirm_new_prazo:
                raise ValidationError("As novas senhas não coincidem.")

        return cleaned_data

    def save(self, commit=True):
        tarefa = super().save(commit=False)
        
        if not tarefa.status:
            tarefa.status = 'pendente'
        
        if commit:
            tarefa.save()
        return tarefa
    
class PeriodoForm(forms.ModelForm):
    class Meta:
        model = Periodo
        fields = ['nome', 'data_inicio', 'data_fim']


class MateriaForm(forms.ModelForm):
    class Meta:
        model = Materia
        fields = ['periodo', 'nome']


class TarefaForm(forms.ModelForm):
    class Meta:
        model = Tarefa
        fields = ['materia', 'titulo', 'descricao', 'data_entrega', 'concluida']

    