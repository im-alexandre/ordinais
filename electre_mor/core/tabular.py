"""Utilitarios tabulares para substituir o acoplamento com django-pandas."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

import pandas as pd


def queryset_para_registros(queryset: Any,
                            campos: Sequence[str] | None = None
                            ) -> list[dict[str, Any]]:
    """Converte um queryset em uma lista de registros ordenados por campos."""

    valores = queryset.values(*campos) if campos else queryset.values()
    return list(valores)


def queryset_para_dataframe(queryset: Any,
                            campos: Sequence[str] | None = None) -> pd.DataFrame:
    """Converte um queryset em DataFrame sem usar django-pandas."""

    return pd.DataFrame.from_records(queryset_para_registros(queryset, campos))


def registros_para_dataframe(registros: Iterable[dict[str, Any]]) -> pd.DataFrame:
    """Converte registros tabulares em DataFrame."""

    return pd.DataFrame.from_records(list(registros))


def pivotar_registros(registros: Iterable[dict[str, Any]],
                      indice: Sequence[str] | str,
                      colunas: Sequence[str] | str,
                      valores: Sequence[str] | str,
                      preenchimento: Any | None = None,
                      agregacao: str = "first") -> pd.DataFrame:
    """Executa pivot em registros tabulares usando pandas diretamente."""

    dataframe = registros_para_dataframe(registros)
    if dataframe.empty:
        return dataframe
    return dataframe.pivot_table(index=indice,
                                 columns=colunas,
                                 values=valores,
                                 fill_value=preenchimento,
                                 aggfunc=agregacao)
