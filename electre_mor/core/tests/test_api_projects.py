from django.urls import reverse
from rest_framework.test import APITestCase

from core.models import (Alternativa, AlternativaCriterio,
                         AvaliacaoCriterios, Criterio, CriterioParametro,
                         Decisor, Projeto)


class ApiProjectsTests(APITestCase):
    def setUp(self):
        self.projeto = Projeto.objects.create(
            nome="Projeto inicial",
            descricao="Descricao inicial",
            qtde_classes=2,
            qtde_criterios=2,
            qtde_alternativas=2,
            qtde_decisores=1,
            lamb=0.5,
        )

    def test_listar_projetos(self):
        response = self.client.get("/api/v1/projects/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["nome"], "Projeto inicial")

    def test_criar_projeto(self):
        payload = {
            "nome": "Projeto novo",
            "descricao": "Descricao do projeto novo",
            "qtde_classes": 2,
            "qtde_criterios": 3,
            "qtde_alternativas": 3,
            "qtde_decisores": 1,
            "lamb": 0.75,
        }

        response = self.client.post("/api/v1/projects/",
                                    payload,
                                    format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["nome"], payload["nome"])
        self.assertEqual(Projeto.objects.count(), 2)
        self.assertTrue(Projeto.objects.filter(nome="Projeto novo").exists())

    def test_recuperar_e_excluir_projeto(self):
        detail_url = f"/api/v1/projects/{self.projeto.id}/"

        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.projeto.id)

        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, 204)
        self.assertFalse(Projeto.objects.filter(id=self.projeto.id).exists())

    def test_mutacoes_padrao_sao_bloqueadas_apos_gerar_resultado(self):
        decisor = Decisor.objects.create(projeto=self.projeto, nome="Decisor 1")
        criterio_1 = Criterio.objects.create(
            projeto=self.projeto,
            nome="Criterio 1",
            numerico=True,
            monotonico=1,
        )
        criterio_2 = Criterio.objects.create(
            projeto=self.projeto,
            nome="Criterio 2",
            numerico=True,
            monotonico=2,
        )
        alternativa_1 = Alternativa.objects.create(
            projeto=self.projeto,
            nome="Alternativa 1",
        )
        alternativa_2 = Alternativa.objects.create(
            projeto=self.projeto,
            nome="Alternativa 2",
        )

        AvaliacaoCriterios.objects.create(
            projeto=self.projeto,
            decisor=decisor,
            criterioA=criterio_1,
            criterioB=criterio_2,
            nota=1,
        )
        AvaliacaoCriterios.objects.create(
            projeto=self.projeto,
            decisor=decisor,
            criterioA=criterio_2,
            criterioB=criterio_1,
            nota=-1,
        )
        AlternativaCriterio.objects.create(
            projeto=self.projeto,
            decisor=decisor,
            criterio=criterio_1,
            alternativa=alternativa_1,
            nota=8,
        )
        AlternativaCriterio.objects.create(
            projeto=self.projeto,
            decisor=decisor,
            criterio=criterio_1,
            alternativa=alternativa_2,
            nota=4,
        )
        AlternativaCriterio.objects.create(
            projeto=self.projeto,
            decisor=decisor,
            criterio=criterio_2,
            alternativa=alternativa_1,
            nota=3,
        )
        AlternativaCriterio.objects.create(
            projeto=self.projeto,
            decisor=decisor,
            criterio=criterio_2,
            alternativa=alternativa_2,
            nota=7,
        )
        CriterioParametro.objects.create(
            projeto=self.projeto,
            criterio=criterio_1,
            p=0.2,
            q=0.1,
            v=0.8,
        )
        CriterioParametro.objects.create(
            projeto=self.projeto,
            criterio=criterio_2,
            p=0.3,
            q=0.1,
            v=0.7,
        )

        generate_response = self.client.post(
            f"/api/v1/projects/{self.projeto.id}/generate-result/",
            {},
            format="json",
        )
        self.assertEqual(generate_response.status_code, 200)

        detail_url = f"/api/v1/projects/{self.projeto.id}/"
        payload = {
            "nome": "Projeto alterado",
            "descricao": self.projeto.descricao,
            "qtde_classes": self.projeto.qtde_classes,
            "qtde_criterios": self.projeto.qtde_criterios,
            "qtde_alternativas": self.projeto.qtde_alternativas,
            "qtde_decisores": self.projeto.qtde_decisores,
            "lamb": self.projeto.lamb,
        }

        put_response = self.client.put(detail_url, payload, format="json")
        patch_response = self.client.patch(
            detail_url,
            {"nome": "Projeto alterado"},
            format="json",
        )
        delete_response = self.client.delete(detail_url)

        self.assertEqual(put_response.status_code, 409)
        self.assertEqual(patch_response.status_code, 409)
        self.assertEqual(delete_response.status_code, 409)
        self.assertTrue(Projeto.objects.filter(id=self.projeto.id).exists())
