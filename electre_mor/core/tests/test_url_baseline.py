from django.test import TestCase
from django.urls import reverse

from core.models import Alternativa, Criterio, Decisor, Projeto


class UrlBaselineGetTests(TestCase):
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

    def assert_get(self, path, expected_status=200, markers=()):
        response = self.client.get(path, follow=False)
        self.assertEqual(response.status_code, expected_status, path)
        content = response.content.decode("utf-8", errors="ignore")
        for marker in markers:
            self.assertIn(marker, content)
        return response

    def test_public_pages_baseline(self):
        self.assert_get(reverse("index"), markers=("ELECTRE",))
        self.assert_get(reverse("projeto_form"), markers=("project"))
        self.assert_get(reverse("metodo"))

    def test_project_pages_baseline(self):
        project_id = 1
        self.assert_get(reverse("projeto", args=[project_id]), markers=("Baseline",))
        self.assert_get(reverse("cadastradecisores", args=[project_id]))
        self.assert_get(reverse("alternativacriterio", args=[project_id]))
        self.assert_get(reverse("avaliarcriterios", args=[project_id]))
        self.assert_get(reverse("avaliaralternativas", args=[project_id]))

    def test_result_pages_baseline_are_observable(self):
        project_id = 1
        self.client.raise_request_exception = False
        for name in ("resultadosapevo", "resultado"):
            response = self.client.get(reverse(name, args=[project_id]), follow=False)
            self.assertIn(response.status_code, (200, 302, 500), name)
