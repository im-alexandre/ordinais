from django.db import transaction

from core.models import (AlternativaCriterio, AvaliacaoAlternativas,
                         AvaliacaoCriterios, CriterioParametro, Projeto)


@transaction.atomic
def substituir_notas_numericas(projeto: Projeto, dados):
    scores = dados["scores"]
    decisores = {score["decisor"] for score in scores}
    for decisor in decisores:
        AlternativaCriterio.objects.filter(
            projeto=projeto,
            decisor=decisor,
        ).delete()

    itens = [
        AlternativaCriterio.objects.create(
            projeto=projeto,
            decisor=score["decisor"],
            criterio=score["criterio"],
            alternativa=score["alternativa"],
            nota=score["nota"],
        ) for score in scores
    ]
    return itens


@transaction.atomic
def substituir_comparacoes_criterios(projeto: Projeto, dados):
    comparisons = dados["comparisons"]
    decisores = {comparison["decisor"] for comparison in comparisons}
    for decisor in decisores:
        AvaliacaoCriterios.objects.filter(
            projeto=projeto,
            decisor=decisor,
        ).delete()

    itens = []
    for comparison in comparisons:
        itens.append(
            AvaliacaoCriterios.objects.create(
                projeto=projeto,
                decisor=comparison["decisor"],
                criterioA=comparison["criterioA"],
                criterioB=comparison["criterioB"],
                nota=comparison["nota"],
            ))
        inverso = dict(comparison)
        inverso["criterioA"], inverso["criterioB"] = (
            inverso["criterioB"],
            inverso["criterioA"],
        )
        inverso["nota"] = -int(inverso["nota"])
        itens.append(
            AvaliacaoCriterios.objects.create(
                projeto=projeto,
                decisor=inverso["decisor"],
                criterioA=inverso["criterioA"],
                criterioB=inverso["criterioB"],
                nota=inverso["nota"],
            ))
    return itens


@transaction.atomic
def substituir_comparacoes_alternativas(projeto: Projeto, dados):
    comparisons = dados["comparisons"]
    decisores = {comparison["decisor"] for comparison in comparisons}
    for decisor in decisores:
        AvaliacaoAlternativas.objects.filter(
            projeto=projeto,
            decisor=decisor,
        ).delete()

    itens = []
    for comparison in comparisons:
        itens.append(
            AvaliacaoAlternativas.objects.create(
                projeto=projeto,
                decisor=comparison["decisor"],
                criterio=comparison["criterio"],
                alternativaA=comparison["alternativaA"],
                alternativaB=comparison["alternativaB"],
                nota=comparison["nota"],
            ))
        inverso = dict(comparison)
        inverso["alternativaA"], inverso["alternativaB"] = (
            inverso["alternativaB"],
            inverso["alternativaA"],
        )
        inverso["nota"] = -int(inverso["nota"])
        itens.append(
            AvaliacaoAlternativas.objects.create(
                projeto=projeto,
                decisor=inverso["decisor"],
                criterio=inverso["criterio"],
                alternativaA=inverso["alternativaA"],
                alternativaB=inverso["alternativaB"],
                nota=inverso["nota"],
            ))
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
