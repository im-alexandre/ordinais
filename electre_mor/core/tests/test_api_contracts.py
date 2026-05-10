from rest_framework.test import APITestCase

from core.models import Projeto


class ApiContractsSmokeTests(APITestCase):
    def test_fluxo_principal_da_api_permanece_consistente(self):
        create_response = self.client.post(
            "/api/v1/projects/",
            {
                "nome": "Contrato",
                "descricao": "Fluxo de contrato",
                "qtde_classes": 2,
                "qtde_criterios": 2,
                "qtde_alternativas": 2,
                "qtde_decisores": 1,
                "lamb": 0.5,
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, 201)

        projeto_id = create_response.data["id"]
        self.assertTrue(Projeto.objects.filter(id=projeto_id).exists())

        participants_response = self.client.put(
            f"/api/v1/projects/{projeto_id}/participants/",
            {
                "decisores": [{
                    "nome": "Decisor 1"
                }],
                "criterios": [{
                    "nome": "Criterio 1",
                    "numerico": True,
                    "monotonico": 1,
                }, {
                    "nome": "Criterio 2",
                    "numerico": True,
                    "monotonico": 2,
                }],
                "alternativas": [{
                    "nome": "Alternativa 1"
                }, {
                    "nome": "Alternativa 2"
                }],
            },
            format="json",
        )
        self.assertEqual(participants_response.status_code, 200)

        criterio_1_id = participants_response.data["criterios"][0]["id"]
        criterio_2_id = participants_response.data["criterios"][1]["id"]
        decisor_id = participants_response.data["decisores"][0]["id"]
        alternativa_1_id = participants_response.data["alternativas"][0]["id"]
        alternativa_2_id = participants_response.data["alternativas"][1]["id"]

        self.assertEqual(
            self.client.put(
                f"/api/v1/projects/{projeto_id}/criteria-comparisons/",
                {
                    "comparisons": [{
                        "decisor_id": decisor_id,
                        "criterio_a_id": criterio_1_id,
                        "criterio_b_id": criterio_2_id,
                        "nota": 1,
                    }],
                },
                format="json",
            ).status_code, 200)

        self.assertEqual(
            self.client.put(
                f"/api/v1/projects/{projeto_id}/numeric-scores/",
                {
                    "scores": [{
                        "criterio_id": criterio_1_id,
                        "alternativa_id": alternativa_1_id,
                        "nota": 8,
                    }, {
                        "criterio_id": criterio_1_id,
                        "alternativa_id": alternativa_2_id,
                        "nota": 4,
                    }, {
                        "criterio_id": criterio_2_id,
                        "alternativa_id": alternativa_1_id,
                        "nota": 3,
                    }, {
                        "criterio_id": criterio_2_id,
                        "alternativa_id": alternativa_2_id,
                        "nota": 7,
                    }],
                },
                format="json",
            ).status_code, 200)

        self.assertEqual(
            self.client.put(
                f"/api/v1/projects/{projeto_id}/parameters/",
                {
                    "parameters": [{
                        "criterio_id": criterio_1_id,
                        "p": 0.2,
                        "q": 0.1,
                        "v": 0.8,
                    }, {
                        "criterio_id": criterio_2_id,
                        "p": 0.3,
                        "q": 0.1,
                        "v": 0.7,
                    }],
                },
                format="json",
            ).status_code, 200)

        result_response = self.client.get(f"/api/v1/projects/{projeto_id}/result/")
        self.assertEqual(result_response.status_code, 200)
        self.assertEqual(result_response.data["project"]["id"], projeto_id)
