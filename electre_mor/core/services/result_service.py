from dataclasses import dataclass

import pandas as pd

from core.ElectreTri import ElectreTri
from core.method import MatrizProjeto
from core.models import CriterioParametro, Projeto
from core.tabular import queryset_para_dataframe


@dataclass
class ResultadoIndisponivel(Exception):
    motivo: str


def _validar_dados(projeto: Projeto):
    if not projeto.decisores.exists() or not projeto.criterios.exists() or not projeto.alternativas.exists():
        raise ResultadoIndisponivel("Projeto sem participantes cadastrados.")
    if projeto.criterioparametro.count() != projeto.criterios.count():
        raise ResultadoIndisponivel("Parametros incompletos.")
    if projeto.alternativacriterios.count() == 0:
        raise ResultadoIndisponivel("Notas numericas ausentes.")
    if projeto.avaliacaocriterios.count() == 0:
        raise ResultadoIndisponivel("Comparacoes de criterios ausentes.")


def obter_resultado(projeto: Projeto):
    _validar_dados(projeto)

    matriz = MatrizProjeto(projeto)
    pesos = matriz.pesos_criterios.reset_index(drop=True)
    if "criterio" not in pesos.columns:
        coluna_criterio = next(coluna for coluna in pesos.columns if coluna != "peso")
        pesos = pesos.rename(columns={coluna_criterio: "criterio"})
    pontuacao = matriz.pontuacao_alternativas
    if pontuacao is None or pontuacao.empty:
        raise ResultadoIndisponivel("Pontuacao das alternativas indisponivel.")

    criterios_custo = [
        criterio.id for criterio in projeto.criterios.filter(numerico=True,
                                                             monotonico=2)
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

    electre_range = ElectreTri(pontuacao_ajustada,
                               parametros,
                               lamb=projeto.lamb,
                               bn=projeto.qtde_classes,
                               method="range",
                               id_projeto=projeto.id)
    classificacao_range_df = electre_range.renderizar()
    pessimista_range = electre_range.pessimista()
    otimista_range = electre_range.otimista()
    classificacao_range = classificacao_range_df.reset_index().to_dict(
        orient="records")
    classificacao_range = [
        {
            **registro,
            "alternative": str(registro["alternative"]),
            "class": str(registro["class"]),
        } for registro in classificacao_range
    ]

    electre_quantile = ElectreTri(pontuacao_ajustada,
                                  parametros,
                                  lamb=projeto.lamb,
                                  bn=projeto.qtde_classes,
                                  method="quantile",
                                  id_projeto=projeto.id)
    classificacao_quantile_df = electre_quantile.renderizar()
    pessimista_quantile = electre_quantile.pessimista()
    otimista_quantile = electre_quantile.otimista()
    classificacao_quantile = classificacao_quantile_df.reset_index().to_dict(
        orient="records")
    classificacao_quantile = [
        {
            **registro,
            "alternative": str(registro["alternative"]),
            "class": str(registro["class"]),
        } for registro in classificacao_quantile
    ]

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
        "pontuacao_alternativas": pontuacao.reset_index().to_dict(orient="records"),
        "classificacao_range": classificacao_range,
        "classificacao_quantile": classificacao_quantile,
        "classificacao_final": {
            "range": formatar_classificacao(pessimista_range, otimista_range),
            "quantile": formatar_classificacao(pessimista_quantile,
                                               otimista_quantile),
        },
    }
