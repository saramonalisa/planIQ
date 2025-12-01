# app/forms.py
from django import forms
from django.forms.widgets import ClearableFileInput
from django.core.exceptions import ValidationError
from tinymce.widgets import TinyMCE
from .models import Tarefa, Periodo, Materia
from django.utils import timezone
from datetime import date

class TarefaForm(forms.ModelForm):
    
    class Meta:
        model = Tarefa
        fields = ['titulo', 'prazo', 'descricao', 'prioridade', 'notificacoes', 'periodo', 'materia']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Digite o título da tarefa'
            }),
            'prazo': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date',
                'min': timezone.now().date().isoformat()
            }),
            'descricao': TinyMCE(attrs={
                'cols': 80,
                'rows': 10,
                'placeholder': 'Descreva os detalhes da tarefa.',
                'class': 'tinymce-editor'
            }),
            'prioridade': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notificacoes': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'periodo': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Selecione o período'
            }),
            'materia': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Selecione a matéria'
            }),
        }
        help_texts = {
            'prazo': 'Selecione uma data futura.',
            'prioridade': 'Defina a importância desta tarefa.',
            'periodo': 'Opcional - para organizar por período acadêmico.',
            'materia': 'Opcional - para associar a uma matéria específica.',
        }

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        
        if usuario:
            self.fields['periodo'].queryset = Periodo.objects.filter(
                usuario=usuario
            ).order_by('-data_inicio')
            
            self.fields['materia'].queryset = Materia.objects.filter(
                usuario=usuario
            ).order_by('nome')
            
        if not self.fields['periodo'].queryset.exists():
            self.fields['periodo'].widget.attrs['disabled'] = 'disabled'
            self.fields['periodo'].help_text = '''
                <div class="alert alert-warning mt-2 p-2">
                    <i class="bi bi-exclamation-triangle"></i>
                    Você precisa criar um período primeiro. 
                    <a href="{% url 'app:novo_periodo' %}" class="alert-link">Criar período</a>
                </div>
            '''
            
        if not self.fields['materia'].queryset.exists():
            self.fields['materia'].widget.attrs['disabled'] = 'disabled'
            self.fields['materia'].help_text = '''
                <div class="alert alert-warning mt-2 p-2">
                    <i class="bi bi-exclamation-triangle"></i>
                    Você precisa criar uma matéria primeiro. 
                    <a href="{% url 'app:nova_materia' %}" class="alert-link">Criar matéria</a>
                </div>
            '''
        
        if self.instance and hasattr(self.instance, 'prazo') and self.instance.prazo:
            self.fields['prazo'].initial = self.instance.prazo 
        
    def clean(self):
        cleaned_data = super().clean()
        prazo = cleaned_data.get('prazo')
        periodo = cleaned_data.get('periodo')
        materia = cleaned_data.get('materia')
        
        if materia and periodo and materia.periodo != periodo:
            self.add_error('materia', 'Esta matéria não pertence ao período selecionado.')
            
        if prazo:
            hoje = timezone.now().date()
            if prazo < hoje:
                self.add_error('prazo', 'O prazo não pode ser uma data passada.')
                
        return cleaned_data

    def save(self, commit=True, usuario=None):
        tarefa = super().save(commit=False)
        
        if usuario:
            tarefa.usuario = usuario
            
        if not tarefa.status:
            tarefa.status = 'pendente'
        
        if commit:
            tarefa.save()
        return tarefa
    
