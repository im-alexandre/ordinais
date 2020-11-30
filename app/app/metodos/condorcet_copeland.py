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

    matriz_somatorio = pd.DataFrame(sum(
        [i.values for i in dataframes.values()]),
                                    index=alternativas,
                                    columns=alternativas)

    matriz_condorcet = matriz_somatorio.applymap(transformacao)
    matriz_copeland = matriz_condorcet.copy()

    matriz_condorcet['soma'] = matriz_condorcet.replace(-1, 0).apply(np.sum,
                                                                     axis=1)
    matriz_condorcet = matriz_condorcet.sort_values(by='soma', ascending=False)
    matriz_condorcet['Classificação'] = matriz_condorcet['soma'].rank(
        method='dense', ascending=False)
    empatados = matriz_condorcet[matriz_condorcet['Classificação'].duplicated(
        keep=False)]
    inicio_ciclo = empatados['Classificação'].min()
    matriz_condorcet['Classificação'] = matriz_condorcet[
        'Classificação'].apply(lambda x: indica_ciclo(x, inicio_ciclo))
    matriz_condorcet.to_excel(saida, sheet_name='condorcet')

    matriz_copeland['soma'] = matriz_copeland.apply(np.sum, axis=1)
    matriz_copeland = matriz_copeland.sort_values(by='soma', ascending=False)
    matriz_copeland['Classificação'] = matriz_copeland.soma.rank(
        method='dense', ascending=False)
    matriz_copeland['Classificação'] = matriz_copeland['Classificação'].astype(
        int)
    matriz_copeland.to_excel(saida, sheet_name='copeland')

    return dict(condorcet=matriz_condorcet, copeland=matriz_copeland)
