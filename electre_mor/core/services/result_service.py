from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from core.ElectreTri import ElectreTri
from core.method import MatrizProjeto
from core.models import (CriterioParametro, Decisor, Projeto)
from core.tabular import queryset_para_dataframe


_CACHE_PREFIX = "electre_mor:resultado_gerado"


@dataclass
class ResultadoIndisponivel(Exception):
    motivo: str
    pendencias: list[dict[str, Any]] | None = None


def _cache_key(projeto: Projeto) -> str:
    data_chave = projeto.data.isoformat() if projeto.data else "sem-data"
    return f"{_CACHE_PREFIX}:{projeto.id}:{data_chave}"


def resultado_gerado(projeto: Projeto) -> bool:
    return projeto.resultado_gerado_em is not None


def obter_resultado_gerado(projeto: Projeto) -> dict[str, Any]:
    if not resultado_gerado(projeto):
        raise ResultadoIndisponivel(
            "Resultado ainda nao gerado manualmente.",
            pendencias=obter_pendencias_resultado(projeto),
        )

    resultado = cache.get(_cache_key(projeto))
    if resultado is None:
        resultado = obter_resultado_agregado(projeto)
        cache.set(_cache_key(projeto), resultado, timeout=None)
    return resultado


def _decisores_ativos(projeto: Projeto):
    return list(
        projeto.decisores.filter(ativo=True).exclude(
            status=Decisor.Status.DESATIVADO).order_by("id"))


def _criterios_scoped(projeto: Projeto) -> bool:
    return projeto.avaliacaocriterios.filter(decisor__isnull=False).exists()


def _notas_numericas_scoped(projeto: Projeto) -> bool:
    return projeto.alternativacriterios.filter(decisor__isnull=False).exists()


def _alternativas_scoped(projeto: Projeto) -> bool:
    return projeto.avaliacaoalternativas.filter(decisor__isnull=False).exists()


def _contagens_esperadas(projeto: Projeto) -> dict[str, int]:
    criterios = list(projeto.criterios.all())
    alternativas = list(projeto.alternativas.all())
    criterios_numericos = [criterio for criterio in criterios if criterio.numerico]
    criterios_qualitativos = [criterio for criterio in criterios if not criterio.numerico]

    total_criterios = len(criterios)
    total_alternativas = len(alternativas)

    return {
        "criterios": total_criterios * (total_criterios - 1)
        if total_criterios > 1 else 0,
        "notas_numericas": len(criterios_numericos) * total_alternativas
        if criterios_numericos and total_alternativas > 0 else 0,
        "comparacoes_alternativas": len(criterios_qualitativos) * total_alternativas *
        (total_alternativas - 1)
        if criterios_qualitativos and total_alternativas > 1 else 0,
        "parametros": total_criterios,
    }


def _faltas_para_decisor(projeto: Projeto, decisor: Decisor,
                         usa_escopo_por_decisor: bool) -> list[str]:
    faltas: list[str] = []
    esperados = _contagens_esperadas(projeto)
    criterios_scoped = _criterios_scoped(projeto)
    notas_numericas_scoped = _notas_numericas_scoped(projeto)
    alternativas_scoped = _alternativas_scoped(projeto)

    if projeto.criterios.count() == 0:
        faltas.append("criterios")
    if projeto.alternativas.count() == 0:
        faltas.append("alternativas")
    if projeto.criterioparametro.count() != esperados["parametros"]:
        faltas.append("parametros")

    if criterios_scoped and usa_escopo_por_decisor:
        qtd_criterios = decisor.avaliacaocriterios.count()
    else:
        qtd_criterios = projeto.avaliacaocriterios.count()

    if notas_numericas_scoped and usa_escopo_por_decisor:
        qtd_notas = decisor.alternativacriterios.count()
    else:
        qtd_notas = projeto.alternativacriterios.count()

    if alternativas_scoped and usa_escopo_por_decisor:
        qtd_alternativas = decisor.avaliacaoalternativas.count()
    else:
        qtd_alternativas = projeto.avaliacaoalternativas.count()

    if esperados["criterios"] and qtd_criterios < esperados["criterios"]:
        faltas.append("comparacoes_criterios")
    if esperados["notas_numericas"] and qtd_notas < esperados["notas_numericas"]:
        faltas.append("notas_numericas")
    if esperados["comparacoes_alternativas"] and qtd_alternativas < esperados[
            "comparacoes_alternativas"]:
        faltas.append("comparacoes_alternativas")

    return faltas


