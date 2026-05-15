from django.db import transaction
from django.utils import timezone

from core.models import Alternativa, Criterio, Decisor, Projeto


def criar_decisor_convidado(projeto, nome, *, is_criador=False):
    return Decisor.objects.create(
        projeto=projeto,
        nome=nome,
        is_criador=is_criador,
        ativo=True,
        status=Decisor.Status.PENDENTE,
    )


@transaction.atomic
def desativar_decisor(decisor):
    decisor.ativo = False
    decisor.status = Decisor.Status.DESATIVADO
    decisor.desativado_em = timezone.now()
    decisor.save(update_fields=["ativo", "status", "desativado_em"])
    return decisor


def listar_decisores(projeto):
    return projeto.decisores.all().order_by("id")


@transaction.atomic
def criar_projeto(dados):
    return Projeto.objects.create(**dados)


@transaction.atomic
def substituir_participantes(projeto, dados):
    projeto.decisores.all().delete()
    projeto.criterios.all().delete()
    projeto.alternativas.all().delete()

    decisores = []
    for indice, decisor in enumerate(dados["decisores"]):
        decisores.append(
            criar_decisor_convidado(
                projeto,
                decisor["nome"],
                is_criador=(indice == 0),
            ))
    criterios = [
        Criterio.objects.create(projeto=projeto, **criterio)
        for criterio in dados["criterios"]
    ]
    alternativas = [
        Alternativa.objects.create(projeto=projeto, **alternativa)
        for alternativa in dados["alternativas"]
    ]
    return {"decisores": decisores, "criterios": criterios, "alternativas": alternativas}
