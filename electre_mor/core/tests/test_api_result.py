from django.core.cache import cache
from rest_framework.test import APITestCase

from core.method import MatrizProjeto
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
        gerar_response = self.client.post(
            f"/api/v1/projects/{self.projeto.id}/generate-result/",
            {},
            format="json",
        )

        self.assertEqual(gerar_response.status_code, 200)
        self.assertIn("classificacao_final", gerar_response.data)

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

        gerar_response = self.client.post(
            f"/api/v1/projects/{projeto.id}/generate-result/",
            {},
            format="json",
        )

        self.assertEqual(gerar_response.status_code, 200)

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

    def test_resultado_precisa_ser_gerado_manual_antes_de_consultar(self):
        response = self.client.get(f"/api/v1/projects/{self.projeto.id}/result/")

        self.assertEqual(response.status_code, 409)
        self.assertIn("pendencias", response.data)

        gerar_response = self.client.post(
            f"/api/v1/projects/{self.projeto.id}/generate-result/",
            {},
            format="json",
        )

        self.assertEqual(gerar_response.status_code, 200)
        self.assertIn("classificacao_final", gerar_response.data)

        self.projeto.refresh_from_db()
        self.assertIsNotNone(self.projeto.resultado_gerado_em)

        consulta_response = self.client.get(
            f"/api/v1/projects/{self.projeto.id}/result/")

        self.assertEqual(consulta_response.status_code, 200)
        self.assertEqual(consulta_response.data["project"]["id"],
                         self.projeto.id)

        cache.clear()

        consulta_apos_clear = self.client.get(
            f"/api/v1/projects/{self.projeto.id}/result/")

        self.assertEqual(consulta_apos_clear.status_code, 200)
        self.assertEqual(consulta_apos_clear.data["project"]["id"],
                         self.projeto.id)

    def test_resultado_permanece_igual_apos_cache_clear_e_mudanca_na_base(self):
        gerar_response = self.client.post(
            f"/api/v1/projects/{self.projeto.id}/generate-result/",
            {},
            format="json",
        )

        self.assertEqual(gerar_response.status_code, 200)

        self.projeto.refresh_from_db()
        self.assertEqual(self.projeto.resultado_snapshot,
                         gerar_response.data)

        snapshot_gerado = gerar_response.data

        AlternativaCriterio.objects.filter(
            projeto=self.projeto,
            criterio=self.criterio_1,
            alternativa=self.alternativa_1,
        ).update(nota=99)

        cache.clear()

        response = self.client.get(f"/api/v1/projects/{self.projeto.id}/result/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, snapshot_gerado)
        self.assertEqual(response.data, self.projeto.resultado_snapshot)

    def test_resultado_legado_sem_snapshot_recalcula_uma_vez_e_persiste(self):
        from django.utils import timezone

        self.projeto.resultado_gerado_em = timezone.now()
        self.projeto.resultado_snapshot = {}
        self.projeto.save(update_fields=["resultado_gerado_em",
                                         "resultado_snapshot"])
        cache.clear()

        response = self.client.get(f"/api/v1/projects/{self.projeto.id}/result/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("classificacao_final", response.data)

        self.projeto.refresh_from_db()
        self.assertEqual(self.projeto.resultado_snapshot, response.data)

    def test_resultado_legado_sem_snapshot_persiste_valor_do_cache(self):
        from django.utils import timezone

        gerar_response = self.client.post(
            f"/api/v1/projects/{self.projeto.id}/generate-result/",
            {},
            format="json",
        )
        snapshot = gerar_response.data
        self.projeto.refresh_from_db()
        cache.set(
            f"electre_mor:resultado_gerado:{self.projeto.id}:{self.projeto.data.isoformat()}",
            snapshot,
            timeout=None,
        )
        self.projeto.resultado_gerado_em = timezone.now()
        self.projeto.resultado_snapshot = {}
        self.projeto.save(update_fields=["resultado_gerado_em",
                                         "resultado_snapshot"])

        response = self.client.get(f"/api/v1/projects/{self.projeto.id}/result/")

        self.assertEqual(response.status_code, 200)
        self.projeto.refresh_from_db()
        self.assertEqual(self.projeto.resultado_snapshot, snapshot)

    def test_resultado_retorna_pendencias_quando_faltam_avaliacoes_de_decisores_ativos(self):
        projeto = Projeto.objects.create(
            nome="Projeto pendencias",
            descricao="Descricao",
            qtde_classes=2,
            qtde_criterios=2,
            qtde_alternativas=2,
            qtde_decisores=2,
            lamb=0.6,
        )
        Decisor.objects.create(projeto=projeto, nome="D1")
        Decisor.objects.create(projeto=projeto, nome="D2")

        Criterio.objects.create(
            projeto=projeto,
            nome="Criterio 1",
            numerico=True,
            monotonico=1,
        )
        Criterio.objects.create(
            projeto=projeto,
            nome="Criterio 2",
            numerico=True,
            monotonico=2,
        )
        Alternativa.objects.create(projeto=projeto, nome="A")
        Alternativa.objects.create(projeto=projeto, nome="B")

        response = self.client.get(f"/api/v1/projects/{projeto.id}/result/")

        self.assertEqual(response.status_code, 409)
        self.assertIn("pendencias", response.data)

    def test_agrega_dois_decisores_ativos_com_peso_igual(self):
        from core.services.result_service import obter_resultado_agregado

        projeto = Projeto.objects.create(
            nome="Projeto agregado",
            descricao="Descricao",
            qtde_classes=2,
            qtde_criterios=2,
            qtde_alternativas=2,
            qtde_decisores=2,
            lamb=0.6,
        )
        decisor_1 = Decisor.objects.create(projeto=projeto, nome="D1")
        decisor_2 = Decisor.objects.create(projeto=projeto, nome="D2")

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
        alternativa_1 = Alternativa.objects.create(projeto=projeto, nome="A")
        alternativa_2 = Alternativa.objects.create(projeto=projeto, nome="B")

        for decisor, nota_criterio, nota_alternativa in (
            (decisor_1, 1, (8.0, 4.0)),
            (decisor_2, 2, (6.0, 2.0)),
        ):
            AvaliacaoCriterios.objects.create(
                projeto=projeto,
                decisor=decisor,
                criterioA=criterio_1,
                criterioB=criterio_2,
                nota=nota_criterio,
            )
            AvaliacaoCriterios.objects.create(
                projeto=projeto,
                decisor=decisor,
                criterioA=criterio_2,
                criterioB=criterio_1,
                nota=-nota_criterio,
            )
            AlternativaCriterio.objects.create(
                projeto=projeto,
                decisor=decisor,
                criterio=criterio_1,
                alternativa=alternativa_1,
                nota=nota_alternativa[0],
            )
            AlternativaCriterio.objects.create(
                projeto=projeto,
                decisor=decisor,
                criterio=criterio_1,
                alternativa=alternativa_2,
                nota=nota_alternativa[1],
            )
            AlternativaCriterio.objects.create(
                projeto=projeto,
                decisor=decisor,
                criterio=criterio_2,
                alternativa=alternativa_1,
                nota=5.0 if decisor == decisor_2 else 7.0,
            )
            AlternativaCriterio.objects.create(
                projeto=projeto,
                decisor=decisor,
                criterio=criterio_2,
                alternativa=alternativa_2,
                nota=1.0 if decisor == decisor_2 else 3.0,
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

        resultado = obter_resultado_agregado(projeto)

        self.assertEqual(resultado["decisores_ativos"], 2)
        self.assertIn("classificacao_final", resultado)

        matriz = MatrizProjeto(projeto)
        pontuacao_alternativas = matriz.pontuacao_alternativas
        pontuacao_alternativas.index = pontuacao_alternativas.index.astype(int)
        pontuacao_alternativas.columns = pontuacao_alternativas.columns.astype(int)
        self.assertIn(alternativa_1.id, pontuacao_alternativas.index)
        self.assertIn(criterio_1.id, pontuacao_alternativas.columns)
        self.assertAlmostEqual(
            pontuacao_alternativas.loc[alternativa_1.id, criterio_1.id],
            7.0,
        )
