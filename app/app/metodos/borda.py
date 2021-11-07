import numpy as np
import pandas as pd


def borda(df: pd.DataFrame) -> pd.DataFrame:
    colunas = list()
    matriz_decisao = df.copy()

    for criterio in matriz_decisao.columns:
        matriz_decisao[criterio + '_ranking'] = matriz_decisao[criterio].rank(
            method='dense', ascending=False)
        colunas.append(criterio + '_ranking')

    matriz_decisao['Score'] = matriz_decisao[colunas].apply(np.sum, axis=1)
    matriz_decisao['Rank'] = matriz_decisao['Score'].rank(
        method='dense', ascending=True)

    matriz_decisao = matriz_decisao.sort_values(by='Score')
    matriz_decisao.index.rename(None, inplace=True)
    matriz_decisao.columns.rename(None, inplace=True)
    matriz_decisao['Score'] = matriz_decisao['Score'].astype(int)
    matriz_decisao['Rank'] = matriz_decisao['Rank'].astype(
        int)
    return matriz_decisao
