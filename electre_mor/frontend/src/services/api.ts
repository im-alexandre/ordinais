import type {
  NotasNumericasPayload,
  ParticipantesPayload,
  Projeto,
  ProjetoPayload,
  ResultadoProjeto,
} from '../types';

const BASE_URL = '/api/v1';

type MetodoHttp = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

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
    throw new Error(
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

export function criarProjeto(payload: ProjetoPayload) {
  return requisitarJson<Projeto>('/projects/', 'POST', payload);
}

export function salvarParticipantes(
  projetoId: number,
  payload: ParticipantesPayload,
) {
  return requisitarJson(`/projects/${projetoId}/participants/`, 'PUT', payload);
}

export function salvarNotasNumericas(
  projetoId: number,
  payload: NotasNumericasPayload,
) {
  return requisitarJson(`/projects/${projetoId}/numeric-scores/`, 'PUT', payload);
}

export function obterResultado(projetoId: number) {
  return requisitarJson<ResultadoProjeto>(`/projects/${projetoId}/result/`);
}
