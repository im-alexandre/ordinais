from rest_framework.test import APITestCase

from core.models import (Alternativa, AlternativaCriterio,
                         AvaliacaoAlternativas, AvaliacaoCriterios, Criterio,
                         CriterioParametro, Decisor, Projeto)


class ApiEvaluationsTests(APITestCase):
    def setUp(self):
        self.projeto = Projeto.objects.create(
            nome="Projeto avaliacoes",
            descricao="Descricao",
            qtde_classes=2,
            qtde_criterios=2,
            qtde_alternativas=2,
            qtde_decisores=1,
            lamb=0.7,
        )
        self.decisor = Decisor.objects.create(projeto=self.projeto,
                                               nome="Decisor 1")
        self.criterio_1 = Criterio.objects.create(
            projeto=self.projeto,
            nome="Criterio 1",
            numerico=True,
            monotonico=1,
        )
        self.criterio_2 = Criterio.objects.create(
            projeto=self.projeto,
            nome="Criterio 2",
            numerico=False,
            monotonico=2,
        )
        self.alternativa_1 = Alternativa.objects.create(
            projeto=self.projeto,
            nome="Alternativa 1",
        )
        self.alternativa_2 = Alternativa.objects.create(
            projeto=self.projeto,
            nome="Alternativa 2",
        )

    def test_substituir_notas_numericas(self):
        payload = {
            "scores": [{
                "criterio_id": self.criterio_1.id,
                "alternativa_id": self.alternativa_1.id,
                "nota": 8.5,
            }, {
                "criterio_id": self.criterio_1.id,
                "alternativa_id": self.alternativa_2.id,
                "nota": 4.0,
            }],
        }

        response = self.client.put(
            f"/api/v1/projects/{self.projeto.id}/numeric-scores/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(AlternativaCriterio.objects.count(), 2)

    def test_substituir_comparacoes_de_criterios(self):
        payload = {
            "comparisons": [{
                "decisor_id": self.decisor.id,
                "criterio_a_id": self.criterio_1.id,
                "criterio_b_id": self.criterio_2.id,
                "nota": 1,
            }],
        }

        response = self.client.put(
            f"/api/v1/projects/{self.projeto.id}/criteria-comparisons/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(AvaliacaoCriterios.objects.count(), 2)
        notas = sorted(AvaliacaoCriterios.objects.values_list("nota",
                                                              flat=True))
        self.assertEqual(notas, [-1, 1])

    def test_substituir_comparacoes_de_alternativas(self):
        payload = {
            "comparisons": [{
                "decisor_id": self.decisor.id,
                "criterio_id": self.criterio_2.id,
                "alternativa_a_id": self.alternativa_1.id,
                "alternativa_b_id": self.alternativa_2.id,
                "nota": -2,
            }],
        }

        response = self.client.put(
            f"/api/v1/projects/{self.projeto.id}/alternative-comparisons/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(AvaliacaoAlternativas.objects.count(), 2)
        notas = sorted(AvaliacaoAlternativas.objects.values_list("nota",
                                                                 flat=True))
        self.assertEqual(notas, [-2, 2])

    def test_substituir_parametros(self):
        payload = {
            "parameters": [{
                "criterio_id": self.criterio_1.id,
                "p": 0.2,
                "q": 0.1,
                "v": 0.8,
            }, {
                "criterio_id": self.criterio_2.id,
                "p": 0.3,
                "q": 0.15,
                "v": 0.7,
            }],
        }

        response = self.client.put(
            f"/api/v1/projects/{self.projeto.id}/parameters/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(CriterioParametro.objects.count(), 2)
