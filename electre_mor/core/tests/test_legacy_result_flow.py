from django.test import TestCase
from django.urls import reverse

from core.models import (Alternativa, AlternativaCriterio,
                         AvaliacaoCriterios, Criterio, CriterioParametro,
                         Decisor, Projeto)


class LegacyResultFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.projeto = Projeto.objects.create(
            id=1,
            nome="Resultado",
            descricao="Projeto com dados completos para resultado",
            qtde_classes=2,
            qtde_criterios=2,
            qtde_alternativas=2,
            qtde_decisores=1,
            lamb=0.5,
        )
        cls.decisor = Decisor.objects.create(
            id=1, projeto=cls.projeto, nome="Decisor 1")
        cls.criterio_1 = Criterio.objects.create(
            id=1,
            projeto=cls.projeto,
            nome="Criterio 1",
            numerico=True,
            monotonico=1,
        )
        cls.criterio_2 = Criterio.objects.create(
            id=2,
            projeto=cls.projeto,
            nome="Criterio 2",
            numerico=True,
            monotonico=1,
        )
        cls.alternativa_1 = Alternativa.objects.create(
            id=1,
            projeto=cls.projeto,
            nome="Alternativa 1",
        )
        cls.alternativa_2 = Alternativa.objects.create(
            id=2,
            projeto=cls.projeto,
            nome="Alternativa 2",
        )

        AvaliacaoCriterios.objects.create(
            projeto=cls.projeto,
            decisor=cls.decisor,
            criterioA=cls.criterio_1,
            criterioB=cls.criterio_2,
            nota=1,
        )
        AvaliacaoCriterios.objects.create(
            projeto=cls.projeto,
            decisor=cls.decisor,
            criterioA=cls.criterio_2,
            criterioB=cls.criterio_1,
            nota=-1,
        )
        AlternativaCriterio.objects.create(
            projeto=cls.projeto,
            criterio=cls.criterio_1,
            alternativa=cls.alternativa_1,
            nota=8,
        )
        AlternativaCriterio.objects.create(
            projeto=cls.projeto,
            criterio=cls.criterio_1,
            alternativa=cls.alternativa_2,
            nota=4,
        )
        AlternativaCriterio.objects.create(
            projeto=cls.projeto,
            criterio=cls.criterio_2,
            alternativa=cls.alternativa_1,
            nota=3,
        )
        AlternativaCriterio.objects.create(
            projeto=cls.projeto,
            criterio=cls.criterio_2,
            alternativa=cls.alternativa_2,
            nota=7,
        )
        CriterioParametro.objects.create(
            projeto=cls.projeto,
            criterio=cls.criterio_1,
            p=0.2,
            q=0.1,
            v=0.8,
        )
        CriterioParametro.objects.create(
            projeto=cls.projeto,
            criterio=cls.criterio_2,
            p=0.3,
            q=0.1,
            v=0.7,
        )

    def test_pagina_de_avaliacao_de_criterios_rende_com_dados_existentes(self):
        response = self.client.get(
            reverse("avaliarcriterios", args=[self.projeto.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pairwise comparison between criteria")

    def test_pagina_de_avaliacao_de_alternativas_rende_com_dados_existentes(self):
        response = self.client.get(
            reverse("avaliaralternativas", args=[self.projeto.id]),
            follow=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("resultadosapevo", args=[self.projeto.id]),
                      response["Location"])

    def test_resultado_exibe_classificacoes_e_tabela_de_pesos(self):
        response = self.client.get(reverse("resultado", args=[self.projeto.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Final result of Project")
        self.assertContains(response, "Weights of the criteria")
        self.assertContains(response, "Classification through bh procedure")

    def test_resultado_sapevo_exibe_tabelas_estruturais(self):
        response = self.client.get(
            reverse("resultadosapevo", args=[self.projeto.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Partial result of Project")
        self.assertContains(response, "Weights of the criteria")

    def test_alternativacriterio_preserva_notas_de_outro_decisor(self):
        decisor_2 = Decisor.objects.create(
            projeto=self.projeto,
            nome="Decisor 2",
        )
        AlternativaCriterio.objects.filter(projeto=self.projeto).delete()
        AlternativaCriterio.objects.create(
            projeto=self.projeto,
            decisor=self.decisor,
            criterio=self.criterio_1,
            alternativa=self.alternativa_1,
            nota=8,
        )
        AlternativaCriterio.objects.create(
            projeto=self.projeto,
            decisor=decisor_2,
            criterio=self.criterio_1,
            alternativa=self.alternativa_1,
            nota=4,
        )

        response = self.client.post(
            f"{reverse('alternativacriterio', args=[self.projeto.id])}?decisor_id={decisor_2.id}",
            {
                "form-TOTAL_FORMS": "2",
                "form-INITIAL_FORMS": "0",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
                "form-0-projeto": self.projeto.id,
                "form-0-criterio": self.criterio_1.id,
                "form-0-alternativa": self.alternativa_1.id,
                "form-0-nota": "9",
                "form-1-projeto": self.projeto.id,
                "form-1-criterio": self.criterio_1.id,
                "form-1-alternativa": self.alternativa_2.id,
                "form-1-nota": "7",
            },
            follow=False,
        )

        self.assertEqual(response.status_code, 302)
        notas = list(
            AlternativaCriterio.objects.filter(
                projeto=self.projeto,
                criterio=self.criterio_1,
                alternativa=self.alternativa_1,
            ).order_by("decisor__nome").values_list("decisor__nome", "nota"))
        self.assertEqual(notas, [("Decisor 1", 8.0), ("Decisor 2", 9.0)])
