import type {
  ComparacoesAlternativasPayload,
  ComparacoesCriteriosPayload,
  ContextoAvaliacao,
  DecisorDetalhado,
  NotasNumericasPayload,
  ParametrosPayload,
  ParticipantesPayload,
  ParticipantesResposta,
  Projeto,
  ProjetoPayload,
  ResultadoProjeto,
} from '../types';

const BASE_URL = '/api/v1';

type MetodoHttp = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

export class ApiError extends Error {
  status: number;

  data: unknown;

  constructor(status: number, data: unknown, message?: string) {
    super(message ?? `Falha HTTP ${status}`);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

async function requisitarJson<T>(
  caminho: string,
  metodo: MetodoHttp = 'GET',
  corpo?: unknown,
): Promise<T> {
  const resposta = await fetch(`${BASE_URL}${caminho}`, {
    method: metodo,
    headers: {
      Accept: 'application/json',
      ...(corpo === undefined
        ? {}
        : { 'Content-Type': 'application/json' }),
    },
    body: corpo === undefined ? undefined : JSON.stringify(corpo),
  });

  if (!resposta.ok) {
    const detalhe = await resposta.text().catch(() => '');
    let dados: unknown = detalhe;
    if (detalhe) {
      try {
        dados = JSON.parse(detalhe);
      } catch {
        dados = detalhe;
      }
    }
    throw new ApiError(
      resposta.status,
      dados,
      detalhe || `Falha ao chamar ${metodo} ${BASE_URL}${caminho}`,
    );
  }

  if (resposta.status === 204) {
    return undefined as T;
  }

  return (await resposta.json()) as T;
}

export function listarProjetos() {
  return requisitarJson<Projeto[]>('/projects/');
}

export function listarDecisores(projetoId: number) {
  return requisitarJson<DecisorDetalhado[]>(
    `/projects/${projetoId}/decision-makers/`,
  );
}


export function criarProjeto(payload: ProjetoPayload) {
  return requisitarJson<Projeto>('/projects/', 'POST', payload);
}

export function salvarParticipantes(
  projetoId: number,
  payload: ParticipantesPayload,
) {
  return requisitarJson<ParticipantesResposta>(
    `/projects/${projetoId}/participants/`,
    'PUT',
    payload,
  );
}

export function salvarNotasNumericas(
  projetoId: number,
  payload: NotasNumericasPayload,
) {
  return requisitarJson(`/projects/${projetoId}/numeric-scores/`, 'PUT', payload);
}

export function salvarComparacoesCriterios(
  projetoId: number,
  payload: ComparacoesCriteriosPayload,
) {
  return requisitarJson(
    `/projects/${projetoId}/criteria-comparisons/`,
    'PUT',
    payload,
  );
}

export function salvarComparacoesAlternativas(
  projetoId: number,
  payload: ComparacoesAlternativasPayload,
) {
  return requisitarJson(
    `/projects/${projetoId}/alternative-comparisons/`,
    'PUT',
    payload,
  );
}

export function salvarParametros(projetoId: number, payload: ParametrosPayload) {
  return requisitarJson(`/projects/${projetoId}/parameters/`, 'PUT', payload);
}

export function obterResultado(projetoId: number) {
  return requisitarJson<ResultadoProjeto>(`/projects/${projetoId}/result/`);
}

export function obterContextoAvaliacaoPorToken(
  projetoId: number,
  token: string,
) {
  return requisitarJson<ContextoAvaliacao>(
    `/projects/${projetoId}/evaluation-token/${token}/`,
  );
}

export function gerarResultado(projetoId: number) {
  return requisitarJson<ResultadoProjeto>(
    `/projects/${projetoId}/generate-result/`,
    'POST',
  );
}
