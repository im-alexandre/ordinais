from rest_framework.test import APITestCase

from core.models import (Alternativa, AlternativaCriterio,
                         AvaliacaoAlternativas, AvaliacaoCriterios, Criterio,
                         CriterioParametro, Decisor, Projeto)


class ApiResultTests(APITestCase):
    def setUp(self):
        self.projeto = Projeto.objects.create(
            nome="Projeto resultado",
            descricao="Descricao",
            qtde_classes=2,
            qtde_criterios=2,
            qtde_alternativas=2,
            qtde_decisores=1,
            lamb=0.6,
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
            numerico=True,
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

        AvaliacaoCriterios.objects.create(
            projeto=self.projeto,
            decisor=self.decisor,
            criterioA=self.criterio_1,
            criterioB=self.criterio_2,
            nota=1,
        )
        AvaliacaoCriterios.objects.create(
            projeto=self.projeto,
            decisor=self.decisor,
            criterioA=self.criterio_2,
            criterioB=self.criterio_1,
            nota=-1,
        )
        AlternativaCriterio.objects.create(
            projeto=self.projeto,
            criterio=self.criterio_1,
            alternativa=self.alternativa_1,
            nota=8,
        )
        AlternativaCriterio.objects.create(
            projeto=self.projeto,
            criterio=self.criterio_1,
            alternativa=self.alternativa_2,
            nota=4,
        )
        AlternativaCriterio.objects.create(
            projeto=self.projeto,
            criterio=self.criterio_2,
            alternativa=self.alternativa_1,
            nota=3,
        )
        AlternativaCriterio.objects.create(
            projeto=self.projeto,
            criterio=self.criterio_2,
            alternativa=self.alternativa_2,
            nota=7,
        )
        CriterioParametro.objects.create(
            projeto=self.projeto,
            criterio=self.criterio_1,
            p=0.2,
            q=0.1,
            v=0.8,
        )
        CriterioParametro.objects.create(
            projeto=self.projeto,
            criterio=self.criterio_2,
            p=0.3,
            q=0.1,
            v=0.7,
        )

    def test_resultado_e_consistente_com_dados_completos(self):
        response = self.client.get(f"/api/v1/projects/{self.projeto.id}/result/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["project"]["id"], self.projeto.id)
        self.assertIn("pesos_criterios", response.data)
        self.assertIn("pontuacao_alternativas", response.data)
        self.assertIn("classificacao_range", response.data)
        self.assertIn("classificacao_quantile", response.data)

    def test_resultado_retorna_conflito_quando_faltam_dados(self):
        projeto_incompleto = Projeto.objects.create(
            nome="Projeto incompleto",
            descricao="Descricao",
            qtde_classes=2,
            qtde_criterios=2,
            qtde_alternativas=2,
            qtde_decisores=1,
            lamb=0.6,
        )

        response = self.client.get(
            f"/api/v1/projects/{projeto_incompleto.id}/result/")

        self.assertEqual(response.status_code, 409)

    def test_resultado_misto_alinha_pesos_por_criterio(self):
        projeto = Projeto.objects.create(
            nome="Caso misto",
            descricao="Vacinas com custo, eficacia e qualidade logistica",
            qtde_classes=3,
            qtde_criterios=3,
            qtde_alternativas=3,
            qtde_decisores=1,
            lamb=0.65,
        )
        decisor = Decisor.objects.create(projeto=projeto, nome="Comite")
        qualidade = Criterio.objects.create(
            projeto=projeto,
            nome="Qualidade",
            numerico=False,
            monotonico=1,
        )
        custo = Criterio.objects.create(
            projeto=projeto,
            nome="Custo",
            numerico=True,
            monotonico=2,
        )
        eficacia = Criterio.objects.create(
            projeto=projeto,
            nome="Eficacia",
            numerico=True,
            monotonico=1,
        )
        alternativas = [
            Alternativa.objects.create(projeto=projeto, nome=nome)
            for nome in ("Vacina A", "Vacina B", "Vacina C")
        ]

        comparacoes_criterios = (
            (qualidade, custo, 2),
            (qualidade, eficacia, 1),
            (eficacia, custo, 1),
        )
        for criterio_a, criterio_b, nota in comparacoes_criterios:
            AvaliacaoCriterios.objects.create(
                projeto=projeto,
                decisor=decisor,
                criterioA=criterio_a,
                criterioB=criterio_b,
                nota=nota,
            )
            AvaliacaoCriterios.objects.create(
                projeto=projeto,
                decisor=decisor,
                criterioA=criterio_b,
                criterioB=criterio_a,
                nota=-nota,
            )

        comparacoes_qualidade = (
            (alternativas[0], alternativas[1], 1),
            (alternativas[0], alternativas[2], 2),
            (alternativas[1], alternativas[2], 1),
        )
        for alternativa_a, alternativa_b, nota in comparacoes_qualidade:
            AvaliacaoAlternativas.objects.create(
                projeto=projeto,
                decisor=decisor,
                criterio=qualidade,
                alternativaA=alternativa_a,
                alternativaB=alternativa_b,
                nota=nota,
            )
            AvaliacaoAlternativas.objects.create(
                projeto=projeto,
                decisor=decisor,
                criterio=qualidade,
                alternativaA=alternativa_b,
                alternativaB=alternativa_a,
                nota=-nota,
            )

        notas = {
            custo: (42, 35, 55),
            eficacia: (91, 86, 94),
        }
        for criterio, valores in notas.items():
            for alternativa, nota in zip(alternativas, valores):
                AlternativaCriterio.objects.create(
                    projeto=projeto,
                    criterio=criterio,
                    alternativa=alternativa,
                    nota=nota,
                )

        for criterio in (qualidade, custo, eficacia):
            CriterioParametro.objects.create(
                projeto=projeto,
                criterio=criterio,
                p=0.2,
                q=0.1,
                v=0.8,
            )

        response = self.client.get(f"/api/v1/projects/{projeto.id}/result/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["classificacao_final"]["range"]), 3)
        self.assertEqual(len(response.data["classificacao_final"]["quantile"]), 3)
        self.assertEqual(
            response.data["pesos_criterios"][0]["criterio_nome"],
            "Qualidade",
        )
        self.assertEqual(
            sorted(item["alternative"]
                   for item in response.data["classificacao_final"]["range"]),
            ["Vacina A", "Vacina B", "Vacina C"],
        )