class PeriodoForm(forms.ModelForm):
    class Meta:
        model = Periodo
        fields = ['nome', 'data_inicio', 'data_fim']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'data_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'data_fim': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
        }
        help_texts = {
            'nome': 'Um nome descritivo para identificar o período.',
            'data_inicio': 'Data de início do período acadêmico.',
            'data_fim': 'Data de término do período acadêmico.',
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if not self.instance.pk:
            hoje = timezone.now().date()
            seis_meses_depois = date(hoje.year + (hoje.month + 5) // 12, 
                                     (hoje.month + 5) % 12 + 1, 
                                     hoje.day)
            self.fields['data_inicio'].initial = hoje
            self.fields['data_fim'].initial = seis_meses_depois
        
    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        
        if data_inicio and data_fim:
            if data_inicio > data_fim:
                self.add_error('data_fim', 'A data de término deve ser posterior à data de início.')
                self.fields['data_fim'].widget.attrs['class'] = 'form-control is-invalid'
                self.fields['data_inicio'].widget.attrs['class'] = 'form-control is-invalid'
            else:
                self.fields['data_fim'].widget.attrs['class'] = 'form-control is-valid'
                self.fields['data_inicio'].widget.attrs['class'] = 'form-control is-valid'
            
            if (data_fim - data_inicio).days < 7:
                self.add_error('data_fim', 'O período deve ter no mínimo 1 semana de duração.')
            
            if (data_fim - data_inicio).days > 730:
                self.add_error('data_fim', 'O período não pode ter mais de 2 anos de duração.')
        
        if data_inicio and data_fim and hasattr(self, 'instance'):
            usuario = getattr(self.instance, 'usuario', None)
            if usuario:
                periodos_existentes = Periodo.objects.filter(
                    usuario=usuario
                ).exclude(pk=self.instance.pk if self.instance.pk else None)
                
                for periodo_existente in periodos_existentes:
                    if (data_inicio <= periodo_existente.data_fim and 
                        data_fim >= periodo_existente.data_inicio):
                        self.add_error('data_inicio', 
                            f'As datas sobrepõem com o período "{periodo_existente.nome}" '
                            f'({periodo_existente.data_inicio} a {periodo_existente.data_fim}).')
                        break
        
        return cleaned_data
    
    def save(self, commit=True, usuario=None):
        periodo = super().save(commit=False)
        
        if usuario:
            periodo.usuario = usuario
            
        if commit:
            periodo.save()
        return periodo


class MateriaForm(forms.ModelForm):
    class Meta:
        model = Materia
        fields = ['periodo', 'nome']
        widgets = {
            'periodo': forms.Select(attrs={
                'class': 'form-select',
                'id': 'periodo_select'
            }),
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
            }),
        }
        help_texts = {
            'periodo': 'Selecione o período acadêmico desta matéria.',
            'nome': 'Nome completo da matéria ou disciplina.',
        }
        
    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        
        if usuario:
            periodos_queryset = Periodo.objects.filter(
                usuario=usuario
            ).order_by('-data_inicio')
            
            self.fields['periodo'].queryset = periodos_queryset
            
            if not periodos_queryset.exists():
                self.fields['periodo'].widget.attrs['disabled'] = 'disabled'
                self.fields['periodo'].help_text = '''
                    <div class="alert alert-warning mt-2 p-2">
                        <i class="bi bi-exclamation-triangle"></i>
                        Você precisa criar um período antes de adicionar matérias.
                        <a href="{% url 'app:novo_periodo' %}" class="alert-link">Criar período</a>
                    </div>
                '''
        
        if self.instance and self.instance.pk and self.instance.periodo:
            self.fields['periodo'].initial = self.instance.periodo
    
    def clean(self):
        cleaned_data = super().clean()
        nome = cleaned_data.get('nome')
        periodo = cleaned_data.get('periodo')
        
        if periodo:
            existing_materia = Materia.objects.filter(
                nome__iexact=nome.strip() if nome else '',
                periodo=periodo,
                usuario=periodo.usuario
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing_materia.exists():
                self.add_error('nome', f'Já existe uma matéria com o nome "{nome}" no período "{periodo.nome}".')
                self.fields['nome'].widget.attrs['class'] = 'form-control is-invalid'
            elif nome:
                self.fields['nome'].widget.attrs['class'] = 'form-control is-valid'
        
        return cleaned_data
    
    def save(self, commit=True, usuario=None):
        materia = super().save(commit=False)
        
        if usuario:
            materia.usuario = usuario
        elif materia.periodo:
            materia.usuario = materia.periodo.usuario
            
        if commit:
            materia.save()
        return materia