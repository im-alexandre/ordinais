from django import forms
from django.utils.translation import ugettext_lazy as _

from core.models import (Alternativa, AlternativaCriterio,
                         AvaliacaoAlternativas, AvaliacaoCriterios, Criterio,
                         CriterioParametro, Decisor, Projeto)


class NomeProjetoForm(forms.ModelForm):
    class Meta:
        model = Projeto
        fields = (
            'nome',
            'descricao',
            'qtde_classes',
            'qtde_criterios',
            'qtde_decisores',
            'qtde_alternativas',
            'lamb',
        )
        labels = {
            'nome': _('Insira o nome do projeto'),
            'descricao': _('Insira a descrição do projeto'),
            'qtde_classes': _('Defina o número de classes'),
            'qtde_criterios': _('Defina o número de critérios'),
            'qtde_decisores': _('Defina o número de decisores'),
            'qtde_alternativas': _('Defina o número de alternativas'),
            'lamb': _('Defina o valor do nível de corte (λ)'),
        }
        widgets = {'descricao': forms.Textarea(attrs={'rows': 5, 'cols': 25})}

    def clean(self):
        cleaned_data = super().clean()
        classes = cleaned_data.get('qtde_classes')
        alternativas = cleaned_data.get('qtde_alternativas')
        if classes > alternativas:
            raise forms.ValidationError(
                'O número de classes deve ser inferior ao número de alternativas'
            )

        return cleaned_data


class DecisorForm(forms.ModelForm):
    class Meta:
        model = Decisor
        fields = ('nome', )


class AlternativaForm(forms.ModelForm):
    class Meta:
        model = Alternativa
        fields = ('nome', )


class CriterioForm(forms.ModelForm):
    class Meta:
        model = Criterio
        fields = ('nome', 'numerico', 'monotonico')


class AlternativaCriterioForm(forms.ModelForm):
    class Meta:
        model = AlternativaCriterio
        fields = ('projeto', 'alternativa', 'criterio', 'nota')
        widgets = {
            'projeto': forms.HiddenInput(),
            'decisor': forms.Select(attrs={'readonly': 'readonly'}),
            'criterio': forms.Select(attrs={'readonly': 'readonly'})
        }


class AvaliacaoCriteriosForm(forms.ModelForm):
    """description"""
    class Meta:
        model = AvaliacaoCriterios
        fields = ('projeto', 'decisor', 'criterioA', 'criterioB', 'nota')
        widgets = {
            'nota':
            forms.TextInput(
                attrs={
                    'type': 'range',
                    'min': -2,
                    'max': 2,
                    'step': 1,
                    'onchange': 'muda_valor(this)'
                }),
            'projeto':
            forms.HiddenInput(),
        }


class AvaliacaoAlternativasForm(forms.ModelForm):
    class Meta:
        model = AvaliacaoAlternativas
        fields = ('projeto', 'decisor', 'criterio', 'alternativaA',
                  'alternativaB', 'nota')
        widgets = {
            'nota':
            forms.TextInput(
                attrs={
                    'type': 'range',
                    'min': -2,
                    'max': 2,
                    'step': 1,
                    'onchange': 'muda_valor_alternativa(this)'
                }),
            'projeto':
            forms.HiddenInput(),
        }


class CriterioParametroForm(forms.ModelForm):
    """description"""
    class Meta:
        model = CriterioParametro
        fields = 'projeto', 'criterio', 'p', 'q', 'v'
        widgets = {
            'projeto': forms.HiddenInput(),
        }
