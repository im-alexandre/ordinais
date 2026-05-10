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

export type ParticipanteNome = {
  nome: string;
};

export type CriterioEntrada = {
  nome: string;
  numerico: boolean;
  monotonico: 1 | 2;
};

export type ParticipantesPayload = {
  decisores: ParticipanteNome[];
  criterios: CriterioEntrada[];
  alternativas: ParticipanteNome[];
};

export type NotaNumerica = {
  criterio_id: number;
  alternativa_id: number;
  nota: number;
};

export type NotasNumericasPayload = {
  scores: NotaNumerica[];
};

export type ResultadoProjeto = {
  project: Projeto;
  pesos_criterios: Array<Record<string, string | number>>;
  pontuacao_alternativas: Array<Record<string, string | number>> | null;
  classificacao_range: Array<Record<string, string | number>>;
  classificacao_quantile: Array<Record<string, string | number>>;
};
