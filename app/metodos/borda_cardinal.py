import os

import numpy as np
import pandas as pd


def borda(df: pd.DataFrame):
    colunas = list()
    for criterio in df.columns:
        ordenado = df[criterio].sort_values(ascending=False)
        ordenado = ordenado.reset_index()
        ordenado[criterio + '_ordem'] = ordenado.index
        ordenado.set_index('alternativa', inplace=True)
        os.system('clear')
        colunas.append(ordenado[criterio + '_ordem'])

    matriz_decisao = pd.concat(colunas, axis=1).applymap(lambda x: x + 1)
    matriz_decisao.columns = df.columns
    matriz_decisao['soma'] = matriz_decisao.apply(np.sum, axis=1)
    matriz_decisao = matriz_decisao.sort_values(by='soma')
    return matriz_decisao
