from django import forms

from app.models import Alternativa, AlternativaCriterio, Criterio, Projeto


class ProjetoForm(forms.ModelForm):
    """formulário para definir a quantidade de critérios e alternativas do projeto"""
    class Meta:
        model = Projeto
        fields = '__all__'


class AlternativaForm(forms.ModelForm):
    class Meta:
        model = Alternativa
        fields = ('nome', )


class CriterioForm(forms.ModelForm):
    class Meta:
        model = Criterio
        fields = ('nome', 'monotonico')


class AlternativaCriterioForm(forms.ModelForm):
    class Meta:
        model = AlternativaCriterio
        fields = ('alternativa', 'criterio', 'nota')
