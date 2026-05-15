from django.core.cache import cache
from rest_framework.test import APITestCase

from core.models import (Alternativa, AlternativaCriterio,
                         AvaliacaoAlternativas, AvaliacaoCriterios, Criterio,
                         CriterioParametro, Decisor, Projeto)
from core.services.evaluation_service import (
    substituir_comparacoes_alternativas,
    substituir_comparacoes_criterios,
    substituir_notas_numericas,
)


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
                                               nome="D1")
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
                "decisor_id": self.decisor.id,
                "criterio_id": self.criterio_1.id,
                "alternativa_id": self.alternativa_1.id,
                "nota": 8.5,
            }, {
                "decisor_id": self.decisor.id,
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
        self.assertEqual(response.data["scores"][0]["decisor_id"],
                         self.decisor.id)
        self.assertTrue(
            AlternativaCriterio.objects.filter(decisor=self.decisor).exists())

    def test_contexto_avaliacao_por_token_retorna_projeto_e_decisor_ativo(self):
        response = self.client.get(
            f"/api/v1/projects/{self.projeto.id}/evaluation-token/{self.decisor.token}/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["project"]["id"], self.projeto.id)
        self.assertEqual(response.data["decisor"]["id"], self.decisor.id)
        self.assertEqual(response.data["decisor"]["token"],
                         self.decisor.token)

    def test_token_invalido_nao_resolve_avaliacao(self):
        response = self.client.get(
            f"/api/v1/projects/{self.projeto.id}/evaluation-token/invalido/"
        )

        self.assertEqual(response.status_code, 404)

    def test_decisor_desativado_retorna_410_no_contexto_por_token(self):
        decisor = Decisor.objects.create(
            projeto=self.projeto,
            nome="Desativado",
            ativo=False,
            status=Decisor.Status.DESATIVADO,
        )

        response = self.client.get(
            f"/api/v1/projects/{self.projeto.id}/evaluation-token/{decisor.token}/"
        )

        self.assertEqual(response.status_code, 410)

    def test_resultado_gerado_bloqueia_novas_notas_numericas(self):
        projeto = Projeto.objects.create(
            nome="Projeto bloqueio",
            descricao="Descricao",
            qtde_classes=2,
            qtde_criterios=2,
            qtde_alternativas=2,
            qtde_decisores=1,
            lamb=0.7,
        )
        decisor = Decisor.objects.create(projeto=projeto, nome="D1")
        criterio_1 = Criterio.objects.create(
            projeto=projeto,
            nome="Criterio 1",
            numerico=True,
            monotonico=1,
        )
        criterio_2 = Criterio.objects.create(
            projeto=projeto,
            nome="Criterio 2",
            numerico=True,
            monotonico=2,
        )
        alternativa_1 = Alternativa.objects.create(projeto=projeto,
                                                   nome="Alternativa 1")
        alternativa_2 = Alternativa.objects.create(projeto=projeto,
                                                   nome="Alternativa 2")
        AvaliacaoCriterios.objects.create(
            projeto=projeto,
            decisor=decisor,
            criterioA=criterio_1,
            criterioB=criterio_2,
            nota=1,
        )
        AvaliacaoCriterios.objects.create(
            projeto=projeto,
            decisor=decisor,
            criterioA=criterio_2,
            criterioB=criterio_1,
            nota=-1,
        )
        AlternativaCriterio.objects.create(
            projeto=projeto,
            decisor=decisor,
            criterio=criterio_1,
            alternativa=alternativa_1,
            nota=8,
        )
        AlternativaCriterio.objects.create(
            projeto=projeto,
            decisor=decisor,
            criterio=criterio_1,
            alternativa=alternativa_2,
            nota=4,
        )
        AlternativaCriterio.objects.create(
            projeto=projeto,
            decisor=decisor,
            criterio=criterio_2,
            alternativa=alternativa_1,
            nota=7,
        )
        AlternativaCriterio.objects.create(
            projeto=projeto,
            decisor=decisor,
            criterio=criterio_2,
            alternativa=alternativa_2,
            nota=3,
        )
        CriterioParametro.objects.create(
            projeto=projeto,
            criterio=criterio_1,
            p=0.2,
            q=0.1,
            v=0.8,
        )
        CriterioParametro.objects.create(
            projeto=projeto,
            criterio=criterio_2,
            p=0.3,
            q=0.1,
            v=0.7,
        )

        gerar_response = self.client.post(
            f"/api/v1/projects/{projeto.id}/generate-result/",
            {},
            format="json",
        )
        self.assertEqual(gerar_response.status_code, 200)

        cache.clear()

        consulta_response = self.client.get(
            f"/api/v1/projects/{projeto.id}/result/")
        self.assertEqual(consulta_response.status_code, 200)

        response = self.client.put(
            f"/api/v1/projects/{projeto.id}/numeric-scores/",
            {
                "scores": [{
                    "decisor_id": decisor.id,
                    "criterio_id": criterio_1.id,
                    "alternativa_id": alternativa_1.id,
                    "nota": 8.5,
                }],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 409)

    def test_resultado_gerado_bloqueia_novo_decisor(self):
        projeto = Projeto.objects.create(
            nome="Projeto bloqueio",
            descricao="Descricao",
            qtde_classes=2,
            qtde_criterios=2,
            qtde_alternativas=2,
            qtde_decisores=1,
            lamb=0.7,
        )
        decisor = Decisor.objects.create(projeto=projeto, nome="D1")
        criterio_1 = Criterio.objects.create(
            projeto=projeto,
            nome="Criterio 1",
            numerico=True,
            monotonico=1,
        )
        criterio_2 = Criterio.objects.create(
            projeto=projeto,
            nome="Criterio 2",
            numerico=True,
            monotonico=2,
        )
        alternativa_1 = Alternativa.objects.create(projeto=projeto,
                                                   nome="Alternativa 1")
        alternativa_2 = Alternativa.objects.create(projeto=projeto,
                                                   nome="Alternativa 2")
        AvaliacaoCriterios.objects.create(
            projeto=projeto,
            decisor=decisor,
            criterioA=criterio_1,
            criterioB=criterio_2,
            nota=1,
        )
        AvaliacaoCriterios.objects.create(
            projeto=projeto,
            decisor=decisor,
            criterioA=criterio_2,
            criterioB=criterio_1,
            nota=-1,
        )
        AlternativaCriterio.objects.create(
            projeto=projeto,
            decisor=decisor,
            criterio=criterio_1,
            alternativa=alternativa_1,
            nota=8,
        )
        AlternativaCriterio.objects.create(
            projeto=projeto,
            decisor=decisor,
            criterio=criterio_1,
            alternativa=alternativa_2,
            nota=4,
        )
        AlternativaCriterio.objects.create(
            projeto=projeto,
            decisor=decisor,
            criterio=criterio_2,
            alternativa=alternativa_1,
            nota=7,
        )
        AlternativaCriterio.objects.create(
            projeto=projeto,
            decisor=decisor,
            criterio=criterio_2,
            alternativa=alternativa_2,
            nota=3,
        )
        CriterioParametro.objects.create(
            projeto=projeto,
            criterio=criterio_1,
            p=0.2,
            q=0.1,
            v=0.8,
        )
        CriterioParametro.objects.create(
            projeto=projeto,
            criterio=criterio_2,
            p=0.3,
            q=0.1,
            v=0.7,
        )

        gerar_response = self.client.post(
            f"/api/v1/projects/{projeto.id}/generate-result/",
            {},
            format="json",
        )
        self.assertEqual(gerar_response.status_code, 200)

        response = self.client.post(
            f"/api/v1/projects/{projeto.id}/decision-makers/",
            {"nome": "D2"},
            format="json",
        )

        self.assertEqual(response.status_code, 409)

    def test_notas_numericas_sao_independentes_por_decisor(self):
        decisor_2 = Decisor.objects.create(projeto=self.projeto, nome="D2")

        substituir_notas_numericas(
            self.projeto, {
                "scores": [{
                    "decisor": self.decisor,
                    "criterio": self.criterio_1,
                    "alternativa": self.alternativa_1,
                    "nota": 8.0,
                }],
            })
        substituir_notas_numericas(
            self.projeto, {
                "scores": [{
                    "decisor": decisor_2,
                    "criterio": self.criterio_1,
                    "alternativa": self.alternativa_1,
                    "nota": 4.0,
                }],
            })

        notas = AlternativaCriterio.objects.filter(
            projeto=self.projeto,
            criterio=self.criterio_1,
            alternativa=self.alternativa_1,
        ).order_by("decisor__nome").values_list("decisor__nome", "nota")
        self.assertEqual(list(notas), [("D1", 8.0), ("D2", 4.0)])

    def test_numeric_scores_api_preserva_dois_decisores(self):
        decisor_2 = Decisor.objects.create(projeto=self.projeto, nome="D2")

        response_1 = self.client.put(
            f"/api/v1/projects/{self.projeto.id}/numeric-scores/",
            {
                "scores": [{
                    "decisor_id": self.decisor.id,
                    "criterio_id": self.criterio_1.id,
                    "alternativa_id": self.alternativa_1.id,
                    "nota": 8.0,
                }],
            },
            format="json",
        )
        self.assertEqual(response_1.status_code, 200)

        response_2 = self.client.put(
            f"/api/v1/projects/{self.projeto.id}/numeric-scores/",
            {
                "scores": [{
                    "decisor_id": decisor_2.id,
                    "criterio_id": self.criterio_1.id,
                    "alternativa_id": self.alternativa_1.id,
                    "nota": 4.0,
                }],
            },
            format="json",
        )
        self.assertEqual(response_2.status_code, 200)

        notas = AlternativaCriterio.objects.filter(
            projeto=self.projeto,
            criterio=self.criterio_1,
            alternativa=self.alternativa_1,
        ).order_by("decisor__nome").values_list("decisor__nome", "nota")
        self.assertEqual(list(notas), [("D1", 8.0), ("D2", 4.0)])

    def test_comparacoes_de_criterios_ficam_separadas_por_decisor(self):
        decisor_2 = Decisor.objects.create(projeto=self.projeto, nome="D2")

        substituir_comparacoes_criterios(
            self.projeto, {
                "comparisons": [{
                    "decisor": self.decisor,
                    "criterioA": self.criterio_1,
                    "criterioB": self.criterio_2,
                    "nota": 1,
                }],
            })
        substituir_comparacoes_criterios(
            self.projeto, {
                "comparisons": [{
                    "decisor": decisor_2,
                    "criterioA": self.criterio_1,
                    "criterioB": self.criterio_2,
                    "nota": 2,
                }],
            })

        notas = list(
            AvaliacaoCriterios.objects.filter(projeto=self.projeto).order_by(
                "decisor__nome", "nota").values_list("decisor__nome", "nota"))
        self.assertEqual(notas, [("D1", -1), ("D1", 1), ("D2", -2),
                                 ("D2", 2)])

    def test_comparacoes_de_alternativas_ficam_separadas_por_decisor(self):
        decisor_2 = Decisor.objects.create(projeto=self.projeto, nome="D2")

        substituir_comparacoes_alternativas(
            self.projeto, {
                "comparisons": [{
                    "decisor": self.decisor,
                    "criterio": self.criterio_2,
                    "alternativaA": self.alternativa_1,
                    "alternativaB": self.alternativa_2,
                    "nota": -2,
                }],
            })
        substituir_comparacoes_alternativas(
            self.projeto, {
                "comparisons": [{
                    "decisor": decisor_2,
                    "criterio": self.criterio_2,
                    "alternativaA": self.alternativa_1,
                    "alternativaB": self.alternativa_2,
                    "nota": -1,
                }],
            })

        notas = list(
            AvaliacaoAlternativas.objects.filter(
                projeto=self.projeto).order_by("decisor__nome",
                                                "nota").values_list(
                                                    "decisor__nome", "nota"))
        self.assertEqual(notas, [("D1", -2), ("D1", 2), ("D2", -1),
                                 ("D2", 1)])

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