def obter_pendencias_resultado(projeto: Projeto) -> list[dict[str, Any]]:
    decisores_ativos = _decisores_ativos(projeto)
    if not decisores_ativos:
        return [{
            "id": 0,
            "nome": "Decisores ativos",
            "status": "pendente",
            "ativo": False,
            "faltas": ["decisores_ativos"],
        }]

    usa_escopo_por_decisor = any((
        _criterios_scoped(projeto),
        _notas_numericas_scoped(projeto),
        _alternativas_scoped(projeto),
    ))
    pendencias = []
    for decisor in decisores_ativos:
        faltas = _faltas_para_decisor(projeto, decisor,
                                      usa_escopo_por_decisor)
        if faltas:
            pendencias.append({
                "id": decisor.id,
                "nome": decisor.nome,
                "status": decisor.status,
                "ativo": decisor.ativo,
                "faltas": faltas,
            })
    return pendencias


def _aplicar_escopo_projeto(matriz: MatrizProjeto, projeto: Projeto,
                            decisores_ativos: list[Decisor]) -> tuple[MatrizProjeto, int]:
    if not decisores_ativos:
        return matriz, 1

    decisor_ids = [decisor.id for decisor in decisores_ativos]
    if _criterios_scoped(projeto):
        matriz.avaliacoes_criterios = matriz.avaliacoes_criterios.filter(
            decisor_id__in=decisor_ids)
    if _alternativas_scoped(projeto):
        matriz.avaliacoes_alternativas = matriz.avaliacoes_alternativas.filter(
            decisor_id__in=decisor_ids)
    if _notas_numericas_scoped(projeto):
        matriz.alternativas_criterios = matriz.alternativas_criterios.filter(
            decisor_id__in=decisor_ids)
    return matriz, len(decisores_ativos)


def _montar_resultado(projeto: Projeto, matriz: MatrizProjeto,
                      decisores_ativos: list[Decisor], divisor: int
                      ) -> dict[str, Any]:
    pesos = matriz.pesos_criterios.reset_index(drop=True)
    if "criterio" not in pesos.columns:
        coluna_criterio = next(coluna for coluna in pesos.columns
                               if coluna != "peso")
        pesos = pesos.rename(columns={coluna_criterio: "criterio"})
    if divisor > 1:
        pesos["peso"] = pesos["peso"] / divisor

    pontuacao = matriz.pontuacao_alternativas
    if pontuacao is None or pontuacao.empty:
        raise ResultadoIndisponivel(
            "Pontuacao das alternativas indisponivel.",
            pendencias=obter_pendencias_resultado(projeto),
        )
    criterios_numericos = {
        criterio.id for criterio in projeto.criterios.filter(numerico=True)
    }
    if divisor > 1:
        colunas_divisiveis = [
            coluna for coluna in pontuacao.columns
            if coluna not in criterios_numericos
        ]
        if colunas_divisiveis:
            pontuacao.loc[:, colunas_divisiveis] = (
                pontuacao.loc[:, colunas_divisiveis] / divisor)

    criterios_custo = [
        criterio.id for criterio in projeto.criterios.filter(
            numerico=True,
            monotonico=2,
        )
    ]
    pontuacao_ajustada = pontuacao.copy()
    for criterio in criterios_custo:
        if criterio in pontuacao_ajustada.columns:
            pontuacao_ajustada[criterio] = pontuacao_ajustada[criterio] * -1

    parametros = queryset_para_dataframe(
        CriterioParametro.objects.filter(projeto=projeto),
        ("criterio", "p", "q", "v"),
    )
    parametros = parametros.set_index("criterio")[["p", "q", "v"]].T
    criterios_parametrizados = list(parametros.columns)
    pontuacao_ajustada = pontuacao_ajustada.reindex(
        columns=criterios_parametrizados)
    pesos_por_criterio = dict(zip(pesos["criterio"], pesos["peso"]))
    parametros.loc["w"] = [
        pesos_por_criterio.get(criterio_id, 0)
        for criterio_id in criterios_parametrizados
    ]

    electre_range = ElectreTri(
        pontuacao_ajustada,
        parametros,
        lamb=projeto.lamb,
        bn=projeto.qtde_classes,
        method="range",
        id_projeto=projeto.id,
    )
    classificacao_range_df = electre_range.renderizar()
    pessimista_range = electre_range.pessimista()
    otimista_range = electre_range.otimista()
    classificacao_range = classificacao_range_df.reset_index().to_dict(
        orient="records")
    classificacao_range = [{
        **registro,
        "alternative": str(registro["alternative"]),
        "class": str(registro["class"]),
    } for registro in classificacao_range]

    electre_quantile = ElectreTri(
        pontuacao_ajustada,
        parametros,
        lamb=projeto.lamb,
        bn=projeto.qtde_classes,
        method="quantile",
        id_projeto=projeto.id,
    )
    classificacao_quantile_df = electre_quantile.renderizar()
    pessimista_quantile = electre_quantile.pessimista()
    otimista_quantile = electre_quantile.otimista()
    classificacao_quantile = classificacao_quantile_df.reset_index().to_dict(
        orient="records")
    classificacao_quantile = [{
        **registro,
        "alternative": str(registro["alternative"]),
        "class": str(registro["class"]),
    } for registro in classificacao_quantile]

    nomes_alternativas = {
        str(alternativa.id): alternativa.nome
        for alternativa in projeto.alternativas.all()
    }

    def formatar_classificacao(pessimista, otimista):
        return [{
            "alternative_id": int(alternativa_id),
            "alternative": nomes_alternativas.get(str(alternativa_id),
                                                  str(alternativa_id)),
            "pessimista": str(classe_pessimista),
            "otimista": str(otimista.loc[alternativa_id]),
            "class": str(classe_pessimista),
        } for alternativa_id, classe_pessimista in pessimista.items()]

    criterios = {
        criterio.id: criterio.nome
        for criterio in projeto.criterios.all()
    }
    pesos_ordenados = pesos.sort_values(by="peso",
                                        ascending=False).reset_index(drop=True)
    pesos_serializados = [{
        **registro,
        "criterio_nome": criterios.get(registro["criterio"],
                                       str(registro["criterio"])),
    } for registro in pesos_ordenados.to_dict(orient="records")]

    resultado = {
        "project": projeto,
        "pesos_criterios": pesos_serializados,
        "pontuacao_alternativas": pontuacao.reset_index().to_dict(
            orient="records"),
        "classificacao_range": classificacao_range,
        "classificacao_quantile": classificacao_quantile,
        "classificacao_final": {
            "range": formatar_classificacao(pessimista_range, otimista_range),
            "quantile": formatar_classificacao(pessimista_quantile,
                                               otimista_quantile),
        },
    }
    if decisores_ativos:
        resultado["decisores_ativos"] = len(decisores_ativos)
    return resultado


