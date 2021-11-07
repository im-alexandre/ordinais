import warnings
from collections import defaultdict

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from core.models import (Alternativa, AlternativaCriterio,
                         AvaliacaoAlternativas, AvaliacaoCriterios, Criterio,
                         Decisor, Projeto)

warnings.filterwarnings('ignore')

pd.options.display.float_format = '{:,.4f}'.format


class MatrizProjeto:
    def __init__(self, projeto: Projeto):
        self.projeto = projeto
        self.decisores = projeto.decisores.all()
        self.criterios = projeto.criterios.all()
        self.alternativas = projeto.alternativas.all()
        self.avaliacoes_criterios = projeto.avaliacaocriterios.all()
        self.avaliacoes_alternativas = projeto.avaliacaoalternativas.all()
        self.alternativas_criterios = projeto.alternativacriterios.all()

    @property
    def avaliacoes(self):

        if self.projeto.avaliacaoalternativas.all():
            df_alternativas = self.avaliacoes_alternativas.to_pivot_table(
                values='nota',
                rows=['decisor', 'criterio', 'alternativaB'],
                cols=[
                    'alternativaA',
                ])
            df_alternativas.fillna(0, inplace=True)
            df_alternativas = pd.concat([
                self._matriz_decisao(x)
                for _, x in df_alternativas.groupby(level=[0, 1])
            ])
            df_alternativas.columns.rename(None, inplace=True)
            df_alternativas.index.rename(
                ['Decisor', 'Critério', 'Alternativa'], inplace=True)
        else:
            df_alternativas = None

        df_criterios = self.avaliacoes_criterios.to_pivot_table(
            values='nota', rows='decisor criterioA'.split(), cols='criterioB')
        df_criterios.fillna(0, inplace=True)
        lista_criterios = list()
        for _, x in df_criterios.groupby(level=[0]):
            df = self._matriz_decisao(x)
            try:
                minimum = min(
                    df.loc[:,
                           'Normalized Vector'][df['Normalized Vector'] > 0])
                vector_not_null = df['Normalized Vector'].replace(
                    0, minimum / 100)

                df.loc[:, 'Not Null Normalized Vector'] = vector_not_null
            except ValueError:
                df.loc[:,
                       'Not Null Normalized Vector'] = df['Normalized Vector']
            lista_criterios.append(df)
        df_criterios = pd.concat(lista_criterios)

        df_criterios.columns.rename(None, inplace=True)

        df_criterios.index.rename(['Decisor', 'Critério'], inplace=True)

        return dict(alternativas=df_alternativas, criterios=df_criterios)

    def _matriz_decisao(self, dataframe):
        sum_vector = dataframe.apply(np.sum, axis=1)
        dataframe.loc[:, 'Sum Vector'] = sum_vector
        scaler = MinMaxScaler()
        normalized_vector = scaler.fit_transform(
            dataframe.loc[:, 'Sum Vector'].values.reshape(-1, 1))
        dataframe.loc[:, 'Normalized Vector'] = normalized_vector.round(4)
        return dataframe

    @property
    def pesos_criterios(self):
        pesos = self.avaliacoes['criterios']['Not Null Normalized Vector']\
            .groupby(level=1)\
            .sum()\
            .to_frame('peso')\
            .reset_index()\
            .rename(
                columns={'criterioA': 'criterio'}
        )
        # pesos.index.rename('Critério', inplace=True)
        return pesos

    @property
    def pontuacao_alternativas(self):
        # pontuacao = self.avaliacoes['alternativas']['Normalized Vector']\
        # .groupby(level=2)\
        # .sum()\
        # .to_frame('pontuacao')\
        # .reset_index()\
        # .rename(
        # columns={'alternativaB': 'alternativa'}
        # )
        try:
            pontuacao = self.avaliacoes['alternativas']
            pontuacao = pontuacao.unstack(level=1)
            pontuacao = pontuacao.groupby(level=1).sum()
            # pontuacao.drop(columns=['Sum Vector', 'Normalized Vector'],
            # inplace=True)
            pontuacao = pontuacao['Normalized Vector']
            pontuacao.index.rename('Alternativa', inplace=True)
            pontuacao.columns.rename('Critério', inplace=True)
        except:
            pass

        try:
            df_alt_crit = self.alternativas_criterios.to_pivot_table(
                values='nota', rows='alternativa', cols='criterio')
            pontuacao = pd.concat([
                pontuacao,
                df_alt_crit,
            ], axis=1)
        except:
            pass

        return pontuacao
