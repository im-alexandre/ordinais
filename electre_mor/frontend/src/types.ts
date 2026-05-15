export type Projeto = {
  id: number;
  nome: string;
  descricao: string;
  qtde_classes: number;
  qtde_criterios: number;
  qtde_alternativas: number;
  qtde_decisores: number;
  lamb: number;
};

export type ProjetoPayload = Omit<Projeto, 'id'>;

export type EntidadeNome = {
  id: number;
  nome: string;
};

export type DecisorStatus =
  | 'pendente'
  | 'em_edicao'
  | 'concluido'
  | 'desativado';

export type DecisorDetalhado = EntidadeNome & {
  status: DecisorStatus;
  ativo: boolean;
  is_criador: boolean;
  token: string;
  evaluation_url: string;
};

export type ParticipanteNome = Omit<EntidadeNome, 'id'>;

export type CriterioEntrada = {
  nome: string;
  numerico: boolean;
  monotonico: 1 | 2;
};

export type Criterio = CriterioEntrada & {
  id: number;
};

export type ParticipantesPayload = {
  decisores: ParticipanteNome[];
  criterios: CriterioEntrada[];
  alternativas: ParticipanteNome[];
};

export type ParticipantesResposta = {
  project: Projeto;
  decisores: DecisorDetalhado[];
  criterios: Criterio[];
  alternativas: EntidadeNome[];
};

export type NotaNumerica = {
  decisor_id: number;
  criterio_id: number;
  alternativa_id: number;
  nota: number;
};

export type NotasNumericasPayload = {
  scores: NotaNumerica[];
};

export type ComparacaoCriterio = {
  decisor_id: number;
  criterio_a_id: number;
  criterio_b_id: number;
  nota: number;
};

export type ComparacoesCriteriosPayload = {
  comparisons: ComparacaoCriterio[];
};

export type ComparacaoAlternativa = {
  decisor_id: number;
  criterio_id: number;
  alternativa_a_id: number;
  alternativa_b_id: number;
  nota: number;
};

export type ComparacoesAlternativasPayload = {
  comparisons: ComparacaoAlternativa[];
};

export type ParametroCriterio = {
  criterio_id: number;
  p: number;
  q: number;
  v: number;
};

export type ParametrosPayload = {
  parameters: ParametroCriterio[];
};

export type OrigemValorPlanilha = 'planilha' | 'automatico' | 'editado';

export type PlanilhaMensagem = {
  codigo: string;
  mensagem: string;
  campo?: string;
  criterio_id?: number;
  alternativa_id?: number;
};

export type PlanilhaValorParametro = {
  valor: number | null;
  origem: OrigemValorPlanilha;
};

export type PlanilhaDesempenhoValor = {
  criterio_id: number;
  criterio: string;
  valor: number | null;
};

export type PlanilhaDesempenhoRevisao = {
  alternativa_id: number;
  alternativa: string;
  valores: PlanilhaDesempenhoValor[];
};

export type PlanilhaParametroRevisao = {
  criterio_id: number;
  criterio: string;
  q: PlanilhaValorParametro;
  p: PlanilhaValorParametro;
  v: PlanilhaValorParametro;
};

export type PlanilhaArquivo = {
  nome: string;
  tamanho?: number;
  tipo?: string;
};

export type PlanilhaPreviewResposta = {
  projeto: Projeto;
  arquivo: PlanilhaArquivo;
  desempenhos: PlanilhaDesempenhoRevisao[];
  parametros: PlanilhaParametroRevisao[];
  erros: PlanilhaMensagem[];
  avisos: PlanilhaMensagem[];
};

export type ConfirmarUploadPlanilhaPayload = {
  desempenhos: PlanilhaDesempenhoRevisao[];
  parametros: PlanilhaParametroRevisao[];
};

export type RecalcularResultadoPayload = {
  lambda?: number;
  lamb?: number;
  qtde_classes: number;
  decisorToken?: string;
};

export type ProjetoCompleto = {
  projeto: Projeto;
  decisores: DecisorDetalhado[];
  criterios: Criterio[];
  alternativas: EntidadeNome[];
};

export type ContextoAvaliacao = {
  project: Projeto;
  decisor: DecisorDetalhado;
  criterios: Criterio[];
  alternativas: EntidadeNome[];
};

export type PendenciaDecisor = {
  id: number;
  nome: string;
  status: DecisorStatus | string;
  ativo: boolean;
  faltas: string[];
};

export type ResultadoPendente = {
  detail: string;
  pendencias: PendenciaDecisor[];
};

export type ClassificacaoFinalItem = {
  alternative_id: number;
  alternative: string;
  pessimista: string;
  otimista: string;
  class: string;
};

export type ResultadoProjeto = {
  project: Projeto;
  pesos_criterios: Array<Record<string, string | number>>;
  pontuacao_alternativas: Array<Record<string, string | number>> | null;
  classificacao_range: Array<Record<string, string | number>>;
  classificacao_quantile: Array<Record<string, string | number>>;
  classificacao_final: {
    range: ClassificacaoFinalItem[];
    quantile: ClassificacaoFinalItem[];
  };
};

export type ResultadoConsulta = ResultadoProjeto | ResultadoPendente;
