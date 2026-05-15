import secrets

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from core.api.evaluation_serializers import (
    AlternativeComparisonItemSerializer,
    AlternativeComparisonsPayloadSerializer,
    ContextoAvaliacaoSerializer,
    CriteriaComparisonItemSerializer,
    CriteriaComparisonsPayloadSerializer,
    NumericScoreItemSerializer,
    NumericScoresPayloadSerializer, ParameterItemSerializer,
    ParametersPayloadSerializer)
from core.api.serializers import (AlternativaSerializer, CriterioSerializer,
                                  DecisorSerializer,
                                  ConfirmarUploadPlanilhaSerializer,
                                  ParticipantsPayloadSerializer,
                                  PlanilhaPreviewRespostaSerializer,
                                  PlanilhaUploadArquivoSerializer,
                                  ProjetoCompletoSerializer,
                                  ProjetoSerializer,
                                  RecalcularResultadoSerializer)
from core.models import Alternativa, Criterio, Decisor, Projeto
from core.services import (substituir_comparacoes_alternativas,
                           substituir_comparacoes_criterios,
                           substituir_notas_numericas, substituir_parametros,
                           substituir_participantes, criar_projeto)
from core.services.project_service import (criar_decisor_convidado,
                                           desativar_decisor,
                                           listar_decisores)
from core.services.spreadsheet_template_service import gerar_planilha_modelo
from core.services.spreadsheet_upload_service import prever_upload_planilha
from core.services.result_service import (
    ResultadoIndisponivel,
    gerar_resultado_manual,
    obter_resultado_gerado,
    obter_pendencias_resultado,
    recalcular_resultado_oficial,
    resultado_gerado,
)


class PodeRecalcularResultado(BasePermission):
    message = "Apenas o criador pode recalcular o resultado oficial."

    def has_permission(self, request, view):
        projeto = view.get_object()
        token_decisor = request.query_params.get("decisorToken") or request.headers.get(
            "X-Decisor-Token")
        if not token_decisor:
            return False

        decisor_criador = projeto.decisores.filter(is_criador=True).first()
        if decisor_criador is None:
            return False

        return secrets.compare_digest(token_decisor, decisor_criador.token)


def _resposta_resultado_bloqueado():
    return Response(
        {
            "detail": "Resultado ja gerado manualmente.",
            "pendencias": [],
        },
        status=status.HTTP_409_CONFLICT,
    )


