from rest_framework.test import APITestCase

from core.models import Alternativa, Criterio, Decisor, Projeto


class ApiParticipantsTests(APITestCase):
    def setUp(self):
        self.projeto = Projeto.objects.create(
            nome="Proj participantes",
            descricao="Descricao",
            qtde_classes=2,
            qtde_criterios=2,
            qtde_alternativas=2,
            qtde_decisores=1,
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
        self.assertEqual(self.projeto.decisores.count(), 1)
        self.assertEqual(self.projeto.criterios.count(), 2)
        self.assertEqual(self.projeto.alternativas.count(), 2)
        self.assertEqual(
            sorted(self.projeto.decisores.values_list("nome", flat=True)),
            ["Decisor A"],
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

    def test_participantes_cria_primeiro_decisor_com_token_e_flag_criador(self):
        payload = {
            "decisores": [{
                "nome": "Criador"
            }],
            "criterios": [{
                "nome": "Qualidade",
                "numerico": False,
                "monotonico": 1,
            }, {
                "nome": "Custo",
                "numerico": True,
                "monotonico": 2,
            }],
            "alternativas": [{
                "nome": "A"
            }, {
                "nome": "B"
            }],
        }

        response = self.client.put(
            f"/api/v1/projects/{self.projeto.id}/participants/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        decisor = Decisor.objects.get(projeto=self.projeto, nome="Criador")
        self.assertTrue(decisor.is_criador)
        self.assertTrue(decisor.ativo)
        self.assertEqual(decisor.status, Decisor.Status.PENDENTE)
        self.assertGreaterEqual(len(decisor.token), 32)

    def test_criador_lista_decisores_e_retorna_links(self):
        response = self.client.get(
            f"/api/v1/projects/{self.projeto.id}/decision-makers/")

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["nome"], "Antigo decisor")
        self.assertIn("token", response.data[0])
        self.assertIn("evaluation_url", response.data[0])

    def test_criador_adiciona_decisor_convidado_e_recebe_link(self):
        response = self.client.post(
            f"/api/v1/projects/{self.projeto.id}/decision-makers/",
            {"nome": "Ana Souza"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["nome"], "Ana Souza")
        self.assertIn("token", response.data)
        self.assertIn("evaluation_url", response.data)
        self.assertIn("decisorToken=", response.data["evaluation_url"])
        self.assertIn("projectId=", response.data["evaluation_url"])
        self.assertIn("view=avaliacao", response.data["evaluation_url"])

    def test_criador_desativa_decisor_pendente(self):
        decisor = Decisor.objects.create(projeto=self.projeto, nome="Ana Souza")

        response = self.client.post(
            f"/api/v1/projects/{self.projeto.id}/decision-makers/{decisor.id}/disable/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        decisor.refresh_from_db()
        self.assertFalse(decisor.ativo)
        self.assertEqual(decisor.status, Decisor.Status.DESATIVADO)
