#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: Electrepy.py
Author: Alexandre Castro
Email: im.alexandre07@gmail.com
Github: https://www.github.com/im-alexandre
Description: Implementação do electre_tri em python
"""
import warnings
from itertools import product

import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')


class ElectreTri():
    """ Calcula as matrizes de concordância, discordância e credibilidade,
    self.dados as alternativas e os parametros"""

    def __init__(
        self,
        entrada,
        parametros,
        lamb,
        bn,
        id_projeto,
        method='quantil',
    ):
        self.entrada = entrada
        self.parametros = parametros
        self.lamb = lamb
        self.bn = bn
        self.method = method
        self.id_projeto = id_projeto

    def _escalona(self, coluna):
        try:
            escala = (max(coluna) - min(coluna)) / (self.bn)
            coluna_escalonada = np.arange(min(coluna), max(coluna), escala)[1:]
        except ZeroDivisionError:
            coluna_escalonada = [max(coluna)]
        return coluna_escalonada

    def comparacao(self, row):
        """docstring for pessimista"""
        if row['cred(b,x)'] >= self.lamb and row['cred(x,b)'] >= self.lamb:
            return 'x I b'
        elif row['cred(b,x)'] >= self.lamb and row['cred(x,b)'] < self.lamb:
            return 'x < b'
        elif row['cred(b,x)'] < self.lamb and row['cred(x,b)'] >= self.lamb:
            return 'x > b'
        else:
            return 'x R b'

    def credibilidade(self, row: pd.Series) -> float:
        """
        Calcula a matriz de credibilidade, dada uma matriz de concordância ou
        discordância
        """
        concordancia = row.values[-1]
        discordancias = row.values[:-1]
        discordancias = discordancias[discordancias > concordancia]
        if len(discordancias) > 0:
            lista = (1 - discordancias) / (1 - concordancia)
            credibilidade = concordancia * (lista.cumprod())
            return credibilidade[-1]
        else:
            credibilidade = concordancia
            return credibilidade

    def discordancia(self, serie: pd.Series, xi: str, bh: str) -> float:
        """
        Calcula a dicordância entre a classe e a alternativa (ou vice-versa),
        dada uma série com os atributos da alternativa, os critérios e as
        fronteiras de classe em cada critério
        """
        diferenca = serie[bh] - serie[xi]
        if diferenca <= serie['p']:
            return 0
        elif diferenca > serie['v']:
            return 1
        else:
            resposta = (-serie['p'] + diferenca) / (serie['v'] - serie['p'])
            return resposta

    def concordancia_parcial(self, serie, xi, bh):
        diferenca = serie[bh] - serie[xi]
        if diferenca >= serie['p']:
            return 0
        elif diferenca <= serie['q']:
            return 1
        else:
            resposta = (serie['p'] - diferenca) / (serie['p'] - serie['q'])
            return resposta

    def concordancia_global(self, serie):
        W = self.parametros.loc['w', :]
        resposta = sum(serie.values * W.values) / sum(W.values)
        return resposta

    def __pessimista(self, credibilidade: pd.DataFrame):
        """Classificação pessimista das alternativas"""
        cla = credibilidade.reset_index()
        qtde_classes = cla.shape[0] + 1
        cla = cla[cla['comparacao'].isin(['x I b', 'x > b'])]
        try:
            index = len(list(cla.index.values))
        except IndexError:
            index = 1
        numero_da_classe = 'Classe ' + str(qtde_classes - (index))
        return numero_da_classe

    def pessimista(self):
        """docstring for pessimista"""
        df = self.credibilidade_df.groupby(level='alternativa').apply(
            self.__pessimista)
        return df

    def __otimista(self, credibilidade: pd.DataFrame):
        """Classificação otimista das alternativas"""
        cla = credibilidade.reset_index()
        qtde_classes = cla.shape[0] + 1
        cla = cla[cla['comparacao'].isin(['x I b', 'x R b', 'x > b'])]
        try:
            index = len(list(cla.index.values))
        except IndexError:
            index = 1
        numero_da_classe = 'Classe ' + str(qtde_classes - (index))
        return numero_da_classe

    def otimista(self):
        """docstring for otimista"""
        df = self.credibilidade_df.groupby(level='alternativa').apply(
            self.__otimista)
        return df

    def renderizar(self, ):
        """docstring for renderizar"""
        alternativas = list(self.entrada.index)

        if self.method == 'quantil':
            self.cla_df = pd.DataFrame(
                self.entrada.quantile(q=np.arange(0, 1, 1 / self.bn),
                                      interpolation='higher').values[1:],
                columns=self.entrada.columns)
            self.cla = [f'b{i}' for i in range(1, self.cla_df.shape[0] + 1)]
            self.cla_df.index = self.cla

        elif self.method == 'range':
            self.cla_df = self.entrada.apply(self._escalona)
            self.cla = [f'b{i}' for i in range(1, self.cla_df.shape[0] + 1)]
            self.cla_df.index = self.cla

        self.dados = pd.concat(
            [self.entrada, self.cla_df, self.parametros],
            axis=0,
        )
        self.index = pd.MultiIndex.from_product(
            [alternativas, self.cla], names=['alternativa', 'classe'])
        self.df = pd.DataFrame(None,
                               index=self.index,
                               columns=self.entrada.columns)

        self.df_concordancia_x_b = self.df.copy()
        self.df_concordancia_b_x = self.df.copy()
        self.df_discordancia_x_b = self.df.copy()
        self.df_discordancia_b_x = self.df.copy()

        for a, c in self.df.index:
            self.df.at[(a, c)] = self.dados.loc[c] - self.dados.loc[a]

        for (x, b), g in product(self.df_concordancia_b_x.index,
                                 self.df_concordancia_b_x.columns):
            self.df_concordancia_x_b.at[(x, b), g] = self.concordancia_parcial(
                self.dados[g], xi=x, bh=b)
            self.df_concordancia_b_x.at[(x, b), g] = self.concordancia_parcial(
                self.dados[g], xi=b, bh=x)

        for (x, b), g in product(self.df_discordancia_x_b.index,
                                 self.df_discordancia_x_b.columns):
            self.df_discordancia_x_b.at[(x, b),
                                        g] = self.discordancia(self.dados[g],
                                                               xi=x,
                                                               bh=b)

        for (x, b), g in product(self.df_discordancia_b_x.index,
                                 self.df_discordancia_b_x.columns):
            self.df_discordancia_b_x.at[(x, b),
                                        g] = self.discordancia(self.dados[g],
                                                               xi=b,
                                                               bh=x)

        self.df_concordancia_x_b['c(x,b)'] = self.df_concordancia_x_b.apply(
            self.concordancia_global, axis=1)
        self.df_concordancia_b_x['c(b,x)'] = self.df_concordancia_b_x.apply(
            self.concordancia_global, axis=1)

        self.df_credibilidade_b_x = pd.concat(
            [self.df_discordancia_b_x, self.df_concordancia_b_x['c(b,x)']],
            axis=1)
        self.df_credibilidade_b_x[
            'cred(b,x)'] = self.df_credibilidade_b_x.apply(self.credibilidade,
                                                           axis=1)

        self.df_credibilidade_x_b = pd.concat(
            [self.df_discordancia_x_b, self.df_concordancia_x_b['c(x,b)']],
            axis=1)
        self.df_credibilidade_x_b[
            'cred(x,b)'] = self.df_credibilidade_x_b.apply(self.credibilidade,
                                                           axis=1)

        self.credibilidade_df = pd.concat([
            self.df_credibilidade_x_b['cred(x,b)'],
            self.df_credibilidade_b_x['cred(b,x)']
        ],
            axis=1)

        self.credibilidade_df['comparacao'] = self.credibilidade_df.apply(
            self.comparacao, axis=1)

        self.credibilidade_df['lambda'] = self.lamb

        if self.method == 'quantile':
            self.nome_tabela = 'bh'
        elif self.method == 'range':
            self.nome_tabela = 'bn'

        tab = pd.ExcelWriter(
            f'resultados/resultado_{self.nome_tabela}{self.id_projeto}.xlsx')
        self.cla_df.to_excel(tab, 'bhs')
        self.parametros.to_excel(tab, 'parametros')
        self.df_concordancia_x_b.to_excel(tab, 'concordancia_x_b')
        self.df_concordancia_b_x.to_excel(tab, 'concordancia_b_x')
        self.df_discordancia_b_x.to_excel(tab, 'discordancia_b_x')
        self.df_discordancia_x_b.to_excel(tab, 'discordancia_x_b')
        self.df_credibilidade_b_x.to_excel(tab, 'credibilidade_b_x')
        self.df_credibilidade_x_b.to_excel(tab, 'credibilidade_x_b')
        self.credibilidade_df.to_excel(tab, 'classificações')
        tab.save()

        return self.credibilidade_df


if __name__ == '__main__':
    entrada = pd.read_excel('electre.xlsx', sheet_name='alternativas')
    parametros = pd.read_excel('electre.xlsx', sheet_name='parametros')
    ElectreTri(entrada, parametros, 0.75).renderizar()
