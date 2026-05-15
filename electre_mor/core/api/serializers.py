from urllib.parse import urlencode

from rest_framework import serializers

from core.models import Alternativa, Criterio, Decisor, Projeto


class ProjetoSerializer(serializers.ModelSerializer):
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
        if qtde_classes is not None and qtde_alternativas is not None and qtde_classes > qtde_alternativas:
            raise serializers.ValidationError(
                {"qtde_classes": "qtde_classes nao pode exceder qtde_alternativas."})
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
