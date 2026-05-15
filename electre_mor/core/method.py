import warnings
from collections import defaultdict

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from core.models import (Alternativa, AlternativaCriterio,
                         AvaliacaoAlternativas, AvaliacaoCriterios, Criterio,
                         Decisor, Projeto)
from core.tabular import queryset_para_dataframe

warnings.filterwarnings('ignore')

pd.options.display.float_format = '{:,.4f}'.format


class MatrizProjeto:
    def __init__(self, projeto: Projeto):
        self.projeto = projeto
        self.decisores = projeto.decisores.filter(
            ativo=True).exclude(status=Decisor.Status.DESATIVADO)
        self.criterios = projeto.criterios.all()
        self.alternativas = projeto.alternativas.all()
        self.avaliacoes_criterios = projeto.avaliacaocriterios.filter(
            decisor__in=self.decisores)
        self.avaliacoes_alternativas = projeto.avaliacaoalternativas.filter(
            decisor__in=self.decisores)
        if projeto.alternativacriterios.filter(decisor__isnull=False).exists():
            self.alternativas_criterios = projeto.alternativacriterios.filter(
                decisor__in=self.decisores)
        else:
            self.alternativas_criterios = projeto.alternativacriterios.filter(
                decisor__isnull=True)

    @property
    def avaliacoes(self):

        if self.projeto.avaliacaoalternativas.all():
            df_alternativas = queryset_para_dataframe(
                self.avaliacoes_alternativas,
                ('decisor', 'criterio', 'alternativaB', 'alternativaA',
                 'nota'))
            df_alternativas = df_alternativas.pivot_table(
                values='nota',
                index=['decisor', 'criterio', 'alternativaB'],
                columns=['alternativaA'],
                aggfunc='first')
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

        df_criterios = queryset_para_dataframe(
            self.avaliacoes_criterios,
            ('decisor', 'criterioA', 'criterioB', 'nota'))
        df_criterios = df_criterios.pivot_table(
            values='nota',
            index=['decisor', 'criterioA'],
            columns=['criterioB'],
            aggfunc='first')
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
        pontuacao = None
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
            df_alt_crit = queryset_para_dataframe(
                self.alternativas_criterios,
                ('alternativa', 'criterio', 'nota'))
            df_alt_crit = df_alt_crit.groupby(
                ['alternativa', 'criterio'],
                as_index=False,
            )['nota'].mean()
            df_alt_crit = df_alt_crit.pivot(
                index='alternativa',
                columns='criterio',
                values='nota',
            )
            pontuacao = pd.concat([pontuacao, df_alt_crit], axis=1) if pontuacao is not None else df_alt_crit
        except:
            pass

        return pontuacao
