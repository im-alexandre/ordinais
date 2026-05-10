from rest_framework import serializers

from core.api.serializers import ProjetoSerializer
from core.models import (Alternativa, AlternativaCriterio,
                         AvaliacaoAlternativas, AvaliacaoCriterios, Criterio,
                         CriterioParametro, Decisor)


class NumericScoreItemSerializer(serializers.Serializer):
    criterio_id = serializers.PrimaryKeyRelatedField(
        source="criterio",
        queryset=Criterio.objects.all(),
    )
    alternativa_id = serializers.PrimaryKeyRelatedField(
        source="alternativa",
        queryset=Alternativa.objects.all(),
    )
    nota = serializers.FloatField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        project = self.context.get("project")
        if project is not None:
            self.fields["criterio_id"].queryset = Criterio.objects.filter(
                projeto=project)
            self.fields["alternativa_id"].queryset = Alternativa.objects.filter(
                projeto=project)


class CriteriaComparisonItemSerializer(serializers.Serializer):
    decisor_id = serializers.PrimaryKeyRelatedField(
        source="decisor",
        queryset=Decisor.objects.all(),
    )
    criterio_a_id = serializers.PrimaryKeyRelatedField(
        source="criterioA",
        queryset=Criterio.objects.all(),
    )
    criterio_b_id = serializers.PrimaryKeyRelatedField(
        source="criterioB",
        queryset=Criterio.objects.all(),
    )
    nota = serializers.IntegerField(min_value=-2, max_value=2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        project = self.context.get("project")
        if project is not None:
            self.fields["decisor_id"].queryset = Decisor.objects.filter(
                projeto=project)
            self.fields["criterio_a_id"].queryset = Criterio.objects.filter(
                projeto=project)
            self.fields["criterio_b_id"].queryset = Criterio.objects.filter(
                projeto=project)


class AlternativeComparisonItemSerializer(serializers.Serializer):
    decisor_id = serializers.PrimaryKeyRelatedField(
        source="decisor",
        queryset=Decisor.objects.all(),
    )
    criterio_id = serializers.PrimaryKeyRelatedField(
        source="criterio",
        queryset=Criterio.objects.all(),
    )
    alternativa_a_id = serializers.PrimaryKeyRelatedField(
        source="alternativaA",
        queryset=Alternativa.objects.all(),
    )
    alternativa_b_id = serializers.PrimaryKeyRelatedField(
        source="alternativaB",
        queryset=Alternativa.objects.all(),
    )
    nota = serializers.IntegerField(min_value=-2, max_value=2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        project = self.context.get("project")
        if project is not None:
            self.fields["decisor_id"].queryset = Decisor.objects.filter(
                projeto=project)
            self.fields["criterio_id"].queryset = Criterio.objects.filter(
                projeto=project)
            self.fields["alternativa_a_id"].queryset = Alternativa.objects.filter(
                projeto=project)
            self.fields["alternativa_b_id"].queryset = Alternativa.objects.filter(
                projeto=project)


class ParameterItemSerializer(serializers.Serializer):
    criterio_id = serializers.PrimaryKeyRelatedField(
        source="criterio",
        queryset=Criterio.objects.all(),
    )
    p = serializers.FloatField()
    q = serializers.FloatField()
    v = serializers.FloatField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        project = self.context.get("project")
        if project is not None:
            self.fields["criterio_id"].queryset = Criterio.objects.filter(
                projeto=project)


class NumericScoresPayloadSerializer(serializers.Serializer):
    scores = NumericScoreItemSerializer(many=True)


class CriteriaComparisonsPayloadSerializer(serializers.Serializer):
    comparisons = CriteriaComparisonItemSerializer(many=True)


class AlternativeComparisonsPayloadSerializer(serializers.Serializer):
    comparisons = AlternativeComparisonItemSerializer(many=True)


class ParametersPayloadSerializer(serializers.Serializer):
    parameters = ParameterItemSerializer(many=True)


class ResultadoSerializer(serializers.Serializer):
    project = ProjetoSerializer(read_only=True)
    pesos_criterios = serializers.ListField(child=serializers.DictField())
    pontuacao_alternativas = serializers.ListField(
        child=serializers.DictField(), allow_null=True)
    classificacao_range = serializers.ListField(child=serializers.DictField())
    classificacao_quantile = serializers.ListField(child=serializers.DictField())