def _decisor_confirmacao_planilha(projeto):
    return projeto.decisores.filter(is_criador=True).first() or projeto.decisores.order_by(
        "id").first()


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Projeto.objects.all().order_by("id")
    serializer_class = ProjetoSerializer

    def update(self, request, *args, **kwargs):
        projeto = self.get_object()
        if resultado_gerado(projeto):
            return _resposta_resultado_bloqueado()
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        projeto = self.get_object()
        if resultado_gerado(projeto):
            return _resposta_resultado_bloqueado()
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        projeto = self.get_object()
        if resultado_gerado(projeto):
            return _resposta_resultado_bloqueado()
        return super().destroy(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        projeto = criar_projeto(serializer.validated_data)
        output = ProjetoSerializer(projeto)
        headers = self.get_success_headers(output.data)
        return Response(output.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    @action(detail=True, methods=["get"], url_path="spreadsheet-template")
    def spreadsheet_template(self, request, pk=None):
        projeto = self.get_object()
        conteudo = gerar_planilha_modelo(projeto)
        resposta = HttpResponse(
            conteudo,
            content_type=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
        )
        resposta["Content-Disposition"] = (
            f'attachment; filename="{projeto.nome}.xlsx"'
        )
        return resposta

    @action(detail=True, methods=["post"], url_path="spreadsheet-upload/preview")
    def spreadsheet_upload_preview(self, request, pk=None):
        projeto = self.get_object()
        serializer = PlanilhaUploadArquivoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        arquivo = serializer.validated_data["arquivo"]
        preview = prever_upload_planilha(projeto, arquivo)
        resposta = {
            "projeto": ProjetoSerializer(projeto).data,
            "arquivo": {
                "nome": getattr(arquivo, "name", "planilha.xlsx"),
                "tamanho": getattr(arquivo, "size", None),
                "tipo": getattr(arquivo, "content_type", None),
            },
            "desempenhos": preview["desempenhos"],
            "parametros": preview["parametros"],
            "erros": preview["erros"],
            "avisos": preview["avisos"],
        }
        resposta_serializer = PlanilhaPreviewRespostaSerializer(resposta)
        return Response(resposta_serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="spreadsheet-upload/confirm")
    def spreadsheet_upload_confirm(self, request, pk=None):
        projeto = self.get_object()
        if resultado_gerado(projeto):
            return _resposta_resultado_bloqueado()

        serializer = ConfirmarUploadPlanilhaSerializer(
            data=request.data,
            context={"project": projeto},
        )
        serializer.is_valid(raise_exception=True)

        decisor = _decisor_confirmacao_planilha(projeto)
        criterios_por_id = {criterio.id: criterio for criterio in projeto.criterios.all()}
        alternativas_por_id = {
            alternativa.id: alternativa
            for alternativa in projeto.alternativas.all()
        }
        scores = []
        for desempenho in serializer.validated_data["desempenhos"]:
            for valor in desempenho["valores"]:
                scores.append({
                    "decisor": decisor,
                    "criterio": criterios_por_id[valor["criterio_id"]],
                    "alternativa": alternativas_por_id[desempenho["alternativa_id"]],
                    "nota": valor["valor"],
                })

        parametros = []
        for parametro in serializer.validated_data["parametros"]:
            parametros.append({
                "criterio": criterios_por_id[parametro["criterio_id"]],
                "p": parametro["p"]["valor"],
                "q": parametro["q"]["valor"],
                "v": parametro["v"]["valor"],
            })

        substituir_notas_numericas(projeto, {"scores": scores})
        substituir_parametros(projeto, {"parameters": parametros})

        resposta = ProjetoCompletoSerializer({
            "projeto": projeto,
            "decisores": projeto.decisores.all().order_by("id"),
            "criterios": projeto.criterios.all().order_by("id"),
            "alternativas": projeto.alternativas.all().order_by("id"),
        })
        return Response(resposta.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["put"])
    def participants(self, request, pk=None):
        projeto = self.get_object()
        if resultado_gerado(projeto):
            return _resposta_resultado_bloqueado()
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

        if resultado_gerado(projeto):
            return _resposta_resultado_bloqueado()
        nome = request.data.get("nome", "").strip()
        if not nome:
            return Response(
                {"nome": "Nome do decisor e obrigatorio."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        decisor = criar_decisor_convidado(projeto, nome)
        serializer = DecisorSerializer(decisor, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["get"],
        url_path=r"evaluation-token/(?P<token>[^/.]+)",
    )
    def evaluation_token(self, request, pk=None, token=None):
        projeto = self.get_object()
        decisor = get_object_or_404(projeto.decisores, token=token)
        if not decisor.ativo:
            return Response(
                {"detail": "Decisor desativado."},
                status=status.HTTP_410_GONE,
            )

        serializer = ContextoAvaliacaoSerializer(
            {
                "project": projeto,
                "decisor": decisor,
            },
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True,
            methods=["post"],
            url_path=r"decision-makers/(?P<decision_maker_id>[^/.]+)/disable")
    def decision_maker_disable(self, request, pk=None, decision_maker_id=None):
        projeto = self.get_object()
        if resultado_gerado(projeto):
            return _resposta_resultado_bloqueado()
        decisor = get_object_or_404(projeto.decisores, id=decision_maker_id)
        desativar_decisor(decisor)
        serializer = DecisorSerializer(decisor, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["put"], url_path="numeric-scores")
    def numeric_scores(self, request, pk=None):
        projeto = self.get_object()
        if resultado_gerado(projeto):
            return _resposta_resultado_bloqueado()
        serializer = NumericScoresPayloadSerializer(data=request.data,
                                                    context={"project": projeto})
        serializer.is_valid(raise_exception=True)
        try:
            itens = substituir_notas_numericas(projeto,
                                               serializer.validated_data)
        except ResultadoIndisponivel as exc:
            return Response({
                "detail": exc.motivo,
                "pendencias": exc.pendencias or [],
            }, status=status.HTTP_409_CONFLICT)
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
        if resultado_gerado(projeto):
            return _resposta_resultado_bloqueado()
        serializer = CriteriaComparisonsPayloadSerializer(
            data=request.data, context={"project": projeto})
        serializer.is_valid(raise_exception=True)
        try:
            itens = substituir_comparacoes_criterios(projeto,
                                                     serializer.validated_data)
        except ResultadoIndisponivel as exc:
            return Response({
                "detail": exc.motivo,
                "pendencias": exc.pendencias or [],
            }, status=status.HTTP_409_CONFLICT)
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
        if resultado_gerado(projeto):
            return _resposta_resultado_bloqueado()
        serializer = AlternativeComparisonsPayloadSerializer(
            data=request.data, context={"project": projeto})
        serializer.is_valid(raise_exception=True)
        try:
            itens = substituir_comparacoes_alternativas(
                projeto, serializer.validated_data)
        except ResultadoIndisponivel as exc:
            return Response({
                "detail": exc.motivo,
                "pendencias": exc.pendencias or [],
            }, status=status.HTTP_409_CONFLICT)
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
        if resultado_gerado(projeto):
            return _resposta_resultado_bloqueado()
        serializer = ParametersPayloadSerializer(data=request.data,
                                                 context={"project": projeto})
        serializer.is_valid(raise_exception=True)
        try:
            itens = substituir_parametros(projeto, serializer.validated_data)
        except ResultadoIndisponivel as exc:
            return Response({
                "detail": exc.motivo,
                "pendencias": exc.pendencias or [],
            }, status=status.HTTP_409_CONFLICT)
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
        if not resultado_gerado(projeto):
            return Response({
                "detail": "Resultado ainda nao gerado manualmente.",
                "pendencias": obter_pendencias_resultado(projeto),
            },
                            status=status.HTTP_409_CONFLICT)

        try:
            resultado = obter_resultado_gerado(projeto)
        except ResultadoIndisponivel as exc:
            return Response({
                "detail": exc.motivo,
                "pendencias": exc.pendencias or [],
            }, status=status.HTTP_409_CONFLICT)

        return Response(resultado, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="generate-result")
    def generate_result(self, request, pk=None):
        projeto = self.get_object()
        try:
            resultado = gerar_resultado_manual(projeto)
        except ResultadoIndisponivel as exc:
            return Response({
                "detail": exc.motivo,
                "pendencias": exc.pendencias or [],
            }, status=status.HTTP_409_CONFLICT)

        return Response(resultado, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        url_path="recalculate-result",
        permission_classes=[PodeRecalcularResultado],
    )
    def recalculate_result(self, request, pk=None):
        projeto = self.get_object()
        payload = request.data.copy()
        if "lamb" not in payload and "lambda" in payload:
            payload["lamb"] = payload["lambda"]
        if payload.get("lamb") == "":
            payload["lamb"] = None

        serializer = RecalcularResultadoSerializer(
            data=payload,
            context={"project": projeto},
        )
        serializer.is_valid(raise_exception=True)

        try:
            resultado = recalcular_resultado_oficial(
                projeto,
                lamb=serializer.validated_data["lamb"],
                qtde_classes=serializer.validated_data["qtde_classes"],
            )
        except ResultadoIndisponivel as exc:
            return Response({
                "detail": exc.motivo,
                "pendencias": exc.pendencias or [],
            }, status=status.HTTP_409_CONFLICT)

        return Response(resultado, status=status.HTTP_200_OK)
