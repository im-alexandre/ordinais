import numpy as np
import pandas as pd

df = pd.read_csv('borda_ordinal.csv', index_col='alternativas')
print('*** Dados de entrada ***\n')
print(df)

df['soma'] = df.apply(np.sum, axis=1)
df = df.sort_values(by='soma')

print('*** matriz de decisão ***\n')
print(df, '\n')
print(f'A melhor alternativa é {df.index[0]}')
df.to_latex('~/Cursos/latex/teste.tex', index=False)
