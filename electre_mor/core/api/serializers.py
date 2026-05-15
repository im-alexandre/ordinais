from urllib.parse import urlencode

from rest_framework import serializers

from core.models import Alternativa, Criterio, Decisor, Projeto


class ProjetoSerializer(serializers.ModelSerializer):
    lamb = serializers.FloatField(
        required=False,
        allow_null=True,
        default=0.75,
        min_value=0.5,
        max_value=1,
    )

    class Meta:
        model = Projeto
        fields = [
            "id",
            "nome",
            "descricao",
            "qtde_classes",
            "qtde_criterios",
            "qtde_alternativas",
            "qtde_decisores",
            "lamb",
            "data",
        ]
        read_only_fields = ["id", "data"]

    def validate(self, attrs):
        qtde_classes = attrs.get("qtde_classes", getattr(self.instance,
                                                         "qtde_classes", None))
        qtde_alternativas = attrs.get("qtde_alternativas",
                                      getattr(self.instance,
                                              "qtde_alternativas", None))
        if "lamb" in attrs and attrs["lamb"] is None:
            attrs["lamb"] = 0.75
        if qtde_classes is not None and qtde_alternativas is not None and qtde_classes > qtde_alternativas:
            raise serializers.ValidationError(
                {"qtde_classes": "qtde_classes nao pode exceder qtde_alternativas."})
        return attrs


class RecalcularResultadoSerializer(serializers.Serializer):
    lamb = serializers.FloatField(
        required=False,
        allow_null=True,
        default=0.75,
        min_value=0.5,
        max_value=1,
    )
    qtde_classes = serializers.IntegerField(min_value=2)

    def validate(self, attrs):
        projeto = self.context.get("project")
        if projeto is not None:
            if attrs["qtde_classes"] > projeto.qtde_alternativas:
                raise serializers.ValidationError({
                    "qtde_classes": "qtde_classes nao pode exceder qtde_alternativas."
                })
        if "lamb" in attrs and attrs["lamb"] is None:
            attrs["lamb"] = 0.75
        return attrs


class DecisorSerializer(serializers.ModelSerializer):
    evaluation_url = serializers.SerializerMethodField()

    class Meta:
        model = Decisor
        fields = [
            "id",
            "nome",
            "status",
            "ativo",
            "is_criador",
            "token",
            "evaluation_url",
        ]
        read_only_fields = fields

    def get_evaluation_url(self, obj):
        request = self.context.get("request")
        query = urlencode({
            "projectId": obj.projeto_id,
            "decisorToken": obj.token,
            "view": "avaliacao",
        })
        path = f"/?{query}"
        if request is not None:
            return request.build_absolute_uri(path)
        return path


class CriterioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Criterio
        fields = ["id", "nome", "numerico", "monotonico"]
        read_only_fields = ["id"]


class AlternativaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alternativa
        fields = ["id", "nome"]
        read_only_fields = ["id"]


class PlanilhaArquivoSerializer(serializers.Serializer):
    nome = serializers.CharField()
    tamanho = serializers.IntegerField(required=False, allow_null=True)
    tipo = serializers.CharField(required=False, allow_null=True)


class PlanilhaMensagemSerializer(serializers.Serializer):
    codigo = serializers.CharField()
    mensagem = serializers.CharField()
    campo = serializers.CharField(required=False)
    criterio_id = serializers.IntegerField(required=False)
    alternativa_id = serializers.IntegerField(required=False)


class PlanilhaDesempenhoValorSerializer(serializers.Serializer):
    criterio_id = serializers.IntegerField()
    criterio = serializers.CharField(required=False, allow_blank=True)
    valor = serializers.FloatField(allow_null=True)

    def validate_criterio_id(self, value):
        project = self.context.get("project")
        if project is not None and not Criterio.objects.filter(
            projeto=project,
            id=value,
        ).exists():
            raise serializers.ValidationError("Criterio fora do projeto.")
        return value


class PlanilhaDesempenhoSerializer(serializers.Serializer):
    alternativa_id = serializers.IntegerField()
    alternativa = serializers.CharField(required=False, allow_blank=True)
    valores = PlanilhaDesempenhoValorSerializer(many=True)

    def validate_alternativa_id(self, value):
        project = self.context.get("project")
        if project is not None and not Alternativa.objects.filter(
            projeto=project,
            id=value,
        ).exists():
            raise serializers.ValidationError("Alternativa fora do projeto.")
        return value


class PlanilhaValorComOrigemSerializer(serializers.Serializer):
    valor = serializers.FloatField()
    origem = serializers.ChoiceField(
        choices=("planilha", "automatico", "editado"),
    )


class PlanilhaParametroSerializer(serializers.Serializer):
    criterio_id = serializers.IntegerField()
    criterio = serializers.CharField(required=False, allow_blank=True)
    q = PlanilhaValorComOrigemSerializer()
    p = PlanilhaValorComOrigemSerializer()
    v = PlanilhaValorComOrigemSerializer()

    def validate_criterio_id(self, value):
        project = self.context.get("project")
        if project is not None and not Criterio.objects.filter(
            projeto=project,
            id=value,
        ).exists():
            raise serializers.ValidationError("Criterio fora do projeto.")
        return value


class PlanilhaUploadArquivoSerializer(serializers.Serializer):
    arquivo = serializers.FileField()


class PlanilhaPreviewRespostaSerializer(serializers.Serializer):
    projeto = ProjetoSerializer()
    arquivo = PlanilhaArquivoSerializer()
    desempenhos = PlanilhaDesempenhoSerializer(many=True)
    parametros = PlanilhaParametroSerializer(many=True)
    erros = PlanilhaMensagemSerializer(many=True)
    avisos = PlanilhaMensagemSerializer(many=True)


class ConfirmarUploadPlanilhaSerializer(serializers.Serializer):
    desempenhos = PlanilhaDesempenhoSerializer(many=True)
    parametros = PlanilhaParametroSerializer(many=True)


class ProjetoCompletoSerializer(serializers.Serializer):
    projeto = ProjetoSerializer()
    decisores = DecisorSerializer(many=True)
    criterios = CriterioSerializer(many=True)
    alternativas = AlternativaSerializer(many=True)


class NomeItemSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=20)


class CriterioInputSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=20)
    numerico = serializers.BooleanField()
    monotonico = serializers.ChoiceField(choices=(1, 2))


class ParticipantsPayloadSerializer(serializers.Serializer):
    decisores = NomeItemSerializer(many=True)
    criterios = CriterioInputSerializer(many=True)
    alternativas = NomeItemSerializer(many=True)

    def validate(self, attrs):
        project = self.context.get("project")
        if project is None:
            return attrs

        esperado = {
            "decisores": project.qtde_decisores,
            "criterios": project.qtde_criterios,
            "alternativas": project.qtde_alternativas,
        }
        for chave, quantidade in esperado.items():
            if len(attrs[chave]) != quantidade:
                raise serializers.ValidationError({
                    chave: f"Quantidade esperada para {chave} e {quantidade}."
                })
        return attrs
