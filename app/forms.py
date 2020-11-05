from django import forms

from app.models import Alternativa, AlternativaCriterio, Criterio

class ProjetoForm(forms.Form):
    """formulário para definir a quantidade de critérios e alternativas do projeto"""
    nome_projeto = forms.CharField(max_length=20, required=True)
    num_alternativas = forms.IntegerField(min_value=2, required=True)
    num_criterios = forms.IntegerField(min_value=2, required=True)

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

