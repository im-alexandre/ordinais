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
