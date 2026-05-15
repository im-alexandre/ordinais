from django.db import transaction

from core.models import Alternativa, Criterio, Decisor, Projeto


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
            Decisor.objects.create(
                projeto=projeto,
                is_criador=(indice == 0),
                ativo=True,
                status=Decisor.Status.PENDENTE,
                **decisor,
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
