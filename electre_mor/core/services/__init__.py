"""Servicos de API do Electre MOR."""

from core.services.evaluation_service import (recalcular_alternativas,
                                              substituir_comparacoes_alternativas,
                                              substituir_comparacoes_criterios,
                                              substituir_notas_numericas,
                                              substituir_parametros)
from core.services.project_service import (substituir_participantes,
                                           criar_projeto)
from core.services.result_service import obter_resultado