def obter_resultado_agregado(projeto: Projeto) -> dict[str, Any]:
    decisores_ativos = _decisores_ativos(projeto)
    if not decisores_ativos:
        raise ResultadoIndisponivel("Projeto sem decisores ativos.",
                                    pendencias=obter_pendencias_resultado(projeto))

    pendencias = obter_pendencias_resultado(projeto)
    if pendencias:
        raise ResultadoIndisponivel("Projeto com pendencias.",
                                    pendencias=pendencias)

    matriz = MatrizProjeto(projeto)
    matriz, divisor = _aplicar_escopo_projeto(matriz, projeto, decisores_ativos)
    return _montar_resultado(projeto, matriz, decisores_ativos, divisor)


@transaction.atomic
def gerar_resultado_manual(projeto: Projeto) -> dict[str, Any]:
    if resultado_gerado(projeto):
        return obter_resultado_gerado(projeto)

    resultado = obter_resultado_agregado(projeto)
    cache.set(_cache_key(projeto), resultado, timeout=None)
    projeto.resultado_gerado_em = timezone.now()
    projeto.save(update_fields=["resultado_gerado_em"])
    decisores_ativos = _decisores_ativos(projeto)
    if decisores_ativos:
        projeto.decisores.filter(id__in=[d.id for d in decisores_ativos]).update(
            status=Decisor.Status.CONCLUIDO,
            concluido_em=timezone.now(),
        )
    return resultado


def obter_resultado_gerado_ou_erro(projeto: Projeto) -> dict[str, Any]:
    if not resultado_gerado(projeto):
        raise ResultadoIndisponivel(
            "Resultado ainda nao gerado manualmente.",
            pendencias=obter_pendencias_resultado(projeto),
        )
    return obter_resultado_gerado(projeto)


def _validar_dados_legacy(projeto: Projeto):
    if not projeto.decisores.exists() or not projeto.criterios.exists() or not projeto.alternativas.exists():
        raise ResultadoIndisponivel("Projeto sem participantes cadastrados.")
    if projeto.criterioparametro.count() != projeto.criterios.count():
        raise ResultadoIndisponivel("Parametros incompletos.")
    if projeto.alternativacriterios.count() == 0:
        raise ResultadoIndisponivel("Notas numericas ausentes.")
    if projeto.avaliacaocriterios.count() == 0:
        raise ResultadoIndisponivel("Comparacoes de criterios ausentes.")


