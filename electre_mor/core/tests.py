from django.test import TestCase
from django.urls import reverse

from core.models import Alternativa, Criterio, Decisor, Projeto


class AvaliacoesFormFilteringTests(TestCase):

    def setUp(self):
        self.projeto = Projeto.objects.create(
            nome='Projeto 1',
            descricao='x',
            qtde_classes=2,
            qtde_criterios=2,
            qtde_decisores=1,
            qtde_alternativas=2,
            lamb=0.7,
        )
        self.decisor = Decisor.objects.create(nome='D1', projeto=self.projeto)
        self.criterio_a = Criterio.objects.create(
            nome='C1', numerico=False, monotonico=1, projeto=self.projeto)
        self.criterio_b = Criterio.objects.create(
            nome='C2', numerico=False, monotonico=1, projeto=self.projeto)
        self.alternativa_a = Alternativa.objects.create(
            nome='A1', projeto=self.projeto)
        self.alternativa_b = Alternativa.objects.create(
            nome='A2', projeto=self.projeto)

        self.outro_projeto = Projeto.objects.create(
            nome='Projeto 2',
            descricao='x',
            qtde_classes=2,
            qtde_criterios=2,
            qtde_decisores=1,
            qtde_alternativas=2,
            lamb=0.7,
        )
        self.outro_decisor = Decisor.objects.create(
            nome='D2', projeto=self.outro_projeto)
        self.outro_criterio = Criterio.objects.create(
            nome='OC', numerico=False, monotonico=1, projeto=self.outro_projeto)
        self.outro_alt = Alternativa.objects.create(
            nome='OA', projeto=self.outro_projeto)

    def test_avaliar_criterios_filtra_campos_por_projeto(self):
        response = self.client.get(
            reverse('avaliarcriterios', args=[self.projeto.id]))
        form = response.context['forms'].forms[0]
        self.assertIn(self.decisor, form.fields['decisor'].queryset)
        self.assertNotIn(self.outro_decisor, form.fields['decisor'].queryset)
        self.assertIn(self.criterio_a, form.fields['criterioA'].queryset)
        self.assertNotIn(self.outro_criterio, form.fields['criterioA'].queryset)
        self.assertTrue(form.fields['decisor'].disabled)
        self.assertTrue(form.fields['criterioA'].disabled)
        self.assertTrue(form.fields['criterioB'].disabled)

    def test_avaliar_alternativas_filtra_campos_por_projeto(self):
        response = self.client.get(
            reverse('avaliaralternativas', args=[self.projeto.id]))
        form = response.context['forms'].forms[0]
        self.assertIn(self.decisor, form.fields['decisor'].queryset)
        self.assertNotIn(self.outro_decisor, form.fields['decisor'].queryset)
        self.assertIn(self.criterio_a, form.fields['criterio'].queryset)
        self.assertNotIn(self.outro_criterio, form.fields['criterio'].queryset)
        self.assertIn(self.alternativa_a, form.fields['alternativaA'].queryset)
        self.assertNotIn(self.outro_alt, form.fields['alternativaA'].queryset)
        self.assertTrue(form.fields['alternativaA'].disabled)
        self.assertTrue(form.fields['alternativaB'].disabled)
