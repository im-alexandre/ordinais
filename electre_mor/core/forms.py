from django import forms

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


class AvaliacaoCriteriosForm(forms.ModelForm):
    """description"""
    class Meta:
        model = AvaliacaoCriterios
        fields = ('projeto', 'decisor', 'criterioA', 'criterioB', 'nota')
        widgets = {
            'nota':
            forms.TextInput(attrs={
                'type': 'range',
                'min': -2,
                'max': 2,
                'step': 1
            })
        }


class AvaliacaoAlternativasForm(forms.ModelForm):
    class Meta:
        model = AvaliacaoAlternativas
        fields = ('projeto', 'decisor', 'criterio', 'alternativaA',
                  'alternativaB', 'nota')
        widgets = {
            'nota':
            forms.TextInput(attrs={
                'type': 'range',
                'min': -2,
                'max': 2,
                'step': 1
            })
        }


class CriterioParametroForm(forms.ModelForm):
    """description"""
    class Meta:
        model = CriterioParametro
        fields = 'projeto', 'criterio', 'p', 'q', 'v'
        widgets = {
            'projeto': forms.HiddenInput(),
            # 'decisor': forms.Select(attrs={'readonly': 'readonly'}),
            # 'criterio': forms.Select(attrs={'readonly': 'readonly'})
        }