def obter_resultado(projeto: Projeto):
    _validar_dados_legacy(projeto)

    matriz = MatrizProjeto(projeto)
    pesos = matriz.pesos_criterios.reset_index(drop=True)
    if "criterio" not in pesos.columns:
        coluna_criterio = next(coluna for coluna in pesos.columns
                               if coluna != "peso")
        pesos = pesos.rename(columns={coluna_criterio: "criterio"})
    pontuacao = matriz.pontuacao_alternativas
    if pontuacao is None or pontuacao.empty:
        raise ResultadoIndisponivel("Pontuacao das alternativas indisponivel.")

    criterios_custo = [
        criterio.id for criterio in projeto.criterios.filter(
            numerico=True,
            monotonico=2,
        )
    ]
    pontuacao_ajustada = pontuacao.copy()
    for criterio in criterios_custo:
        if criterio in pontuacao_ajustada.columns:
            pontuacao_ajustada[criterio] = pontuacao_ajustada[criterio] * -1

    parametros = queryset_para_dataframe(
        CriterioParametro.objects.filter(projeto=projeto),
        ("criterio", "p", "q", "v"),
    )
    parametros = parametros.set_index("criterio")[["p", "q", "v"]].T
    criterios_parametrizados = list(parametros.columns)
    pontuacao_ajustada = pontuacao_ajustada.reindex(
        columns=criterios_parametrizados)
    pesos_por_criterio = dict(zip(pesos["criterio"], pesos["peso"]))
    parametros.loc["w"] = [
        pesos_por_criterio.get(criterio_id, 0)
        for criterio_id in criterios_parametrizados
    ]

    electre_range = ElectreTri(
        pontuacao_ajustada,
        parametros,
        lamb=projeto.lamb,
        bn=projeto.qtde_classes,
        method="range",
        id_projeto=projeto.id,
    )
    classificacao_range_df = electre_range.renderizar()
    pessimista_range = electre_range.pessimista()
    otimista_range = electre_range.otimista()
    classificacao_range = classificacao_range_df.reset_index().to_dict(
        orient="records")
    classificacao_range = [{
        **registro,
        "alternative": str(registro["alternative"]),
        "class": str(registro["class"]),
    } for registro in classificacao_range]

    electre_quantile = ElectreTri(
        pontuacao_ajustada,
        parametros,
        lamb=projeto.lamb,
        bn=projeto.qtde_classes,
        method="quantile",
        id_projeto=projeto.id,
    )
    classificacao_quantile_df = electre_quantile.renderizar()
    pessimista_quantile = electre_quantile.pessimista()
    otimista_quantile = electre_quantile.otimista()
    classificacao_quantile = classificacao_quantile_df.reset_index().to_dict(
        orient="records")
    classificacao_quantile = [{
        **registro,
        "alternative": str(registro["alternative"]),
        "class": str(registro["class"]),
    } for registro in classificacao_quantile]

    nomes_alternativas = {
        str(alternativa.id): alternativa.nome
        for alternativa in projeto.alternativas.all()
    }

    def formatar_classificacao(pessimista, otimista):
        return [{
            "alternative_id": int(alternativa_id),
            "alternative": nomes_alternativas.get(str(alternativa_id),
                                                  str(alternativa_id)),
            "pessimista": str(classe_pessimista),
            "otimista": str(otimista.loc[alternativa_id]),
            "class": str(classe_pessimista),
        } for alternativa_id, classe_pessimista in pessimista.items()]

    criterios = {
        criterio.id: criterio.nome
        for criterio in projeto.criterios.all()
    }
    pesos_ordenados = pesos.sort_values(by="peso",
                                        ascending=False).reset_index(drop=True)
    pesos_serializados = [{
        **registro,
        "criterio_nome": criterios.get(registro["criterio"],
                                       str(registro["criterio"])),
    } for registro in pesos_ordenados.to_dict(orient="records")]

    return {
        "project": projeto,
        "pesos_criterios": pesos_serializados,
        "pontuacao_alternativas": pontuacao.reset_index().to_dict(
            orient="records"),
        "classificacao_range": classificacao_range,
        "classificacao_quantile": classificacao_quantile,
        "classificacao_final": {
            "range": formatar_classificacao(pessimista_range, otimista_range),
            "quantile": formatar_classificacao(pessimista_quantile,
                                               otimista_quantile),
        },
    }
