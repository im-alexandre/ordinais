import os
from itertools import combinations, product

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import pyperclip

print('')

df = pd.read_csv('./condorcet_likert.csv', index_col='alternativas')
# pyperclip.copy(df.to_latex())
print('')
print('*** Dados de entrada ***\n')
print(df)
print('\n', 50 * '*', 'Tabela no formato LaTeX\n')
print(df.to_latex())

alternativas = list(df.index)
criterios = list(df.columns)
# print(alternativas)

alternativas_combinadas = list(combinations(alternativas, 2))
print('')
print(list(alternativas_combinadas))

dataframes = {
    criterio: pd.DataFrame(data=0, index=alternativas, columns=alternativas)
    for criterio in criterios
}
for criterio, (alternativaA, alternativaB) in product(criterios,
                                                      alternativas_combinadas):
    if df.at[alternativaA, criterio] > df.at[alternativaB, criterio]:
        dataframes[criterio].at[alternativaA, alternativaB] = +1

    elif df.at[alternativaA, criterio] < df.at[alternativaB, criterio]:
        dataframes[criterio].at[alternativaA, alternativaB] = -1

    else:
        dataframes[criterio].at[alternativaA, alternativaB] = 0
    os.system('clear')
    print(criterio, dataframes[criterio], sep='\n')

print('')

matriz_somatorio = pd.DataFrame(sum([i.values for i in dataframes.values()]),
                                index=alternativas,
                                columns=alternativas)
os.system('clear')
print(matriz_somatorio)
pyperclip.copy(matriz_somatorio.to_latex())
print('\n\n')
print(matriz_somatorio.to_latex())


def transformacao(valor):
    if valor >= 1:
        return 1
    elif valor <= -1:
        return -1
    else:
        return 0


matriz_decisao = matriz_somatorio.applymap(transformacao)

transposta = matriz_decisao.T
transposta = transposta.values * -1
valores_decisao = matriz_decisao.values + transposta

matriz_final = pd.DataFrame(valores_decisao,
                            index=alternativas,
                            columns=alternativas)
os.system('clear')
print('\n\n *** MATRIZ DE DECISÃO *** \n')
print(matriz_decisao)

G = nx.DiGraph()
G.add_nodes_from(alternativas)

for i, j in list(product(alternativas, alternativas)):
    if matriz_final.at[i, j] == 1:
        G.add_weighted_edges_from([
            (i, j, 1),
        ])

nx.draw(G, node_size=6000, with_labels=True, node_shape='s')
plt.show()
os.system('clear')
print(matriz_decisao)
