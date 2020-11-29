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


def condorcet(df: pd.DataFrame, projeto_id, saida):
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

    matriz_decisao = matriz_somatorio.applymap(transformacao)
    matriz_final = matriz_decisao.copy()

    matriz_decisao['soma'] = matriz_decisao.replace(-1, 0).apply(np.sum,
                                                                 axis=1)
    matriz_decisao = matriz_decisao.sort_values(by='soma', ascending=False)
    matriz_decisao['Classificação'] = matriz_decisao['soma'].rank(
        method='dense', ascending=False)
    matriz_decisao['Classificação'] = matriz_decisao['Classificação'].astype(int)
    matriz_decisao.to_excel(saida, sheet_name='condorcet')

    matriz_final['soma'] = matriz_final.apply(np.sum, axis=1)
    matriz_final = matriz_final.sort_values(by='soma', ascending=False)
    matriz_final['Classificação'] = matriz_final.soma.rank(method='dense',
                                                           ascending=False)
    matriz_final['Classificação'] = matriz_final['Classificação'].astype(int)
    matriz_final.to_excel(saida, sheet_name='copeland')

    return dict(condorcet=matriz_decisao, copeland=matriz_final)
