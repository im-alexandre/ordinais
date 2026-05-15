from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.api.evaluation_serializers import (
    AlternativeComparisonItemSerializer,
    AlternativeComparisonsPayloadSerializer,
    CriteriaComparisonItemSerializer,
    CriteriaComparisonsPayloadSerializer,
    NumericScoreItemSerializer,
    NumericScoresPayloadSerializer, ParameterItemSerializer,
    ParametersPayloadSerializer, ResultadoSerializer)
from core.api.serializers import (AlternativaSerializer, CriterioSerializer,
                                  DecisorSerializer,
                                  ParticipantsPayloadSerializer,
                                  ProjetoSerializer)
from core.models import Alternativa, Criterio, Decisor, Projeto
from core.services import (obter_resultado, substituir_comparacoes_alternativas,
                           substituir_comparacoes_criterios,
                           substituir_notas_numericas, substituir_parametros,
                           substituir_participantes, criar_projeto)
from core.services.project_service import (criar_decisor_convidado,
                                           desativar_decisor,
                                           listar_decisores)
from core.services.result_service import ResultadoIndisponivel


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Projeto.objects.all().order_by("id")
    serializer_class = ProjetoSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        projeto = criar_projeto(serializer.validated_data)
        output = ProjetoSerializer(projeto)
        headers = self.get_success_headers(output.data)
        return Response(output.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    @action(detail=True, methods=["put"])
    def participants(self, request, pk=None):
        projeto = self.get_object()
        serializer = ParticipantsPayloadSerializer(data=request.data,
                                                   context={"project": projeto})
        serializer.is_valid(raise_exception=True)
        resultado = substituir_participantes(projeto, serializer.validated_data)
        return Response(
            {
                "project": ProjetoSerializer(projeto).data,
                "decisores": DecisorSerializer(resultado["decisores"],
                                               many=True).data,
                "criterios": CriterioSerializer(resultado["criterios"],
                                                many=True).data,
                "alternativas": AlternativaSerializer(resultado["alternativas"],
                                                      many=True).data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get", "post"], url_path="decision-makers")
    def decision_makers(self, request, pk=None):
        projeto = self.get_object()
        if request.method == "GET":
            decisores = listar_decisores(projeto)
            serializer = DecisorSerializer(
                decisores,
                many=True,
                context={"request": request},
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

        nome = request.data.get("nome", "").strip()
        if not nome:
            return Response(
                {"nome": "Nome do decisor e obrigatorio."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        decisor = criar_decisor_convidado(projeto, nome)
        serializer = DecisorSerializer(decisor, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True,
            methods=["post"],
            url_path=r"decision-makers/(?P<decision_maker_id>[^/.]+)/disable")
    def decision_maker_disable(self, request, pk=None, decision_maker_id=None):
        projeto = self.get_object()
        decisor = get_object_or_404(projeto.decisores, id=decision_maker_id)
        desativar_decisor(decisor)
        serializer = DecisorSerializer(decisor, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["put"], url_path="numeric-scores")
    def numeric_scores(self, request, pk=None):
        projeto = self.get_object()
        serializer = NumericScoresPayloadSerializer(data=request.data,
                                                    context={"project": projeto})
        serializer.is_valid(raise_exception=True)
        itens = substituir_notas_numericas(projeto, serializer.validated_data)
        return Response(
            {
                "project_id": projeto.id,
                "scores": NumericScoreItemSerializer(itens, many=True).data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["put"], url_path="criteria-comparisons")
    def criteria_comparisons(self, request, pk=None):
        projeto = self.get_object()
        serializer = CriteriaComparisonsPayloadSerializer(
            data=request.data, context={"project": projeto})
        serializer.is_valid(raise_exception=True)
        itens = substituir_comparacoes_criterios(projeto,
                                                 serializer.validated_data)
        return Response(
            {
                "project_id": projeto.id,
                "comparisons": CriteriaComparisonItemSerializer(itens,
                                                                many=True).data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["put"], url_path="alternative-comparisons")
    def alternative_comparisons(self, request, pk=None):
        projeto = self.get_object()
        serializer = AlternativeComparisonsPayloadSerializer(
            data=request.data, context={"project": projeto})
        serializer.is_valid(raise_exception=True)
        itens = substituir_comparacoes_alternativas(projeto,
                                                    serializer.validated_data)
        return Response(
            {
                "project_id": projeto.id,
                "comparisons": AlternativeComparisonItemSerializer(
                    itens,
                    many=True,
                ).data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["put"])
    def parameters(self, request, pk=None):
        projeto = self.get_object()
        serializer = ParametersPayloadSerializer(data=request.data,
                                                 context={"project": projeto})
        serializer.is_valid(raise_exception=True)
        itens = substituir_parametros(projeto, serializer.validated_data)
        return Response(
            {
                "project_id": projeto.id,
                "parameters": ParameterItemSerializer(itens, many=True).data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"])
    def result(self, request, pk=None):
        projeto = self.get_object()
        try:
            resultado = obter_resultado(projeto)
        except ResultadoIndisponivel as exc:
            return Response({"detail": exc.motivo},
                            status=status.HTTP_409_CONFLICT)

        serializer = ResultadoSerializer(resultado)
        return Response(serializer.data, status=status.HTTP_200_OK)
