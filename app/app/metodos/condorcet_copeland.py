import os
from itertools import combinations, product

import numpy as np
import pandas as pd


def transformacao(valor):
    if valor >= 1:
        return 1
    elif valor <= -1:
        return -1
    else:
        return 0


def indica_ciclo(valor, inicio_ciclo):
    if valor >= inicio_ciclo:
        return '-'
    else:
        return valor


def condorcet_copeland(df: pd.DataFrame, projeto_id, saida) -> dict[str, pd.DataFrame]:
    """docstring for condorcet"""

    alternativas = list(df.index)
    criterios = list(df.columns)

    alternativas_combinadas = list(combinations(alternativas, 2))
    dataframes = {
        criterio: pd.DataFrame(data=0,
                               index=alternativas,
                               columns=alternativas)
        for criterio in criterios
    }
    for criterio, (alternativaA,
                   alternativaB) in product(criterios,
                                            alternativas_combinadas):
        if df.at[alternativaA, criterio] > df.at[alternativaB, criterio]:
            dataframes[criterio].at[alternativaA, alternativaB] = +1
            dataframes[criterio].at[alternativaB, alternativaA] = -1

        elif df.at[alternativaA, criterio] < df.at[alternativaB, criterio]:
            dataframes[criterio].at[alternativaA, alternativaB] = -1
            dataframes[criterio].at[alternativaB, alternativaA] = 1

        else:
            dataframes[criterio].at[alternativaA, alternativaB] = 0

        dataframes[criterio].to_excel(saida, sheet_name=criterio)

    matriz_Scoretorio = pd.DataFrame(sum(
        [i.values for i in dataframes.values()]),
                                    index=alternativas,
                                    columns=alternativas)

    matriz_condorcet = matriz_Scoretorio.applymap(transformacao)
    matriz_copeland = matriz_condorcet.copy()

    matriz_condorcet['Score'] = matriz_condorcet.replace(-1, 0).apply(np.sum,
                                                                     axis=1)
    matriz_condorcet = matriz_condorcet.sort_values(by='Score', ascending=False)
    matriz_condorcet['Rank'] = matriz_condorcet['Score'].rank(
        method='dense', ascending=False)
    empatados = matriz_condorcet[matriz_condorcet['Rank'].duplicated(
        keep=False)]
    inicio_ciclo = empatados['Rank'].min()
    matriz_condorcet['Rank'] = matriz_condorcet[
        'Rank'].apply(lambda x: indica_ciclo(x, inicio_ciclo))
    matriz_condorcet.to_excel(saida, sheet_name='condorcet')

    matriz_copeland['Score'] = matriz_copeland.apply(np.sum, axis=1)
    matriz_copeland = matriz_copeland.sort_values(by='Score', ascending=False)
    matriz_copeland['Rank'] = matriz_copeland.Score.rank(
        method='dense', ascending=False)
    matriz_copeland['Rank'] = matriz_copeland['Rank'].astype(
        int)
    matriz_copeland.to_excel(saida, sheet_name='copeland')

    return dict(condorcet=matriz_condorcet, copeland=matriz_copeland)
