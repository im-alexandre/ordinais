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
    pesos = matriz.pesos_criterios.sort_values(by="peso",
                                               ascending=False).reset_index(
                                                   drop=True)
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
    parametros.loc["w"] = pesos["peso"].values

    electre_range = ElectreTri(pontuacao_ajustada,
                               parametros,
                               lamb=projeto.lamb,
                               bn=projeto.qtde_classes,
                               method="range",
                               id_projeto=projeto.id)
    classificacao_range = electre_range.renderizar().reset_index().to_dict(
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
    classificacao_quantile = electre_quantile.renderizar().reset_index().to_dict(
        orient="records")
    classificacao_quantile = [
        {
            **registro,
            "alternative": str(registro["alternative"]),
            "class": str(registro["class"]),
        } for registro in classificacao_quantile
    ]

    return {
        "project": projeto,
        "pesos_criterios": pesos.to_dict(orient="records"),
        "pontuacao_alternativas": pontuacao.reset_index().to_dict(orient="records"),
        "classificacao_range": classificacao_range,
        "classificacao_quantile": classificacao_quantile,
    }
