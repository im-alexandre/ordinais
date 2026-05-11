from django.test import TestCase
from django.urls import reverse

from core.models import Alternativa, Criterio, Decisor, Projeto


class LegacyProjectFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.projeto = Projeto.objects.create(
            id=1,
            nome="Baseline",
            descricao="Projeto de baseline para testes legados",
            qtde_classes=2,
            qtde_criterios=2,
            qtde_alternativas=2,
            qtde_decisores=1,
            lamb=0.5,
        )
        Decisor.objects.create(id=1, projeto=cls.projeto, nome="Decisor 1")
        Criterio.objects.create(
            id=1,
            projeto=cls.projeto,
            nome="Criterio 1",
            numerico=True,
            monotonico=1,
        )
        Criterio.objects.create(
            id=2,
            projeto=cls.projeto,
            nome="Criterio 2",
            numerico=False,
            monotonico=1,
        )
        Alternativa.objects.create(
            id=1,
            projeto=cls.projeto,
            nome="Alternativa 1",
        )
        Alternativa.objects.create(
            id=2,
            projeto=cls.projeto,
            nome="Alternativa 2",
        )

    def test_criacao_de_projeto_redireciona_para_cadastro_de_participantes(self):
        response = self.client.post(
            reverse("projeto_form"),
            {
                "nome": "Novo projeto",
                "descricao": "Descricao do projeto",
                "qtde_classes": 2,
                "qtde_criterios": 2,
                "qtde_decisores": 1,
                "qtde_alternativas": 2,
                "lamb": 0.5,
            },
            follow=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/dm_criteria_alt/", response["Location"])

    def test_pagina_de_projeto_lista_dados_cadastrados(self):
        response = self.client.get(reverse("projeto", args=[self.projeto.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Baseline")
        self.assertContains(response, "Decisor 1")
        self.assertContains(response, "Alternativa 1")
        self.assertContains(response, "Criterio 1")

    def test_pagina_de_cadastro_mostra_formularios_do_projeto(self):
        response = self.client.get(reverse("cadastradecisores", args=[self.projeto.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Name")
        self.assertContains(response, "Monotonicity")
