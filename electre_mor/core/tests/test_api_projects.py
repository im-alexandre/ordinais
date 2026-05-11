from django.urls import reverse
from rest_framework.test import APITestCase

from core.models import Projeto


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
