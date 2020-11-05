import os
from itertools import combinations, product

# import matplotlib.pyplot as plt
# import networkx as nx
import numpy as np
import pandas as pd


def transformacao(valor):
    if valor >= 1:
        return 1
    elif valor <= -1:
        return -1
    else:
        return 0


def condorcet(df: pd.DataFrame):
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

        elif df.at[alternativaA, criterio] < df.at[alternativaB, criterio]:
            dataframes[criterio].at[alternativaA, alternativaB] = -1

        else:
            dataframes[criterio].at[alternativaA, alternativaB] = 0

    matriz_somatorio = pd.DataFrame(sum(
        [i.values for i in dataframes.values()]),
        index=alternativas,
        columns=alternativas)

    matriz_decisao = matriz_somatorio.applymap(transformacao)

    transposta = matriz_decisao.T
    transposta = transposta.values * -1
    valores_decisao = matriz_decisao.values + transposta

    matriz_final = pd.DataFrame(valores_decisao,
                                index=alternativas,
                                columns=alternativas)
    matriz_decisao['soma'] = matriz_decisao.apply(np.sum, axis=1)
    matriz_final['soma'] = matriz_final.apply(np.sum, axis=1)
    matriz_decisao = matriz_decisao.sort_values(by='soma', ascending=False)
    matriz_final = matriz_final.sort_values(by='soma', ascending=False)
    return dict(condorcet=matriz_decisao, copeland=matriz_final)
