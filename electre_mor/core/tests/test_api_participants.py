from django.urls import reverse
from rest_framework.test import APITestCase

from core.models import Alternativa, Criterio, Decisor, Projeto


class ApiParticipantsTests(APITestCase):
    def setUp(self):
        self.projeto = Projeto.objects.create(
            nome="Projeto participantes",
            descricao="Descricao",
            qtde_classes=2,
            qtde_criterios=2,
            qtde_alternativas=2,
            qtde_decisores=2,
            lamb=0.6,
        )
        Decisor.objects.create(projeto=self.projeto, nome="Antigo decisor")
        Criterio.objects.create(
            projeto=self.projeto,
            nome="Antigo criterio",
            numerico=True,
            monotonico=1,
        )
        Alternativa.objects.create(projeto=self.projeto, nome="Antiga alternativa")

    def test_substituir_participantes_do_projeto(self):
        payload = {
            "decisores": [{
                "nome": "Decisor A"
            }, {
                "nome": "Decisor B"
            }],
            "criterios": [{
                "nome": "Criterio A",
                "numerico": True,
                "monotonico": 1,
            }, {
                "nome": "Criterio B",
                "numerico": False,
                "monotonico": 2,
            }],
            "alternativas": [{
                "nome": "Alternativa A"
            }, {
                "nome": "Alternativa B"
            }],
        }

        response = self.client.put(
            f"/api/v1/projects/{self.projeto.id}/participants/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.projeto.refresh_from_db()
        self.assertEqual(self.projeto.decisores.count(), 2)
        self.assertEqual(self.projeto.criterios.count(), 2)
        self.assertEqual(self.projeto.alternativas.count(), 2)
        self.assertEqual(
            sorted(self.projeto.decisores.values_list("nome", flat=True)),
            ["Decisor A", "Decisor B"],
        )
        self.assertFalse(
            self.projeto.decisores.filter(nome="Antigo decisor").exists())

    def test_rejeita_payload_incompleto(self):
        response = self.client.put(
            f"/api/v1/projects/{self.projeto.id}/participants/",
            {"decisores": []},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
