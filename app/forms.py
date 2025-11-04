from django import forms
from django.forms.widgets import ClearableFileInput
from django.core.exceptions import ValidationError
from tinymce.widgets import TinyMCE
from .models import Tarefa
from .models import Periodo, Materia, Tarefa

class TarefaForm(forms.ModelForm):
        class Meta:
            model = Tarefa
            fields = ['materia', 'titulo', 'descricao', 'data_entrega', 'concluida']
            widgets = {
                'materia': forms.Select(attrs={'class': 'form-control'}),
                'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título da tarefa'}),
                'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descrição'}),
                'data_entrega': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                'concluida': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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

    