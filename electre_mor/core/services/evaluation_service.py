from django.db import transaction

from core.models import (AlternativaCriterio, AvaliacaoAlternativas,
                         AvaliacaoCriterios, CriterioParametro, Projeto)
from core.services.result_service import ResultadoIndisponivel, resultado_gerado


def _garantir_resultado_nao_gerado(projeto: Projeto):
    if resultado_gerado(projeto):
        raise ResultadoIndisponivel("Resultado ja gerado manualmente.",
                                    pendencias=[])


def _marcar_decisor_em_edicao(decisor):
    if not decisor.ativo or decisor.status == decisor.Status.DESATIVADO:
        return
    decisor.status = decisor.Status.EM_EDICAO
    decisor.concluido_em = None
    decisor.save(update_fields=["status", "concluido_em"])


@transaction.atomic
def substituir_notas_numericas(projeto: Projeto, dados):
    _garantir_resultado_nao_gerado(projeto)
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
    for decisor in decisores:
        _marcar_decisor_em_edicao(decisor)
    return itens


@transaction.atomic
def substituir_comparacoes_criterios(projeto: Projeto, dados):
    _garantir_resultado_nao_gerado(projeto)
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
    for decisor in decisores:
        _marcar_decisor_em_edicao(decisor)
    return itens


@transaction.atomic
def substituir_comparacoes_alternativas(projeto: Projeto, dados):
    _garantir_resultado_nao_gerado(projeto)
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
    for decisor in decisores:
        _marcar_decisor_em_edicao(decisor)
    return itens


@transaction.atomic
def substituir_parametros(projeto: Projeto, dados):
    _garantir_resultado_nao_gerado(projeto)
    CriterioParametro.objects.filter(projeto=projeto).delete()
    itens = [
        CriterioParametro.objects.create(projeto=projeto, **parameter)
        for parameter in dados["parameters"]
    ]
    return itens


def recalcular_alternativas(*args, **kwargs):
    """Mantido para compatibilidade sem acoplar a API ao detalhe do fluxo."""
    return None
