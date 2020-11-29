import numpy as np
import pandas as pd


def borda(df: pd.DataFrame):
    colunas = list()
    matriz_decisao = df.copy()
    for criterio in matriz_decisao.columns:
        matriz_decisao[criterio + '_ordem'] = matriz_decisao[criterio].rank(
            method='dense', ascending=False)
        colunas.append(criterio + '_ordem')

    matriz_decisao['soma'] = matriz_decisao[colunas].apply(np.sum, axis=1)
    matriz_decisao['Classificação'] = matriz_decisao['soma'].rank(
        method='dense', ascending=True)
    matriz_decisao = matriz_decisao.sort_values(by='soma')
    matriz_decisao.index.rename(None, inplace=True)
    matriz_decisao.columns.rename(None, inplace=True)
    matriz_decisao['soma'] = matriz_decisao['soma'].astype(int)
    matriz_decisao['Classificação'] = matriz_decisao['Classificação'].astype(
        int)
    return matriz_decisao
