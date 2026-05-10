from django.test import TestCase
from django.urls import reverse

from core.models import Alternativa, Criterio, Decisor, Projeto


class UrlFlowBaselineTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.projeto = Projeto.objects.create(
            id=1,
            nome="Baseline",
            descricao="Projeto de baseline para testes exploratorios",
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
        Alternativa.objects.create(id=1, projeto=cls.projeto, nome="Alternativa 1")
        Alternativa.objects.create(id=2, projeto=cls.projeto, nome="Alternativa 2")

    def test_project_creation_redirects_to_decision_makers_step(self):
        response = self.client.post(
            reverse("projeto_form"),
            {
                "nome": "Novo",
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

    def test_invalid_project_creation_renders_form_with_error(self):
        response = self.client.post(
            reverse("projeto_form"),
            {
                "nome": "Invalido",
                "descricao": "Descricao do projeto",
                "qtde_classes": 3,
                "qtde_criterios": 2,
                "qtde_decisores": 1,
                "qtde_alternativas": 2,
                "lamb": 0.5,
            },
            follow=False,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "O número de classes deve ser inferior")

    def test_delete_project_redirects_to_home(self):
        response = self.client.get(reverse("deletarprojeto", args=[1]), follow=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/")
