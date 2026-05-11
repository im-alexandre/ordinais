from django.db import transaction

from core.models import (AlternativaCriterio, AvaliacaoAlternativas,
                         AvaliacaoCriterios, CriterioParametro, Projeto)


@transaction.atomic
def substituir_notas_numericas(projeto: Projeto, dados):
    AlternativaCriterio.objects.filter(projeto=projeto).delete()
    itens = [
        AlternativaCriterio.objects.create(projeto=projeto, **score)
        for score in dados["scores"]
    ]
    return itens


@transaction.atomic
def substituir_comparacoes_criterios(projeto: Projeto, dados):
    AvaliacaoCriterios.objects.filter(projeto=projeto).delete()
    itens = []
    for comparison in dados["comparisons"]:
        itens.append(AvaliacaoCriterios.objects.create(projeto=projeto,
                                                       **comparison))
        inverso = dict(comparison)
        inverso["criterioA"], inverso["criterioB"] = (
            inverso["criterioB"],
            inverso["criterioA"],
        )
        inverso["nota"] = -int(inverso["nota"])
        itens.append(AvaliacaoCriterios.objects.create(projeto=projeto,
                                                       **inverso))
    return itens


@transaction.atomic
def substituir_comparacoes_alternativas(projeto: Projeto, dados):
    AvaliacaoAlternativas.objects.filter(projeto=projeto).delete()
    itens = []
    for comparison in dados["comparisons"]:
        itens.append(AvaliacaoAlternativas.objects.create(
            projeto=projeto, **comparison))
        inverso = dict(comparison)
        inverso["alternativaA"], inverso["alternativaB"] = (
            inverso["alternativaB"],
            inverso["alternativaA"],
        )
        inverso["nota"] = -int(inverso["nota"])
        itens.append(AvaliacaoAlternativas.objects.create(
            projeto=projeto, **inverso))
    return itens


@transaction.atomic
def substituir_parametros(projeto: Projeto, dados):
    CriterioParametro.objects.filter(projeto=projeto).delete()
    itens = [
        CriterioParametro.objects.create(projeto=projeto, **parameter)
        for parameter in dados["parameters"]
    ]
    return itens


def recalcular_alternativas(*args, **kwargs):
    """Mantido para compatibilidade sem acoplar a API ao detalhe do fluxo."""
    return None
