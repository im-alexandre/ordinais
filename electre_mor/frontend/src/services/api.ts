import type {
  ComparacoesAlternativasPayload,
  ComparacoesCriteriosPayload,
  ContextoAvaliacao,
  ConfirmarUploadPlanilhaPayload,
  DecisorDetalhado,
  PlanilhaPreviewResposta,
  NotasNumericasPayload,
  ParametrosPayload,
  ParticipantesPayload,
  ParticipantesResposta,
  Projeto,
  ProjetoCompleto,
  ProjetoPayload,
  ResultadoProjeto,
  RecalcularResultadoPayload,
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

async function requisitarBlob(caminho: string): Promise<Blob> {
  const resposta = await fetch(`${BASE_URL}${caminho}`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
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
      detalhe || `Falha ao chamar GET ${BASE_URL}${caminho}`,
    );
  }

  return resposta.blob();
}

async function requisitarFormDataJson<T>(
  caminho: string,
  metodo: MetodoHttp,
  corpo: FormData,
): Promise<T> {
  const resposta = await fetch(`${BASE_URL}${caminho}`, {
    method: metodo,
    headers: {
      Accept: 'application/json',
    },
    body: corpo,
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

export function baixarPlanilhaModelo(projetoId: number): Promise<Blob> {
  return requisitarBlob(`/projects/${projetoId}/spreadsheet-template/`);
}

export function preverUploadPlanilha(
  projetoId: number,
  arquivo: Blob,
): Promise<PlanilhaPreviewResposta> {
  const formData = new FormData();
  const nomeArquivo = arquivo instanceof File ? arquivo.name : 'planilha.xlsx';
  formData.append('arquivo', arquivo, nomeArquivo);

  return requisitarFormDataJson<PlanilhaPreviewResposta>(
    `/projects/${projetoId}/spreadsheet-upload/preview/`,
    'POST',
    formData,
  );
}

export function confirmarUploadPlanilha(
  projetoId: number,
  payload: ConfirmarUploadPlanilhaPayload,
): Promise<ProjetoCompleto> {
  return requisitarJson<ProjetoCompleto>(
    `/projects/${projetoId}/spreadsheet-upload/confirm/`,
    'POST',
    payload,
  );
}

export function recalcularResultado(
  projetoId: number,
  payload: RecalcularResultadoPayload,
): Promise<ResultadoProjeto> {
  const lambda = payload.lambda ?? payload.lamb;
  const consulta = payload.decisorToken
    ? `?${new URLSearchParams({ decisorToken: payload.decisorToken }).toString()}`
    : '';

  return requisitarJson<ResultadoProjeto>(
    `/projects/${projetoId}/recalculate-result/${consulta}`,
    'POST',
    {
      lambda,
      qtde_classes: payload.qtde_classes,
    },
  );
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
