import { afterEach, describe, expect, it, vi } from 'vitest';

import {
  baixarPlanilhaModelo,
  criarProjeto,
  confirmarUploadPlanilha,
  gerarResultado,
  listarDecisores,
  obterContextoAvaliacaoPorToken,
  listarProjetos,
  obterResultado,
  preverUploadPlanilha,
  recalcularResultado,
  salvarParticipantes,
} from './api';
import type {
  ConfirmarUploadPlanilhaPayload,
  ParticipantesPayload,
  PlanilhaPreviewResposta,
  RecalcularResultadoPayload,
  ResultadoProjeto,
} from '../types';

describe('cliente da API', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it('lista projetos a partir de /api/v1/projects/', async () => {
    const resposta = [{ id: 1, nome: 'Projeto A' }];
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(resposta), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );

    vi.stubGlobal('fetch', fetchMock);

    const projetos = await listarProjetos();

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/projects/',
      expect.objectContaining({
        method: 'GET',
      }),
    );
    expect(projetos).toEqual(resposta);
  });

  it('baixa a planilha modelo como blob', async () => {
    const arquivo = new Blob(['xlsx-binary'], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    });
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(arquivo, {
        status: 200,
        headers: {
          'Content-Type':
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        },
      }),
    );

    vi.stubGlobal('fetch', fetchMock);

    const blob = await baixarPlanilhaModelo(12);

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/projects/12/spreadsheet-template/',
      expect.objectContaining({
        method: 'GET',
      }),
    );
    expect(blob).toBeInstanceOf(Blob);
    expect(blob.size).toBeGreaterThan(0);
  });

  it('envia o upload para preview usando FormData', async () => {
    const resposta: PlanilhaPreviewResposta = {
      projeto: {
        id: 12,
        nome: 'Projeto Planilha',
        descricao: 'Descricao',
        qtde_classes: 3,
        qtde_criterios: 2,
        qtde_alternativas: 2,
        qtde_decisores: 1,
        lamb: 0.75,
      },
      arquivo: {
        nome: 'modelo.xlsx',
      },
      desempenhos: [
        {
          alternativa_id: 1,
          alternativa: 'Solar',
          valores: [
            { criterio_id: 10, criterio: 'Custo', valor: 100 },
            { criterio_id: 11, criterio: 'Prazo', valor: 12 },
          ],
        },
      ],
      parametros: [
        {
          criterio_id: 10,
          criterio: 'Custo',
          q: { valor: 2, origem: 'automatico' },
          p: { valor: 4, origem: 'planilha' },
          v: { valor: 9, origem: 'editado' },
        },
      ],
      erros: [],
      avisos: [
        { codigo: 'parametro_automatico', mensagem: 'q calculado automaticamente.' },
      ],
    };
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(resposta), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );

    vi.stubGlobal('fetch', fetchMock);

    const arquivo = new File(['xlsx-binary'], 'modelo.xlsx', {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    });

    const preview = await preverUploadPlanilha(12, arquivo);

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/projects/12/spreadsheet-upload/preview/',
      expect.objectContaining({
        method: 'POST',
        body: expect.any(FormData),
      }),
    );
    const [, options] = fetchMock.mock.calls[0];
    const body = options?.body as FormData;
    const enviado = body.get('arquivo');
    expect(enviado).toBeInstanceOf(File);
    expect((enviado as File).name).toBe('modelo.xlsx');
    expect((enviado as File).type).toBe(
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    );
    expect(preview).toEqual(resposta);
  });

  it('confirma o upload revisado com JSON serializado', async () => {
    const resposta = {
      project: {
        id: 12,
        nome: 'Projeto Planilha',
        descricao: 'Descricao',
        qtde_classes: 3,
        qtde_criterios: 2,
        qtde_alternativas: 2,
        qtde_decisores: 1,
        lamb: 0.75,
      },
      decisores: [],
      criterios: [],
      alternativas: [],
    };
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(resposta), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );

    vi.stubGlobal('fetch', fetchMock);

    const payload: ConfirmarUploadPlanilhaPayload = {
      desempenhos: [
        {
          alternativa_id: 1,
          alternativa: 'Solar',
          valores: [
            { criterio_id: 10, criterio: 'Custo', valor: 100 },
          ],
        },
      ],
      parametros: [
        {
          criterio_id: 10,
          criterio: 'Custo',
          q: { valor: 2, origem: 'automatico' },
          p: { valor: 4, origem: 'planilha' },
          v: { valor: 9, origem: 'editado' },
        },
      ],
    };

    const resultado = await confirmarUploadPlanilha(12, payload);

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/projects/12/spreadsheet-upload/confirm/',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
        }),
      }),
    );
    expect(resultado).toEqual(resposta);
  });

  it('recalcula o resultado oficial enviando lambda e qtde_classes', async () => {
    const resposta: ResultadoProjeto = {
      project: {
        id: 12,
        nome: 'Projeto Planilha',
        descricao: 'Descricao',
        qtde_classes: 4,
        qtde_criterios: 2,
        qtde_alternativas: 2,
        qtde_decisores: 1,
        lamb: 0.8,
      },
      pesos_criterios: [],
      pontuacao_alternativas: [],
      classificacao_range: [],
      classificacao_quantile: [],
      classificacao_final: {
        range: [],
        quantile: [],
      },
    };
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(resposta), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );

    vi.stubGlobal('fetch', fetchMock);

    const payload: RecalcularResultadoPayload = {
      lamb: 0.8,
      qtde_classes: 4,
    };

    const resultado = await recalcularResultado(12, payload);

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/projects/12/recalculate-result/',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
        }),
        body: JSON.stringify({
          lambda: 0.8,
          qtde_classes: 4,
        }),
      }),
    );
    expect(resultado).toEqual(resposta);
  });

  it('cria projeto com payload serializado em JSON', async () => {
    const resposta = { id: 9, nome: 'Novo projeto' };
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(resposta), {
        status: 201,
        headers: { 'Content-Type': 'application/json' },
      }),
    );

    vi.stubGlobal('fetch', fetchMock);

    const projeto = await criarProjeto({
      nome: 'Novo projeto',
      descricao: 'Descricao do projeto',
      qtde_classes: 2,
      qtde_criterios: 3,
      qtde_alternativas: 3,
      qtde_decisores: 1,
      lamb: 0.7,
    });

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/projects/',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
        }),
      }),
    );
    expect(projeto).toEqual(resposta);
  });

  it('salva participantes no projeto correto', async () => {
    const resposta = {
      project: { id: 4, nome: 'Projeto X' },
      decisores: [],
      criterios: [],
      alternativas: [],
    };
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(resposta), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );

    vi.stubGlobal('fetch', fetchMock);

    const payload: ParticipantesPayload = {
      decisores: [{ nome: 'Decisor 1' }],
      criterios: [{ nome: 'Criterio 1', numerico: true, monotonico: 1 }],
      alternativas: [{ nome: 'Alternativa 1' }],
    };

    const resultado = await salvarParticipantes(4, payload);

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/projects/4/participants/',
      expect.objectContaining({
        method: 'PUT',
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
        }),
      }),
    );
    expect(resultado).toEqual(resposta);
  });

  it('resolve o contexto de avaliacao por token', async () => {
    const resposta = {
      project: {
        id: 4,
        nome: 'Projeto X',
        descricao: 'Descricao',
        qtde_classes: 3,
        qtde_criterios: 2,
        qtde_alternativas: 2,
        qtde_decisores: 2,
        lamb: 0.65,
      },
      decisor: {
        id: 9,
        nome: 'Ana Souza',
        status: 'pendente',
        ativo: true,
        is_criador: false,
        token: 'token-seguro',
        evaluation_url:
          'http://localhost/?projectId=4&decisorToken=token-seguro&view=avaliacao',
      },
      criterios: [
        { id: 10, nome: 'Qualidade', numerico: false, monotonico: 1 },
      ],
      alternativas: [
        { id: 20, nome: 'Vacina A' },
      ],
    };
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(resposta), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );

    vi.stubGlobal('fetch', fetchMock);

    const contexto = await obterContextoAvaliacaoPorToken(4, 'token-seguro');

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/projects/4/evaluation-token/token-seguro/',
      expect.objectContaining({
        method: 'GET',
      }),
    );
    expect(contexto).toEqual(resposta);
  });

  it('lista decisores com links individuais de avaliacao', async () => {
    const resposta = [{
      id: 9,
      nome: 'Ana Souza',
      status: 'pendente',
      ativo: true,
      is_criador: false,
      token: 'token-seguro',
      evaluation_url:
        'http://localhost/?projectId=4&decisorToken=token-seguro&view=avaliacao',
    }];
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(resposta), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );

    vi.stubGlobal('fetch', fetchMock);

    const decisores = await listarDecisores(4);

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/projects/4/decision-makers/',
      expect.objectContaining({
        method: 'GET',
      }),
    );
    expect(decisores).toEqual(resposta);
  });

  it('gera resultado manualmente', async () => {
    const resposta: ResultadoProjeto = {
      project: {
        id: 4,
        nome: 'Projeto X',
        descricao: 'Descricao',
        qtde_classes: 3,
        qtde_criterios: 2,
        qtde_alternativas: 2,
        qtde_decisores: 2,
        lamb: 0.65,
      },
      pesos_criterios: [],
      pontuacao_alternativas: [],
      classificacao_range: [],
      classificacao_quantile: [],
      classificacao_final: {
        range: [],
        quantile: [],
      },
    };
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(resposta), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );

    vi.stubGlobal('fetch', fetchMock);

    const resultado = await gerarResultado(4);

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/projects/4/generate-result/',
      expect.objectContaining({
        method: 'POST',
      }),
    );
    expect(resultado).toEqual(resposta);
  });
});
